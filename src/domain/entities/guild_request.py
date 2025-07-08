from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Optional

from domain.values.tag import Tag

@dataclass
class GuildJoinRequest:
    guild_tag: Tag
    user_id: int
    username: str
    status: Literal['pending', 'accepted', 'rejected', 'expired']
    created_at: Optional[datetime] = None