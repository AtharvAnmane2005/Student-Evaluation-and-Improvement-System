import io

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import RedirectResponse, StreamingResponse
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import get_database
from app.core.deps import CurrentUser, get_current_user, require_role
from app.models.resume import ResumeDetail, ResumeInDB, ResumeSummary, ResumeUploadResponse
from app.repositories.profile_repositories import StudentRepository
from app.repositories.resume_repository import ResumeRepository
from app.services.resume_parsing_service import ResumeParsingService
from app.services.resume_service import ResumeError, ResumeService
from app.services.storage_service import StorageService

router = APIRouter()


async def _get_resume_with_access_check(
    resume_id: str, current_user: CurrentUser, db: AsyncIOMotorDatabase
) -> ResumeInDB:
    resume = await ResumeRepository(db).get_by_id(resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")

    if current_user.role == "student":
        student = await StudentRepository(db).get_by_user_id(current_user.id)
        if not student or resume.student_id != student.id:
            raise HTTPException(status_code=403, detail="You do not have access to this resume.")
    # TPO/Admin can view any resume — needed for candidate review (Phase 8+).

    return resume


def _to_summary(resume: ResumeInDB) -> ResumeSummary:
    return ResumeSummary(
        id=resume.id,
        version=resume.version,
        original_filename=resume.original_filename,
        uploaded_at=resume.uploaded_at,
        is_active=resume.is_active,
    )


def _to_detail(resume: ResumeInDB) -> ResumeDetail:
    return ResumeDetail(
        id=resume.id,
        version=resume.version,
        original_filename=resume.original_filename,
        uploaded_at=resume.uploaded_at,
        is_active=resume.is_active,
        parsed=resume.parsed,
        skill_set=resume.skill_set,
        experience_years=resume.experience_years,
    )


@router.post("", response_model=ResumeUploadResponse, status_code=201)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: CurrentUser = Depends(require_role("student")),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    file_bytes = await file.read()
    service = ResumeService(db)
    try:
        resume = await service.upload_resume(current_user.id, file.filename or "resume.pdf", file_bytes)
    except ResumeError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

    return ResumeUploadResponse(
        id=resume.id,
        version=resume.version,
        original_filename=resume.original_filename,
        file_size_bytes=resume.file_size_bytes,
        uploaded_at=resume.uploaded_at,
        is_active=resume.is_active,
    )


@router.get("/history", response_model=list[ResumeSummary])
async def resume_history(
    current_user: CurrentUser = Depends(require_role("student")),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    student = await StudentRepository(db).get_by_user_id(current_user.id)
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found.")

    history = await ResumeRepository(db).get_history_for_student(student.id)
    return [_to_summary(r) for r in history]


@router.get("/{resume_id}", response_model=ResumeDetail)
async def get_resume(
    resume_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    resume = await _get_resume_with_access_check(resume_id, current_user, db)
    return _to_detail(resume)


@router.post("/{resume_id}/reparse", response_model=ResumeDetail)
async def reparse_resume(
    resume_id: str,
    current_user: CurrentUser = Depends(require_role("student")),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """
    Manually re-triggers parsing on an already-uploaded resume — useful if
    the first pass failed (e.g. a transient storage read error) or after
    a parsing-logic improvement ships and existing resumes should benefit
    without needing to re-upload. Restricted to the resume's own student;
    a bulk "reparse everything" admin tool is a reasonable future addition
    but isn't needed yet at this scale.
    """
    resume = await _get_resume_with_access_check(resume_id, current_user, db)

    parsing_service = ResumeParsingService(db)
    success = await parsing_service.parse_and_store(resume.id)
    if not success:
        raise HTTPException(status_code=422, detail="Resume could not be parsed. The file may be unreadable.")

    refreshed = await ResumeRepository(db).get_by_id(resume.id)
    return _to_detail(refreshed)


@router.get("/{resume_id}/download")
async def download_resume(
    resume_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    resume = await _get_resume_with_access_check(resume_id, current_user, db)
    storage = StorageService()

    if resume.file_url.startswith("local://"):
        try:
            file_bytes = storage.read_local_file(resume.file_url)
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail="Resume file is missing from storage.") from exc
        return StreamingResponse(
            io.BytesIO(file_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f'inline; filename="{resume.original_filename}"'},
        )

    # Cloudinary (or any future absolute-URL backend) — just redirect.
    return RedirectResponse(resume.file_url)
