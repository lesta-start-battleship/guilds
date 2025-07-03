from fastapi import FastAPI

from api.v1.guild import router as guild
from api.v1.member import router as member
from api.v1.guild_request import router as guild_request

from settings import settings


app = FastAPI(
    title=settings.project.title,
    description=settings.project.description,
    version=settings.project.release_version,
    debug=settings.debug
)

app.include_router(guild, prefix='/api/v1/guild', tags=['guild'])
app.include_router(member, prefix='/api/v1/member', tags=['member'])
app.include_router(guild_request, prefix='api/v1/request', tags='guild request')