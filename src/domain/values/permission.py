from enum import Enum

class Permission(str, Enum):
    owner = 'owner'
    invite_members = 'invite_members'
    kick_members = 'kick_members'
    promote_members = 'promote_members'
    wars = 'wars'
    
    def __str__(self):
        return self.value