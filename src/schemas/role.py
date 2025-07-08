from pydantic import BaseModel
from typing import Set

class RoleRequest(BaseModel):
    title: str
    permissions: Set[str]
    promote_roles: Set[int]

class RoleResponse(RoleRequest):
    id: int