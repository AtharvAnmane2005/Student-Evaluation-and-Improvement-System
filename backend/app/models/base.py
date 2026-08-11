"""
Shared Pydantic base types for MongoDB documents.

PyObjectId lets Pydantic v2 models accept/emit MongoDB ObjectIds as plain
strings over the API (never leaking bson types into JSON responses) while
still round-tripping cleanly with Motor.
"""
from typing import Annotated, Any

from bson import ObjectId
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field


def _validate_object_id(value: Any) -> str:
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, str) and ObjectId.is_valid(value):
        return value
    raise ValueError(f"Invalid ObjectId: {value!r}")


PyObjectId = Annotated[str, BeforeValidator(_validate_object_id)]


class MongoBaseModel(BaseModel):
    """Base for documents read from MongoDB — aliases `_id` to `id`."""

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )

    id: PyObjectId | None = Field(default=None, alias="_id")
