from dataclasses import dataclass, field
from typing import Optional, List
import re

TAG_PATTERN = re.compile(r'^[A-Za-z0-9_]+$')
MIN_TAG_LENGTH = 3
MAX_TAG_LENGTH = 20

@dataclass(frozen=True)
class Tag:
    value: str
    
    def __post_init__(self):
        if not (MIN_TAG_LENGTH <= len(self.value) <= MAX_TAG_LENGTH):
            raise ValueError(f'Tag length must be between {MIN_TAG_LENGTH} and {MAX_TAG_LENGTH}')
        if not TAG_PATTERN.match(self.value):
            raise ValueError('Tag must contain only latin letters, digits, and underscore')

@dataclass
class Role:
    id: int
    title: str
    edit: float
    owner: float

@dataclass
class Member:
    id: int
    user_id: int
    user_name: str
    role_id: int

@dataclass
class Guild:
    id: int
    tag: Tag
    title: Optional[str] = None
    description: Optional[str] = None
    owner_id: int
    members: List[Member] = field(default_factory=list)