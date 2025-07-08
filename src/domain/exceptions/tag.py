from dataclasses import dataclass

from domain.exceptions.base import ApplicationException


@dataclass
class InvalidTagFormatException(ApplicationException):
    text: str
    
    @property
    def message(self):
        return f'Некорректный формат тега: {self.text}'