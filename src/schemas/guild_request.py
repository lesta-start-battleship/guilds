from datetime import datetime
from pydantic import BaseModel

from schemas.base import BasePagination

class RequestResponse(BaseModel):
    user_id: int
    user_name: str
    created_at: datetime

class RequestPagination(BasePagination[RequestResponse]):
    ...