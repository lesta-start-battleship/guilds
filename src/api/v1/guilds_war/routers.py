from fastapi import APIRouter
from .future_api import router as test
from .declare_war import router as declare_war

router = APIRouter(prefix="/guild/war")

router.include_router(declare_war)
router.include_router(test)


