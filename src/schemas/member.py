from pydantic import BaseModel
from typing import Optional

from schemas.base import BasePagination
from schemas.role import RoleResponse

class AddMemberRequest(BaseModel):
    user_name: Optional[str] = None

class EditMemberRequest(BaseModel):
    role_id: int
class MemberResponse(AddMemberRequest):
    user_id: int
    guild_id: int
    guild_tag: str
    role: Optional[RoleResponse] = None
    
class MemberPagination(BasePagination[MemberResponse]):
    ...

class MemberShopResponse(BaseModel):
    user_id: int