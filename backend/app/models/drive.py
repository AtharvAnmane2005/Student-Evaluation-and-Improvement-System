from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

from app.models.base import MongoBaseModel, PyObjectId


class DriveStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"


class ApplicationStatus(str, Enum):
    APPLIED = "applied"
    SHORTLISTED = "shortlisted"
    REJECTED = "rejected"
    SELECTED = "selected"


class EligibilityCriteria(BaseModel):
    min_cgpa: float | None = None
    departments: list[str] = Field(default_factory=list)  # empty = open to all departments
    batch_years: list[int] = Field(default_factory=list)  # empty = open to all batch years


# ---------------------------------------------------------------------------
# DB documents
# ---------------------------------------------------------------------------
class CompanyInDB(MongoBaseModel):
    name: str
    description: str | None = None
    website: str | None = None
    industry: str | None = None


class PlacementDriveInDB(MongoBaseModel):
    company_id: PyObjectId
    job_title: str
    description: str
    jd_text: str
    jd_embedding: list[float] | None = None  # populated by Phase 9 (semantic matching)
    required_skills: list[str] = Field(default_factory=list)
    experience_required_years: float = 0.0  # Phase 9: needed for the hybrid formula's experience_score term
    package: str | None = None
    location: str | None = None
    eligibility: EligibilityCriteria = Field(default_factory=EligibilityCriteria)
    deadline: datetime
    selection_process: list[str] = Field(default_factory=list)
    status: DriveStatus = DriveStatus.OPEN
    created_by: PyObjectId  # TPO document _id (not the User _id)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ApplicationInDB(MongoBaseModel):
    drive_id: PyObjectId
    student_id: PyObjectId
    resume_id: PyObjectId
    status: ApplicationStatus = ApplicationStatus.APPLIED
    final_score: float | None = None  # populated by Phase 9
    semantic_score: float | None = None
    skills_score: float | None = None
    experience_score: float | None = None
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    applied_at: datetime = Field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------
class DriveCreateRequest(BaseModel):
    company_name: str
    company_description: str | None = None
    company_website: str | None = None
    company_industry: str | None = None
    job_title: str
    description: str
    jd_text: str
    required_skills: list[str] = Field(default_factory=list)
    experience_required_years: float = Field(default=0.0, ge=0)
    package: str | None = None
    location: str | None = None
    eligibility: EligibilityCriteria = Field(default_factory=EligibilityCriteria)
    deadline: datetime
    selection_process: list[str] = Field(default_factory=list)


class DriveUpdateRequest(BaseModel):
    job_title: str | None = None
    description: str | None = None
    jd_text: str | None = None
    required_skills: list[str] | None = None
    experience_required_years: float | None = Field(default=None, ge=0)
    package: str | None = None
    location: str | None = None
    eligibility: EligibilityCriteria | None = None
    deadline: datetime | None = None
    selection_process: list[str] | None = None
    status: DriveStatus | None = None


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------
class CompanySummary(BaseModel):
    id: str
    name: str
    description: str | None = None
    website: str | None = None
    industry: str | None = None


class DriveSummary(BaseModel):
    id: str
    company: CompanySummary
    job_title: str
    package: str | None
    location: str | None
    deadline: datetime
    status: DriveStatus
    required_skills: list[str]


class DriveDetail(DriveSummary):
    description: str
    jd_text: str
    eligibility: EligibilityCriteria
    selection_process: list[str]
    experience_required_years: float
    created_at: datetime


class ApplicationResponse(BaseModel):
    id: str
    drive_id: str
    student_id: str
    resume_id: str
    status: ApplicationStatus
    applied_at: datetime


class ApplicationStatusUpdateRequest(BaseModel):
    status: ApplicationStatus


class ApplicationDetail(ApplicationResponse):
    """Enriched view for TPOs reviewing applicants — adds just enough
    student/resume context to make a shortlist/reject decision without a
    second round-trip per applicant."""

    student_name: str
    student_department: str | None
    student_cgpa: float | None
    resume_filename: str | None
