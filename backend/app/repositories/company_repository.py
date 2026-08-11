import re

from app.models.drive import CompanyInDB
from app.repositories.base import BaseRepository


class CompanyRepository(BaseRepository[CompanyInDB]):
    collection_name = "companies"
    model = CompanyInDB

    async def get_by_name(self, name: str) -> CompanyInDB | None:
        return await self.find_one({"name": {"$regex": f"^{re.escape(name)}$", "$options": "i"}})
