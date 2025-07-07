from fastapi import APIRouter

from .guilds_war.routers import router as war
from .guilds.routers import router as guilds
from .chat.routers import router as chat

router = APIRouter(prefix='/api/v1')

router.include_router(chat)
router.include_router(war)
router.include_router(guilds)
