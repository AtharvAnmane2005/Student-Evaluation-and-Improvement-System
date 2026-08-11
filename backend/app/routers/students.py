from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import get_database
from app.core.deps import CurrentUser, require_role
from app.models.user import StudentInDB, StudentProfileResponse, StudentProfileUpdateRequest
from app.services.student_profile_service import StudentProfileError, StudentProfileService

router = APIRouter()


def _to_response(student: StudentInDB, email: str) -> StudentProfileResponse:
    return StudentProfileResponse(
        id=student.id,
        email=email,
        name=student.name,
        department=student.department,
        batch_year=student.batch_year,
        cgpa=student.cgpa,
        phone=student.phone,
        linkedin_url=student.linkedin_url,
        github_url=student.github_url,
        portfolio_url=student.portfolio_url,
        skills=student.skills,
        achievements=student.achievements,
        certificates=student.certificates,
        active_resume_id=student.active_resume_id,
        profile_completeness_pct=student.profile_completeness_pct,
    )


@router.get("/me", response_model=StudentProfileResponse)
async def get_my_profile(
    current_user: CurrentUser = Depends(require_role("student")),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    service = StudentProfileService(db)
    try:
        student = await service.get_profile(current_user.id)
    except StudentProfileError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    return _to_response(student, current_user.email)


@router.put("/me", response_model=StudentProfileResponse)
async def update_my_profile(
    payload: StudentProfileUpdateRequest,
    current_user: CurrentUser = Depends(require_role("student")),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    service = StudentProfileService(db)
    try:
        student = await service.update_profile(current_user.id, payload)
    except StudentProfileError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    return _to_response(student, current_user.email)
