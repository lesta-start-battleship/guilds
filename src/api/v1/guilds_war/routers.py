from fastapi import APIRouter
from .future_api import router as test
from .declare_war import router as declare_war
from .confirm_war import router as confirm_war

router = APIRouter(prefix="/guild/war")

router.include_router(declare_war)
router.include_router(confirm_war)


