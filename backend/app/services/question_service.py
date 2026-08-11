"""
Admin-facing question bank management.

Import/export is JSON-based (bulk create from a JSON array, and a JSON
dump of matching questions) rather than CSV/Excel. This satisfies the
"import questions / export questions" requirement functionally without
pulling in a spreadsheet-parsing dependency for what's fundamentally a
JSON-shaped resource — CSV/Excel support is a reasonable future addition
if a real workflow need for it shows up.
"""
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.assessment import (
    DIFFICULTY_MARKS,
    CategoryCreateRequest,
    QuestionCategoryInDB,
    QuestionCreateRequest,
    QuestionInDB,
    QuestionType,
    QuestionUpdateRequest,
)
from app.repositories.question_repository import QuestionCategoryRepository, QuestionRepository


class QuestionError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class QuestionService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.categories = QuestionCategoryRepository(db)
        self.questions = QuestionRepository(db)

    async def create_category(self, payload: CategoryCreateRequest) -> QuestionCategoryInDB:
        return await self.categories.create(
            {"name": payload.name, "parent_category_id": payload.parent_category_id}
        )

    @staticmethod
    def _validate_question_payload(
        question_type: QuestionType, options: list[str], correct_answer: str | None
    ) -> None:
        if question_type == QuestionType.MCQ:
            if len(options) < 2:
                raise QuestionError("MCQ questions need at least 2 options.")
            if not correct_answer:
                raise QuestionError("MCQ questions require a correct_answer.")
            if correct_answer not in options:
                raise QuestionError("correct_answer must be one of the provided options.")
        elif question_type == QuestionType.CODING:
            if not correct_answer:
                raise QuestionError("Coding questions require an expected-output correct_answer.")

    async def create_question(self, admin_user_id: str, payload: QuestionCreateRequest) -> QuestionInDB:
        category = await self.categories.get_by_id(payload.category_id)
        if not category:
            raise QuestionError("Category not found.", 404)

        self._validate_question_payload(payload.type, payload.options, payload.correct_answer)

        return await self.questions.create(
            {
                "category_id": payload.category_id,
                "skill_tags": payload.skill_tags,
                "difficulty": payload.difficulty.value,
                "type": payload.type.value,
                "text": payload.text,
                "options": payload.options,
                "correct_answer": payload.correct_answer,
                "marks": DIFFICULTY_MARKS[payload.difficulty],
                "company_tags": payload.company_tags,
                "created_by": admin_user_id,
                "created_at": datetime.utcnow(),
            }
        )

    async def update_question(self, question_id: str, payload: QuestionUpdateRequest) -> QuestionInDB:
        existing = await self.questions.get_by_id(question_id)
        if not existing:
            raise QuestionError("Question not found.", 404)

        update_data = payload.model_dump(exclude_unset=True)

        new_type = payload.type or existing.type
        new_options = payload.options if payload.options is not None else existing.options
        new_answer = payload.correct_answer if "correct_answer" in update_data else existing.correct_answer
        self._validate_question_payload(new_type, new_options, new_answer)

        if "difficulty" in update_data:
            update_data["marks"] = DIFFICULTY_MARKS[payload.difficulty]
            update_data["difficulty"] = payload.difficulty.value
        if "type" in update_data:
            update_data["type"] = payload.type.value

        updated = await self.questions.update_by_id(question_id, update_data)
        if not updated:
            raise QuestionError("Question not found.", 404)
        return updated

    async def delete_question(self, question_id: str) -> None:
        deleted = await self.questions.delete_by_id(question_id)
        if not deleted:
            raise QuestionError("Question not found.", 404)

    async def bulk_import(self, admin_user_id: str, questions: list[QuestionCreateRequest]) -> list[QuestionInDB]:
        created = []
        for payload in questions:
            created.append(await self.create_question(admin_user_id, payload))
        return created

    async def export_questions(
        self, category_id: str | None = None, difficulty: str | None = None
    ) -> list[QuestionInDB]:
        return await self.questions.find_by_filters(category_id=category_id, difficulty=difficulty, limit=1000)
