from pydantic import BaseModel
from typing import Optional

class AddMemberRequest(BaseModel):
    user_id: int
    user_name: Optional[str]

class EditMemberRequest(AddMemberRequest):
    user_name: Optional[str]
    role_id: Optional[int]
    
class MemberResponse(EditMemberRequest):
    user_id: int
    user_name: Optional[str]
    guild_id: int
    role_id: Optional[int]