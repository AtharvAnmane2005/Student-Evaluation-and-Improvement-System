"""
Knowledge tracing logic.

This is a deliberately SIMPLE exponential-moving-average mastery update,
not a full Bayesian Knowledge Tracing (BKT) model. A real BKT model needs
per-skill calibrated parameters (P(learn), P(guess), P(slip)) fitted from
real usage data — data that doesn't exist yet for a system with zero
assessment history. Shipping an uncalibrated "BKT" would be false
precision dressed up as rigor. This heuristic is transparent, reasonable,
and easy to replace with a real BKT model later once there's enough
attempt data to fit one meaningfully.
"""
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.assessment import DifficultyLevel, KnowledgeStateInDB
from app.repositories.knowledge_state_repository import KnowledgeStateRepository

LEARNING_RATE = 0.25
WEAK_THRESHOLD = 50.0
STRONG_THRESHOLD = 75.0

# Harder correct answers move mastery up faster; harder wrong answers move
# it down faster too — getting a Hard question wrong is a weaker signal of
# low mastery than getting an Easy one wrong, so it costs less.
DIFFICULTY_WEIGHT = {DifficultyLevel.EASY: 0.7, DifficultyLevel.MEDIUM: 1.0, DifficultyLevel.HARD: 1.3}


class KnowledgeTracingService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.knowledge_states = KnowledgeStateRepository(db)

    async def update_mastery(
        self, student_id: str, skill_tag: str, is_correct: bool, difficulty: DifficultyLevel
    ) -> KnowledgeStateInDB:
        existing = await self.knowledge_states.get_by_student_and_skill(student_id, skill_tag)

        weight = DIFFICULTY_WEIGHT[difficulty]
        target = 100.0 if is_correct else 0.0

        old_mastery = existing.mastery_pct if existing else 50.0  # start neutral, not zero
        delta = LEARNING_RATE * weight * (target - old_mastery)
        new_mastery = max(0.0, min(100.0, old_mastery + delta))

        new_attempts_count = (existing.attempts_count if existing else 0) + 1
        new_confidence = min(1.0, new_attempts_count / 10)  # grows toward 1.0 over ~10 attempts

        history_entry = {"date": datetime.utcnow().isoformat(), "mastery_pct": round(new_mastery, 2)}

        if existing:
            new_history = (existing.history + [history_entry])[-50:]  # bounded, avoid unbounded growth
            updated = await self.knowledge_states.update_by_id(
                existing.id,
                {
                    "mastery_pct": new_mastery,
                    "confidence": new_confidence,
                    "attempts_count": new_attempts_count,
                    "last_updated": datetime.utcnow(),
                    "history": new_history,
                },
            )
            return updated

        return await self.knowledge_states.create(
            {
                "student_id": student_id,
                "skill_tag": skill_tag,
                "mastery_pct": new_mastery,
                "confidence": new_confidence,
                "attempts_count": new_attempts_count,
                "last_updated": datetime.utcnow(),
                "history": [history_entry],
            }
        )

    async def get_weak_and_strong_topics(
        self, student_id: str
    ) -> tuple[list[KnowledgeStateInDB], list[KnowledgeStateInDB]]:
        states = await self.knowledge_states.get_all_for_student(student_id)
        weak = [s for s in states if s.mastery_pct < WEAK_THRESHOLD]
        strong = [s for s in states if s.mastery_pct >= STRONG_THRESHOLD]
        return weak, strong

    async def get_average_mastery(self, student_id: str) -> float | None:
        """
        Simple average across all tracked skills for this student. This is
        the "Knowledge Tracing Score" input the Phase 1 Placement Readiness
        formula (25% weight) needs — exposed here as a reusable building
        block. The FULL readiness score (combining this with resume score
        and semantic match) isn't assembled until a dashboard phase needs
        it, since those other two inputs depend on Phase 7/9 (blocked).
        """
        states = await self.knowledge_states.get_all_for_student(student_id)
        if not states:
            return None
        return sum(s.mastery_pct for s in states) / len(states)
