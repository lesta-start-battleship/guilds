from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class InviteResponse(BaseModel):
    ...
    
class RequestResponse(BaseModel):
    user_id: int
    user_name: Optional[str]
    created_at: datetime