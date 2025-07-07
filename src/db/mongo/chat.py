from typing import Optional, Any
from datetime import datetime
from bson import ObjectId
from pydantic import BaseModel, Field, ConfigDict, field_serializer
from pydantic_core import core_schema
from pydantic import GetCoreSchemaHandler


class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.json_or_python_schema(
            python_schema=core_schema.with_info_plain_validator_function(cls.validate),
            json_schema=core_schema.with_info_plain_validator_function(cls.validate)
        )

    @classmethod
    def validate(cls, v, _info=None):
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str):
            try:
                return ObjectId(v)
            except Exception:
                raise ValueError("Invalid ObjectId string")
        raise TypeError("Invalid type for ObjectId")


class MongoChatMessage(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    guild_id: int
    user_id: int
    # user_name: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )

    @field_serializer("id")
    def serialize_id(self, value: Optional[PyObjectId], _info) -> Optional[str]:
        return str(value) if value is not None else None
