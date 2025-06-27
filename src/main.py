from fastapi import FastAPI

from api.v1.start_endpoints import router as start

from settings import settings


app = FastAPI(
    title=settings.project.title,
    description=settings.project.description,
    version=settings.project.release_version,
    debug=settings.debug
)

app.include_router(start, prefix="/api/v1", tags=["old"])
