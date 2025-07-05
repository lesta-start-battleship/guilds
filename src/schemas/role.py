from pydantic import BaseModel
from typing import Set

class RoleRequest(BaseModel):
    title: str
    permissions: Set[str]

class RoleResponse(RoleRequest):
    id: int