import logging

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.ml.parsing.parser import parse_resume
from app.repositories.resume_repository import ResumeRepository
from app.services.storage_service import StorageService

logger = logging.getLogger(__name__)


class ResumeParsingService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.resumes = ResumeRepository(db)
        self.storage = StorageService()

    async def parse_and_store(self, resume_id: str) -> bool:
        """
        Returns True on success, False on failure — never raises. A
        parsing failure is logged but must not take down whatever
        triggered it (typically the upload endpoint, right after the file
        was already successfully saved).
        """
        resume = await self.resumes.get_by_id(resume_id)
        if not resume:
            logger.error("parse_and_store called for missing resume_id=%s", resume_id)
            return False

        try:
            file_bytes = self._read_file(resume.file_url)
            parsed, text, skills, experience_years = parse_resume(file_bytes)
        except Exception:
            logger.exception("Resume parsing failed for resume_id=%s", resume_id)
            return False

        await self.resumes.update_by_id(
            resume_id,
            {
                "parsed": parsed.model_dump(),
                "resume_text": text,
                "skill_set": skills,
                "experience_years": experience_years,
                # Phase 9: the cached bi-encoder embedding was computed from
                # the old skill_set/experience_years — invalidate it so the
                # next match request recomputes against the fresh data.
                "resume_embedding": None,
            },
        )
        return True

    def _read_file(self, file_url: str) -> bytes:
        if file_url.startswith("local://"):
            return self.storage.read_local_file(file_url)

        # Cloudinary (or any future absolute-URL backend) — fetch over HTTP.
        import requests

        response = requests.get(file_url, timeout=15)
        response.raise_for_status()
        return response.content
