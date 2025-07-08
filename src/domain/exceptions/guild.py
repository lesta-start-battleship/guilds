from dataclasses import dataclass

from domain.exceptions.base import ApplicationException

@dataclass
class GuildAlreadyExistsException(ApplicationException):
    text: str
    
    @property
    def message(self):
        return f'Гильдия с тегом {self.text} уже существует'

@dataclass
class GuildNotExistsException(ApplicationException):
    text: str
    
    @property
    def message(self):
        return f'Гильдии {self.text} не существует'

@dataclass
class GuildIsNotActiveException(ApplicationException):
    text: str
    
    @property
    def message(self):
        return f'Гильдия {self.text} не активна'

@dataclass
class GuildIsFullException(ApplicationException):
    text: str
    
    @property
    def message(self):
        return f'Гильдия {self.text} заполнена'