from pydantic import BaseModel
from typing import Optional

from schemas.base import BasePagination

class EditGuildRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class CreateGuildRequest(EditGuildRequest):
    tag: str

class GuildResponse(CreateGuildRequest):
    id: int
    owner_id: int
    is_active: bool
    is_full: bool
    
class GuildPagination(BasePagination[GuildResponse]):
    ...