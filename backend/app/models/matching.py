from pydantic import BaseModel


class MatchScoreBreakdown(BaseModel):
    """Core hybrid-score output — field names match the notebook's
    compute_hybrid_scores_batch() dict keys exactly (final_score,
    semantic_score, skills_score, experience_score, matched_skills,
    missing_skills), so anyone comparing this API's output against the
    notebook's own evaluate_resume_pretty() report can do so directly."""

    final_score: float
    semantic_score: float
    skills_score: float
    experience_score: float
    matched_skills: list[str]
    missing_skills: list[str]


class DriveMatchScoreResponse(MatchScoreBreakdown):
    """Phase 7: single resume x single drive."""

    drive_id: str


class RecommendedDriveResponse(MatchScoreBreakdown):
    """Phase 9: one row of the student's ranked drive recommendations."""

    drive_id: str
    job_title: str
    company_name: str
    location: str | None
    package: str | None


class RankedApplicantResponse(MatchScoreBreakdown):
    """Phase 9: one row of a TPO's ranked applicant list for a drive."""

    application_id: str
    student_id: str
    student_name: str
    resume_id: str
