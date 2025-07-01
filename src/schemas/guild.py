from pydantic import BaseModel
from typing import Optional

class EditGuildRequest(BaseModel):
    title: Optional[str]
    desciption: Optional[str]

class CreateGuildRequest(EditGuildRequest):
    tag: str

class GuildResponse(CreateGuildRequest):
    id: int
    owner_id: int