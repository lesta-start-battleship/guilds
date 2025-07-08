from dataclasses import dataclass
from re import fullmatch

from settings import settings

from domain.values.base import BaseValueObject
from domain.exceptions.tag import InvalidTagFormatException


pattern = fr'^[A-Za-z0-9_]{{{settings.tag_min_length},{settings.tag_max_length}}}$'

@dataclass(frozen=True)
class Tag(BaseValueObject):
    value: str
    
    def __post_init__(self):
        self.validate()
    
    def validate(self):
        if fullmatch(pattern, self.value) is None:
            raise InvalidTagFormatException(self.value)
    
    def as_generic_type(self):
        return str(self.value)
    
    def __str__(self):
        return self.value
