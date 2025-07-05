from fastapi import APIRouter
from .chat import router as chat

router = APIRouter(prefix='/chat', tags=['Chat'])
router.include_router(chat)
