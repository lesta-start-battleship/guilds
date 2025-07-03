from pydantic import BaseModel
from typing import Optional

from schemas.base import BasePagination
from schemas.role import RoleResponse

class AddMemberRequest(BaseModel):
    user_id: int
    user_name: Optional[str]

class EditMemberRequest(BaseModel):
    role_id: Optional[int]
    user_name: Optional[str]
    
class MemberResponse(AddMemberRequest):
    guild_id: int
    guild_tag: str
    role: RoleResponse
    
class MemberPagination(BasePagination[MemberResponse]):
    ...