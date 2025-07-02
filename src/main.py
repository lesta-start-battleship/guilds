from fastapi import FastAPI

from api.v1.start_endpoints import router as start
from api.v1.guild import router as guild
from api.v1.member import router as member

from settings import settings


app = FastAPI(
    title=settings.project.title,
    description=settings.project.description,
    version=settings.project.release_version,
    debug=settings.debug
)

app.include_router(start, prefix="/api/v1", tags=["old"])
app.include_router(guild, prefix='/api/v1/guild', tags=['guild'])
app.include_router(member, prefix='/api/v1/member', tags=['member'])