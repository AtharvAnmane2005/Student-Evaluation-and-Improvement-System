"""
Student profile read/update logic (Phase 12).

This didn't exist before Phase 12 — `StudentInDB` has held these fields
since Phase 4, but nothing ever exposed them for the student to view or
edit. The dashboard's profile-completeness widget, and the "complete your
profile" flow after a first-time Google sign-in (see Phase 4 addendum),
both need this to actually do something.
"""
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.user import StudentInDB, StudentProfileUpdateRequest
from app.repositories.profile_repositories import StudentRepository

# Fields that count toward "is this profile filled out" — deliberately a
# simple, transparent completeness metric (each field is worth an equal
# share) rather than a weighted formula, since there's no product
# requirement yet for some fields mattering more than others.
_COMPLETENESS_FIELDS = (
    "department",
    "batch_year",
    "cgpa",
    "phone",
    "linkedin_url",
    "github_url",
    "skills",
    "active_resume_id",
)


def _compute_completeness_pct(student: StudentInDB) -> float:
    filled = 0
    for field in _COMPLETENESS_FIELDS:
        value = getattr(student, field)
        if isinstance(value, list):
            if len(value) > 0:
                filled += 1
        elif value is not None:
            filled += 1
    return round(100 * filled / len(_COMPLETENESS_FIELDS), 1)


class StudentProfileError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(message)


class StudentProfileService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.students = StudentRepository(db)

    async def get_profile(self, user_id: str) -> StudentInDB:
        student = await self.students.get_by_user_id(user_id)
        if not student:
            raise StudentProfileError(404, "Student profile not found.")
        return student

    async def update_profile(self, user_id: str, payload: StudentProfileUpdateRequest) -> StudentInDB:
        student = await self.get_profile(user_id)

        # Only include fields the caller actually sent (exclude_unset), so
        # omitting a field never wipes existing data — a partial PUT, same
        # convention as DriveUpdateRequest in Phase 8.
        updates = payload.model_dump(exclude_unset=True)
        if not updates:
            return student

        merged = student.model_copy(update=updates)
        updates["profile_completeness_pct"] = _compute_completeness_pct(merged)

        updated = await self.students.update_by_id(student.id, updates)
        assert updated is not None  # student.id was just validated above
        return updated
