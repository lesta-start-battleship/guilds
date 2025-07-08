from dataclasses import dataclass

from domain.exceptions.base import ApplicationException


@dataclass
class MemberNotFoundException(ApplicationException):
    text: int
    
    @property
    def message(self):
        return f'Пользователь {self.text} не состоит в гильдии'

@dataclass
class MemberAlreadyInGuildException(ApplicationException):
    text: int
    
    @property
    def message(self):
        return f'Пользователь {self.text} уже состоит в гильдии'

@dataclass
class MemberInOtherGuildException(ApplicationException):
    text: int
    
    @property
    def message(self):
        return f'Пользователь {self.text} состоит в другой гильдии'

@dataclass
class MemberNotHavePermissionException(ApplicationException):
    text: int
    
    @property
    def message(self):
        return f'у пользователя {self.text} недостаточно прав'

@dataclass
class MemberNotOwnerException(ApplicationException):
    text: int
    
    @property
    def message(self):
        return f'Пользователь {self.text} не является владельцем гильдии'