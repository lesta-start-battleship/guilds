from dataclasses import dataclass

from domain.exceptions.base import ApplicationException


@dataclass
class RequestAlreadyExistException(ApplicationException):
    guild_tag: str
    
    @property
    def message(self):
        return f'Запрос на вступление в {self.guild_tag} уже существует'

@dataclass
class RequestNotFoundException(ApplicationException):
    guild_tag: str
    
    @property
    def message(self):
        return f'Запрос на вступление в {self.guild_tag} не найден'