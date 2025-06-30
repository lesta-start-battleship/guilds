from fastapi import FastAPI

from api.v1.start_endpoints import router as start
from api.v1.chat import router as chat

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


#
# @app.middleware("http")
# async def log_requests(request: Request, call_next):
#     print(f"🔍 Request: {request.client.host} {request.method} {request.url.path}")
#     print(f"📦 User-Agent: {request.headers.get('user-agent')}")
#     print(f"🕵️ Authorization: {request.headers.get('authorization')}")
#     response = await call_next(request)
#     return response
