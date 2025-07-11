from fastapi import APIRouter
from .future_api import router as test
from .declare_war import router as declare_war
from .confirm_war import router as confirm_war
from .cancel_war import router as cancel_war
from .list_war import router as list_war
from .get_war import router as get_war

router = APIRouter(prefix="/guild/war", tags=['Guild Wars'])

router.include_router(declare_war)
router.include_router(confirm_war)
router.include_router(cancel_war)
router.include_router(list_war)
router.include_router(get_war)


