from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel,  conlist
from datetime import datetime

router = APIRouter()



@router.get("./test")
async def get_rage(guild_id: int = Path(..., description="ID гильдии")):
    return {"test": "test"}  # заглушка



