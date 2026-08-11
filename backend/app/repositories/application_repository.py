from app.models.drive import ApplicationInDB
from app.repositories.base import BaseRepository


class ApplicationRepository(BaseRepository[ApplicationInDB]):
    collection_name = "applications"
    model = ApplicationInDB

    async def get_existing(self, drive_id: str, student_id: str) -> ApplicationInDB | None:
        return await self.find_one({"drive_id": drive_id, "student_id": student_id})

    async def get_for_student(self, student_id: str, page: int = 1, limit: int = 20) -> list[ApplicationInDB]:
        return await self.find_many({"student_id": student_id}, page=page, limit=limit, sort=[("applied_at", -1)])

    async def get_for_drive(self, drive_id: str, page: int = 1, limit: int = 50) -> list[ApplicationInDB]:
        return await self.find_many({"drive_id": drive_id}, page=page, limit=limit, sort=[("applied_at", -1)])
