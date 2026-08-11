from app.models.assessment import KnowledgeStateInDB
from app.repositories.base import BaseRepository


class KnowledgeStateRepository(BaseRepository[KnowledgeStateInDB]):
    collection_name = "knowledge_states"
    model = KnowledgeStateInDB

    async def get_by_student_and_skill(self, student_id: str, skill_tag: str) -> KnowledgeStateInDB | None:
        return await self.find_one({"student_id": student_id, "skill_tag": skill_tag})

    async def get_all_for_student(self, student_id: str) -> list[KnowledgeStateInDB]:
        return await self.find_many({"student_id": student_id}, sort=[("mastery_pct", -1)], limit=200)
