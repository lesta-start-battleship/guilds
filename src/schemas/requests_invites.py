from pydantic import BaseModel
from datetime import datetime
from typing import Optional
    
class RequestResponse(BaseModel):
    user_id: int
    # user_name: Optional[str]
    created_at: datetime