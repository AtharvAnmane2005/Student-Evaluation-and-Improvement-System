"""
Storage abstraction so ResumeService never needs to know whether a file
lands on local disk (dev) or Cloudinary (prod free tier) — selected via
STORAGE_BACKEND in settings, per the Phase 1 deployment design.
"""
from pathlib import Path

from app.core.config import get_settings

settings = get_settings()

_cloudinary_configured = False


def _ensure_cloudinary_configured() -> None:
    global _cloudinary_configured
    if _cloudinary_configured:
        return
    import cloudinary

    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True,
    )
    _cloudinary_configured = True


class StorageService:
    async def save_pdf(self, file_bytes: bytes, student_id: str, storage_key: str) -> str:
        """Returns a URL/reference the file can later be retrieved from."""
        if settings.STORAGE_BACKEND == "cloudinary":
            return self._save_to_cloudinary(file_bytes, student_id, storage_key)
        return self._save_to_local(file_bytes, student_id, storage_key)

    def _save_to_local(self, file_bytes: bytes, student_id: str, storage_key: str) -> str:
        directory = Path(settings.LOCAL_STORAGE_PATH) / "resumes" / student_id
        directory.mkdir(parents=True, exist_ok=True)
        file_path = directory / f"{storage_key}.pdf"
        file_path.write_bytes(file_bytes)
        # Stored as a relative "local://" key, not an absolute filesystem
        # path — the download route resolves it against LOCAL_STORAGE_PATH,
        # so moving the storage root later doesn't break existing records.
        return f"local://resumes/{student_id}/{storage_key}.pdf"

    def _save_to_cloudinary(self, file_bytes: bytes, student_id: str, storage_key: str) -> str:
        _ensure_cloudinary_configured()
        import cloudinary.uploader

        result = cloudinary.uploader.upload(
            file_bytes,
            resource_type="raw",  # PDFs are non-image assets on Cloudinary
            public_id=f"placer/resumes/{student_id}/{storage_key}",
            overwrite=True,
        )
        return result["secure_url"]

    def read_local_file(self, file_url: str) -> bytes:
        """Only valid for local:// URLs — resolves and reads the file back."""
        if not file_url.startswith("local://"):
            raise ValueError("read_local_file called on a non-local URL.")
        relative_path = file_url.removeprefix("local://")
        full_path = Path(settings.LOCAL_STORAGE_PATH) / relative_path
        if not full_path.is_file():
            raise FileNotFoundError(f"Resume file not found at {full_path}")
        return full_path.read_bytes()
