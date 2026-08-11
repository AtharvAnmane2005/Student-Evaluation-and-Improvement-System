from app.models.assessment import AssessmentAttemptInDB
from app.repositories.base import BaseRepository


class AttemptRepository(BaseRepository[AssessmentAttemptInDB]):
    collection_name = "assessment_attempts"
    model = AssessmentAttemptInDB

    async def get_for_student(self, student_id: str) -> list[AssessmentAttemptInDB]:
        return await self.find_many({"student_id": student_id}, sort=[("started_at", -1)])
