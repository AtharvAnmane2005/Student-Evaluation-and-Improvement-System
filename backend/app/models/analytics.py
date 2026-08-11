"""
Response schemas for Phase 15 analytics.

Deliberately Python-side aggregation (fetch-then-group-in-memory) rather
than MongoDB aggregation pipelines — consistent with this project's
existing "simple first, optimize when there's a real need" approach (see
e.g. knowledge tracing being an EMA rather than real BKT), and it keeps
these endpoints testable against the same mongomock setup every other
test in this suite already uses without worrying about pipeline-operator
support gaps.
"""
from pydantic import BaseModel


class ApplicationStatusBreakdown(BaseModel):
    applied: int
    shortlisted: int
    rejected: int
    selected: int


class DriveFunnel(BaseModel):
    drive_id: str
    job_title: str
    company_name: str
    status: str
    total_applications: int
    breakdown: ApplicationStatusBreakdown


class TpoAnalyticsResponse(BaseModel):
    total_drives: int
    open_drives: int
    closed_drives: int
    total_applications: int
    breakdown: ApplicationStatusBreakdown
    selection_rate_pct: float  # selected / total_applications, 0 if no applications
    drives: list[DriveFunnel]


class SkillMasteryOverview(BaseModel):
    skill_tag: str
    avg_mastery_pct: float
    student_count: int


class AdminAnalyticsResponse(BaseModel):
    total_students: int
    total_tpos: int
    total_drives: int
    open_drives: int
    closed_drives: int
    total_applications: int
    application_breakdown: ApplicationStatusBreakdown
    placed_students: int  # unique students with at least one "selected" application
    placement_rate_pct: float  # placed_students / total_students, 0 if no students
    total_categories: int
    total_questions: int
    total_assessments: int
    total_attempts: int
    submitted_attempts: int
    average_score_pct: float  # across submitted attempts with nonzero max possible marks
    skill_mastery_overview: list[SkillMasteryOverview]
