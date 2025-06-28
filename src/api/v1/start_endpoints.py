from fastapi import APIRouter


router = APIRouter()


@router.get("/hello")
async def get_task_status():
    return {"status": "res"}


