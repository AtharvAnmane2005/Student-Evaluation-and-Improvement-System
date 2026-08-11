from datetime import datetime

from pydantic import Field

from app.models.base import MongoBaseModel, PyObjectId


class ActivityLogInDB(MongoBaseModel):
    user_id: PyObjectId
    action: str
    entity: str
    entity_id: str
    metadata: dict = Field(default_factory=dict)
    ip_address: str | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
