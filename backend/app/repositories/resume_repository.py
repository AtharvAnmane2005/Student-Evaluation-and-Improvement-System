from app.models.resume import ResumeInDB
from app.repositories.base import BaseRepository


class ResumeRepository(BaseRepository[ResumeInDB]):
    collection_name = "resumes"
    model = ResumeInDB

    async def get_active_for_student(self, student_id: str) -> ResumeInDB | None:
        return await self.find_one({"student_id": student_id, "is_active": True})

    async def get_history_for_student(
        self, student_id: str, page: int = 1, limit: int = 20
    ) -> list[ResumeInDB]:
        return await self.find_many(
            {"student_id": student_id}, page=page, limit=limit, sort=[("version", -1)]
        )

    async def get_next_version_number(self, student_id: str) -> int:
        latest = await self.find_many(
            {"student_id": student_id}, page=1, limit=1, sort=[("version", -1)]
        )
        return (latest[0].version + 1) if latest else 1

    async def deactivate_all_for_student(self, student_id: str) -> None:
        await self.collection.update_many(
            {"student_id": student_id}, {"$set": {"is_active": False}}
        )
