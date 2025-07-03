from fastapi import APIRouter
from .test_router import router as test

router = APIRouter()

router.include_router(test)


