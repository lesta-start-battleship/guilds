from fastapi import APIRouter

from .chat import router as chat
from .guild import router as guild
from .member import router as member
from .guild_request import router as guild_request
from .guilds_war.routers import router as war

router = APIRouter(prefix='/api/v1', tags=['v1'])

router.include_router(chat, prefix='/chat', tags=['Chat'])
router.include_router(guild, prefix='guild', tags=['Guild'])
router.include_router(member, prefix='/member', tags=['Member'])
router.include_router(guild_request, prefix='/request', tags=['Guild Requests'])
router.include_router(war, prefix='/war', tags=['Guild Wars'])