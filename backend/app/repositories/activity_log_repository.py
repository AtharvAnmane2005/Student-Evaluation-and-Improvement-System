from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.activity_log import ActivityLogInDB
from app.repositories.base import BaseRepository


class ActivityLogRepository(BaseRepository[ActivityLogInDB]):
    collection_name = "activity_logs"
    model = ActivityLogInDB


async def log_activity(
    db: AsyncIOMotorDatabase,
    user_id: str,
    action: str,
    entity: str,
    entity_id: str,
    metadata: dict | None = None,
    ip_address: str | None = None,
) -> None:
    """Fire-and-forget audit trail write. Never raises — a logging failure
    should never take down the actual request it's logging."""
    try:
        await ActivityLogRepository(db).create(
            {
                "user_id": user_id,
                "action": action,
                "entity": entity,
                "entity_id": entity_id,
                "metadata": metadata or {},
                "ip_address": ip_address,
            }
        )
    except Exception:
        import logging

        logging.getLogger(__name__).exception("Failed to write activity log (action=%s)", action)
