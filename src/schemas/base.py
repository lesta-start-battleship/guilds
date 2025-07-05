from pydantic import BaseModel, Field
from pydantic.generics import GenericModel
from typing import Generic, TypeVar, Optional, List

T = TypeVar('T')

class Response(GenericModel, Generic[T]):
    error: Optional[str] = Field(description='Error message', default=None)
    error_code: int = Field(description='Error code')
    status: bool = Field(default=True, description='Response status')
    value: Optional[T] = Field(description='', default=None)
    
class MessageResponse(Response[None]):
    ...
    
class BasePagination(GenericModel, Generic[T]):
    items: List[T] = Field(description='List of items')
    total_items: int = Field(description='Total number of items')
    total_pages: int = Field(description='Total pages')