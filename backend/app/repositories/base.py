"""
Generic repository base class.

Every collection-specific repository (UserRepository, ResumeRepository, ...)
subclasses this to get consistent CRUD + pagination behavior, keeping raw
Motor/PyMongo calls out of the service layer entirely (Repository Pattern,
per project rule #8).
"""
from typing import Any, Generic, TypeVar

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase
from pydantic import BaseModel

ModelT = TypeVar("ModelT", bound=BaseModel)


class BaseRepository(Generic[ModelT]):
    collection_name: str
    model: type[ModelT]

    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db

    @property
    def collection(self) -> AsyncIOMotorCollection:
        return self._db[self.collection_name]

    async def create(self, data: dict[str, Any]) -> ModelT:
        result = await self.collection.insert_one(data)
        doc = await self.collection.find_one({"_id": result.inserted_id})
        return self.model.model_validate(doc)

    async def get_by_id(self, doc_id: str) -> ModelT | None:
        if not ObjectId.is_valid(doc_id):
            return None
        doc = await self.collection.find_one({"_id": ObjectId(doc_id)})
        return self.model.model_validate(doc) if doc else None

    async def find_one(self, query: dict[str, Any]) -> ModelT | None:
        doc = await self.collection.find_one(query)
        return self.model.model_validate(doc) if doc else None

    async def find_many(
        self,
        query: dict[str, Any] | None = None,
        page: int = 1,
        limit: int = 20,
        sort: list[tuple[str, int]] | None = None,
    ) -> list[ModelT]:
        query = query or {}
        cursor = self.collection.find(query)
        if sort:
            cursor = cursor.sort(sort)
        cursor = cursor.skip((page - 1) * limit).limit(limit)
        return [self.model.model_validate(doc) async for doc in cursor]

    async def count(self, query: dict[str, Any] | None = None) -> int:
        return await self.collection.count_documents(query or {})

    async def update_by_id(self, doc_id: str, data: dict[str, Any]) -> ModelT | None:
        if not ObjectId.is_valid(doc_id):
            return None
        await self.collection.update_one({"_id": ObjectId(doc_id)}, {"$set": data})
        return await self.get_by_id(doc_id)

    async def delete_by_id(self, doc_id: str) -> bool:
        if not ObjectId.is_valid(doc_id):
            return False
        result = await self.collection.delete_one({"_id": ObjectId(doc_id)})
        return result.deleted_count == 1
