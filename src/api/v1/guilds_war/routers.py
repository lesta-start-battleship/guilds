from fastapi import APIRouter
from .future_api import router as test

router = APIRouter(prefix="/guild/war")

router.include_router(test)


