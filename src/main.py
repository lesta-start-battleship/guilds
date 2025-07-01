from fastapi import FastAPI

from api.v1.start_endpoints import router as start
from api.v1.chat import router as chat

from api.v1.guilds_war.routers import router as guild_war_router

from fastapi import Request
from settings import settings


app = FastAPI(
    title=settings.project.title,
    description=settings.project.description,
    version=settings.project.release_version,
    debug=settings.debug
)

app.include_router(start, prefix="/api/v1", tags=["old"])
app.include_router(chat, prefix="/api/v1", tags=["chat"])
app.include_router(guild_war_router, prefix="/api/v1", tags=["Guilds War"])
