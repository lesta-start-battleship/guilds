from pydantic import BaseModel, Field
from typing import Optional, List

class Response[_BaseSchema](BaseModel):
    error: Optional[str] = Field(description='Error essage')
    error_code: int = Field(description='Error code')
    status: bool = Field(default=True, description='Response status')
    value: Optional[_BaseSchema] = Field(description='')
    
class BasePagination[_BaseSchema](BaseModel):
    items: List[_BaseSchema] = Field(description='List of items')
    total_items: int = Field(description='Total number of items')
    total_pages: int = Field(description='Total pages')