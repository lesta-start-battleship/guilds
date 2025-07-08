from dataclasses import dataclass

from domain.exceptions.base import ApplicationException


@dataclass
class RoleNotFoundException(ApplicationException):
    text: str
    
    @property
    def message(self):
        return f'Роль {self.text} не найдена'

@dataclass
class RoleAlreadyExistException(Exception):
    text: str
    
    @property
    def message(self):
        return f'Роль {self.text} уже существует'