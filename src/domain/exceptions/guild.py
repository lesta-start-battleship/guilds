class GuildAlreadyExistsException(Exception):
    def __init__(self, tag: str):
        super().__init__(f'Guild "{tag}" alreadry exists')
        
class GuildNotExistsException(Exception):
    def __init__(self, tag: str):
        super().__init__(f'Guild "{tag}" not exists')

class InvalidTagFormatException(Exception):
    def __init__(self, tag: str):
        super().__init__(f'Invalid tag format: {tag}')

class UserNotOwnerException(Exception):
    def __init__(self, user_id: int):
        super().__init__(f'User "{user_id}" is not owner')