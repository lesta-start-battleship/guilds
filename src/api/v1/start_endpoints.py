from fastapi import APIRouter
from celery.result import AsyncResult
from services.services import task_status

router = APIRouter()


@router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    task = AsyncResult(task_id)
    return await task_status(task)

