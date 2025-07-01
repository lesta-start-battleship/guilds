from pydantic import BaseModel, Field

class DeclareWarRequest(BaseModel):
    initiator_guild_id: int = Field(..., description="ID гильдии, которая инициирует войну")
    target_guild_id: int = Field(..., description="ID гильдии, которой отправляется запрос на войну")

    initiator_owner_id: int = Field(..., description="ID владельца инициирующей гильдии (для проверки прав)")