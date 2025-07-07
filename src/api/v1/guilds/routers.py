from fastapi import APIRouter
from .guild import router as guild
from .member import router as member
from .guild_request import router as guild_request

router = APIRouter(prefix='/guild')

router.include_router(guild, tags=['Guild'])
router.include_router(member, prefix='/member', tags=['Member'])
router.include_router(guild_request, prefix='/request', tags=['Guild Requests'])
