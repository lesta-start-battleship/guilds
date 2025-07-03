from pydantic import BaseModel
from typing import Optional

class AddMemberRequest(BaseModel):
    user_id: int
    user_name: Optional[str]

class EditMemberRequest(BaseModel):
    role_id: Optional[int]
    
class MemberResponse(AddMemberRequest):
    guild_id: int
    role_id: Optional[int]