from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class TermResponse(BaseModel):
    word: str
    tf: int
    idf: float

