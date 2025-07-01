from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db

from .schemas import DeclareWarRequest

router = APIRouter()


@router.post("/declare")
async def declare_war(data: DeclareWarRequest, session: AsyncSession = Depends(get_db)):
    return {
        "status": "pending",
        "message": f"Guild {data.initiator_guild_id} declared war on Guild {data.target_guild_id}"
    }