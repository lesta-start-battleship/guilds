from pydantic import BaseModel
from typing import Optional

class RoleRequest(BaseModel):
    title: str
    edit: Optional[bool]
    balance: Optional[bool]
    owner: Optional[bool]

class RoleResponse(RoleRequest):
    id: int