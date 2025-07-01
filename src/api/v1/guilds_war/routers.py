from fastapi import APIRouter
from .future_api import router as test

router = APIRouter()

router.include_router(test)


