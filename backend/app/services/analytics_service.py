from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.analytics import (
    AdminAnalyticsResponse,
    ApplicationStatusBreakdown,
    DriveFunnel,
    SkillMasteryOverview,
    TpoAnalyticsResponse,
)
from app.models.assessment import DIFFICULTY_MARKS, AttemptStatus
from app.repositories.application_repository import ApplicationRepository
from app.repositories.assessment_repository import AssessmentRepository
from app.repositories.attempt_repository import AttemptRepository
from app.repositories.company_repository import CompanyRepository
from app.repositories.drive_repository import PlacementDriveRepository
from app.repositories.knowledge_state_repository import KnowledgeStateRepository
from app.repositories.profile_repositories import StudentRepository, TPORepository
from app.repositories.question_repository import QuestionCategoryRepository, QuestionRepository

# Generous but finite caps on "fetch everything" queries — this project's
# scale (a college placement cell, not a SaaS product) means these won't
# be hit in practice, but an unbounded find_many() against a collection
# that could theoretically grow unboundedly is still worth capping.
_ANALYTICS_FETCH_LIMIT = 5000


def _empty_breakdown() -> ApplicationStatusBreakdown:
    return ApplicationStatusBreakdown(applied=0, shortlisted=0, rejected=0, selected=0)


def _tally(applications) -> ApplicationStatusBreakdown:
    counts = {"applied": 0, "shortlisted": 0, "rejected": 0, "selected": 0}
    for app in applications:
        status = app.status.value if hasattr(app.status, "value") else app.status
        if status in counts:
            counts[status] += 1
    return ApplicationStatusBreakdown(**counts)


class AnalyticsService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.drives = PlacementDriveRepository(db)
        self.applications = ApplicationRepository(db)
        self.companies = CompanyRepository(db)
        self.students = StudentRepository(db)
        self.tpos = TPORepository(db)
        self.categories = QuestionCategoryRepository(db)
        self.questions = QuestionRepository(db)
        self.assessments = AssessmentRepository(db)
        self.attempts = AttemptRepository(db)
        self.knowledge_states = KnowledgeStateRepository(db)

    async def get_tpo_analytics(self, tpo_user_id: str) -> TpoAnalyticsResponse:
        tpo = await self.tpos.get_by_user_id(tpo_user_id)
        if not tpo:
            drives = []
        else:
            drives = await self.drives.find_many({"created_by": tpo.id}, limit=_ANALYTICS_FETCH_LIMIT)

        drive_funnels: list[DriveFunnel] = []
        overall = _empty_breakdown()
        open_count = 0
        closed_count = 0

        for drive in drives:
            if drive.status == "open":
                open_count += 1
            else:
                closed_count += 1

            applications = await self.applications.find_many({"drive_id": drive.id}, limit=_ANALYTICS_FETCH_LIMIT)
            breakdown = _tally(applications)
            for field in ("applied", "shortlisted", "rejected", "selected"):
                setattr(overall, field, getattr(overall, field) + getattr(breakdown, field))

            company = await self.companies.get_by_id(drive.company_id)
            drive_funnels.append(
                DriveFunnel(
                    drive_id=drive.id,
                    job_title=drive.job_title,
                    company_name=company.name if company else "Unknown company",
                    status=drive.status.value if hasattr(drive.status, "value") else drive.status,
                    total_applications=len(applications),
                    breakdown=breakdown,
                )
            )

        total_applications = overall.applied + overall.shortlisted + overall.rejected + overall.selected
        selection_rate = round(100 * overall.selected / total_applications, 1) if total_applications else 0.0

        return TpoAnalyticsResponse(
            total_drives=len(drives),
            open_drives=open_count,
            closed_drives=closed_count,
            total_applications=total_applications,
            breakdown=overall,
            selection_rate_pct=selection_rate,
            drives=drive_funnels,
        )

    async def get_admin_analytics(self) -> AdminAnalyticsResponse:
        total_students = await self.students.count({})
        total_tpos = await self.tpos.count({})
        total_drives = await self.drives.count({})
        open_drives = await self.drives.count({"status": "open"})
        closed_drives = total_drives - open_drives

        applications = await self.applications.find_many({}, limit=_ANALYTICS_FETCH_LIMIT)
        breakdown = _tally(applications)
        total_applications = len(applications)
        placed_student_ids = {a.student_id for a in applications if a.status == "selected"}
        placement_rate = round(100 * len(placed_student_ids) / total_students, 1) if total_students else 0.0

        total_categories = await self.categories.count({})
        total_questions = await self.questions.count({})
        total_assessments = await self.assessments.count({})

        attempts = await self.attempts.find_many({}, limit=_ANALYTICS_FETCH_LIMIT)
        total_attempts = len(attempts)
        submitted = [a for a in attempts if a.status == AttemptStatus.SUBMITTED]

        score_pcts = []
        for attempt in submitted:
            total_marks = sum(ans.marks_awarded for ans in attempt.answers)
            max_marks = sum(DIFFICULTY_MARKS[ans.difficulty_at_time] for ans in attempt.answers)
            if max_marks > 0:
                score_pcts.append(100 * total_marks / max_marks)
        average_score = round(sum(score_pcts) / len(score_pcts), 1) if score_pcts else 0.0

        knowledge_states = await self.knowledge_states.find_many({}, limit=_ANALYTICS_FETCH_LIMIT)
        by_skill: dict[str, list[float]] = {}
        for state in knowledge_states:
            by_skill.setdefault(state.skill_tag, []).append(state.mastery_pct)
        skill_overview = sorted(
            (
                SkillMasteryOverview(
                    skill_tag=tag,
                    avg_mastery_pct=round(sum(values) / len(values), 1),
                    student_count=len(values),
                )
                for tag, values in by_skill.items()
            ),
            key=lambda s: s.avg_mastery_pct,
        )

        return AdminAnalyticsResponse(
            total_students=total_students,
            total_tpos=total_tpos,
            total_drives=total_drives,
            open_drives=open_drives,
            closed_drives=closed_drives,
            total_applications=total_applications,
            application_breakdown=breakdown,
            placed_students=len(placed_student_ids),
            placement_rate_pct=placement_rate,
            total_categories=total_categories,
            total_questions=total_questions,
            total_assessments=total_assessments,
            total_attempts=total_attempts,
            submitted_attempts=len(submitted),
            average_score_pct=average_score,
            skill_mastery_overview=skill_overview,
        )
