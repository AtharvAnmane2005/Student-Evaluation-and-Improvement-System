from app.models.user import AdminInDB, StudentInDB, TPOInDB
from app.repositories.base import BaseRepository


class StudentRepository(BaseRepository[StudentInDB]):
    collection_name = "students"
    model = StudentInDB

    async def get_by_user_id(self, user_id: str) -> StudentInDB | None:
        return await self.find_one({"user_id": user_id})


class TPORepository(BaseRepository[TPOInDB]):
    collection_name = "tpos"
    model = TPOInDB

    async def get_by_user_id(self, user_id: str) -> TPOInDB | None:
        return await self.find_one({"user_id": user_id})


class AdminRepository(BaseRepository[AdminInDB]):
    collection_name = "admins"
    model = AdminInDB

    async def get_by_user_id(self, user_id: str) -> AdminInDB | None:
        return await self.find_one({"user_id": user_id})
