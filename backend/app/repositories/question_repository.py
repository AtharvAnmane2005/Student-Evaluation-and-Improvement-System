from app.models.assessment import QuestionCategoryInDB, QuestionInDB
from app.repositories.base import BaseRepository


class QuestionCategoryRepository(BaseRepository[QuestionCategoryInDB]):
    collection_name = "question_categories"
    model = QuestionCategoryInDB


class QuestionRepository(BaseRepository[QuestionInDB]):
    collection_name = "questions"
    model = QuestionInDB

    async def find_by_filters(
        self,
        category_id: str | None = None,
        difficulty: str | None = None,
        skill_tag: str | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> list[QuestionInDB]:
        query: dict = {}
        if category_id:
            query["category_id"] = category_id
        if difficulty:
            query["difficulty"] = difficulty
        if skill_tag:
            query["skill_tags"] = skill_tag
        return await self.find_many(query, page=page, limit=limit)

    async def get_random_unused(
        self, category_ids: list[str], difficulty: str, exclude_ids: list[str]
    ) -> QuestionInDB | None:
        """
        Picks one question at the target difficulty from the given
        categories, excluding ones already asked in this attempt. Uses a
        simple "fetch candidates, pick randomly in Python" approach rather
        than Mongo's $sample — the question pools here are small enough
        (tens to low hundreds per category/difficulty) that this is both
        simpler and avoids $sample's known small-collection bias, and it
        works identically against mongomock in tests.
        """
        import random
        from bson import ObjectId

        query: dict = {"difficulty": difficulty}
        if category_ids:
            query["category_id"] = {"$in": category_ids}
        if exclude_ids:
            valid_exclude = [eid for eid in exclude_ids if ObjectId.is_valid(eid)]
            query["_id"] = {"$nin": [ObjectId(eid) for eid in valid_exclude]}

        candidates = await self.find_many(query, page=1, limit=200)
        return random.choice(candidates) if candidates else None
