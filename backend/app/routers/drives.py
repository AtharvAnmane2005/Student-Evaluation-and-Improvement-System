from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import get_database
from app.core.deps import CurrentUser, get_current_user, require_role
from app.models.drive import (
    ApplicationDetail,
    ApplicationResponse,
    ApplicationStatusUpdateRequest,
    CompanySummary,
    DriveCreateRequest,
    DriveDetail,
    DriveSummary,
    DriveUpdateRequest,
    PlacementDriveInDB,
)
from app.repositories.application_repository import ApplicationRepository
from app.repositories.company_repository import CompanyRepository
from app.repositories.drive_repository import PlacementDriveRepository
from app.repositories.profile_repositories import StudentRepository, TPORepository
from app.repositories.resume_repository import ResumeRepository
from app.services.drive_service import DriveError, DriveService

router = APIRouter()


async def _to_summary(drive: PlacementDriveInDB, db: AsyncIOMotorDatabase) -> DriveSummary:
    company = await CompanyRepository(db).get_by_id(drive.company_id)
    company_summary = (
        CompanySummary(
            id=company.id,
            name=company.name,
            description=company.description,
            website=company.website,
            industry=company.industry,
        )
        if company
        else CompanySummary(id=drive.company_id, name="Unknown company")
    )
    return DriveSummary(
        id=drive.id,
        company=company_summary,
        job_title=drive.job_title,
        package=drive.package,
        location=drive.location,
        deadline=drive.deadline,
        status=drive.status,
        required_skills=drive.required_skills,
    )


async def _to_detail(drive: PlacementDriveInDB, db: AsyncIOMotorDatabase) -> DriveDetail:
    summary = await _to_summary(drive, db)
    return DriveDetail(
        **summary.model_dump(),
        description=drive.description,
        jd_text=drive.jd_text,
        eligibility=drive.eligibility,
        selection_process=drive.selection_process,
        experience_required_years=drive.experience_required_years,
        created_at=drive.created_at,
    )


def _to_application_response(application) -> ApplicationResponse:
    return ApplicationResponse(
        id=application.id,
        drive_id=application.drive_id,
        student_id=application.student_id,
        resume_id=application.resume_id,
        status=application.status,
        applied_at=application.applied_at,
    )


@router.post("", response_model=DriveDetail, status_code=201)
async def create_drive(
    payload: DriveCreateRequest,
    current_user: CurrentUser = Depends(require_role("tpo")),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    service = DriveService(db)
    try:
        drive = await service.create_drive(current_user.id, payload)
    except DriveError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    return await _to_detail(drive, db)


@router.get("", response_model=list[DriveSummary])
async def list_drives(
    page: int = 1,
    limit: int = 20,
    status_filter: str | None = None,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    query: dict = {}
    if status_filter:
        query["status"] = status_filter
    drives = await PlacementDriveRepository(db).find_many(
        query, page=page, limit=limit, sort=[("created_at", -1)]
    )
    return [await _to_summary(d, db) for d in drives]


@router.get("/applications/me", response_model=list[ApplicationResponse])
async def my_applications(
    current_user: CurrentUser = Depends(require_role("student")),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    student = await StudentRepository(db).get_by_user_id(current_user.id)
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found.")
    applications = await ApplicationRepository(db).get_for_student(student.id)
    return [_to_application_response(a) for a in applications]


@router.get("/mine", response_model=list[DriveSummary])
async def list_my_drives(
    page: int = 1,
    limit: int = 50,
    current_user: CurrentUser = Depends(require_role("tpo")),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    service = DriveService(db)
    try:
        drives = await service.get_my_drives(current_user.id, page=page, limit=limit)
    except DriveError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    return [await _to_summary(d, db) for d in drives]


@router.get("/{drive_id}", response_model=DriveDetail)
async def get_drive(
    drive_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    drive = await PlacementDriveRepository(db).get_by_id(drive_id)
    if not drive:
        raise HTTPException(status_code=404, detail="Drive not found.")
    return await _to_detail(drive, db)


@router.put("/{drive_id}", response_model=DriveDetail)
async def update_drive(
    drive_id: str,
    payload: DriveUpdateRequest,
    current_user: CurrentUser = Depends(require_role("tpo")),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    service = DriveService(db)
    try:
        drive = await service.update_drive(current_user.id, drive_id, payload)
    except DriveError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    return await _to_detail(drive, db)


@router.delete("/{drive_id}", status_code=204)
async def delete_drive(
    drive_id: str,
    current_user: CurrentUser = Depends(require_role("tpo")),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    service = DriveService(db)
    try:
        await service.delete_drive(current_user.id, drive_id)
    except DriveError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


@router.post("/{drive_id}/apply", response_model=ApplicationResponse, status_code=201)
async def apply_to_drive(
    drive_id: str,
    current_user: CurrentUser = Depends(require_role("student")),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    service = DriveService(db)
    try:
        application = await service.apply_to_drive(current_user.id, drive_id)
    except DriveError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    return _to_application_response(application)


async def _to_application_detail(application, db: AsyncIOMotorDatabase) -> ApplicationDetail:
    base = _to_application_response(application)
    student = await StudentRepository(db).get_by_id(application.student_id)
    resume = await ResumeRepository(db).get_by_id(application.resume_id)
    return ApplicationDetail(
        **base.model_dump(),
        student_name=student.name if student else "Unknown student",
        student_department=student.department if student else None,
        student_cgpa=student.cgpa if student else None,
        resume_filename=resume.original_filename if resume else None,
    )


@router.get("/{drive_id}/applications", response_model=list[ApplicationDetail])
async def get_drive_applications(
    drive_id: str,
    current_user: CurrentUser = Depends(require_role("tpo")),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    drive = await PlacementDriveRepository(db).get_by_id(drive_id)
    if not drive:
        raise HTTPException(status_code=404, detail="Drive not found.")

    tpo = await TPORepository(db).get_by_user_id(current_user.id)
    if not tpo or drive.created_by != tpo.id:
        raise HTTPException(status_code=403, detail="You do not have permission to view these applications.")

    applications = await ApplicationRepository(db).get_for_drive(drive_id)
    return [await _to_application_detail(a, db) for a in applications]


@router.patch("/{drive_id}/applications/{application_id}", response_model=ApplicationDetail)
async def update_application_status(
    drive_id: str,
    application_id: str,
    payload: ApplicationStatusUpdateRequest,
    current_user: CurrentUser = Depends(require_role("tpo")),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    service = DriveService(db)
    try:
        application = await service.update_application_status(
            current_user.id, drive_id, application_id, payload.status.value
        )
    except DriveError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    return await _to_application_detail(application, db)
