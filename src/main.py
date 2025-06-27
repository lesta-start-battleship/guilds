from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

from starlette.templating import Jinja2Templates

from api.v1.start_endpoints import router as start
from api.v2.endpoints.start_endpoints import router as start_endpoints
from api.v2.endpoints.documents import router as documents
from api.v2.endpoints.collection import router as collection
from api.v2.endpoints.users import router as users_router

from settings import settings

from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(
    title=settings.project.title,
    description=settings.project.description,
    version=settings.project.release_version,
    debug=settings.debug
)
Instrumentator().instrument(app).expose(
    app,
    endpoint="/metrics",
    tags=["start"],
    include_in_schema=False
)

templates = Jinja2Templates(directory="templates")

app.include_router(start, prefix="/api/v1", tags=["old"])
app.include_router(start_endpoints, prefix="/api/v2", tags=["start"])
app.include_router(documents, prefix="/api/v2", tags=["documents"])
app.include_router(collection, prefix="/api/v2", tags=["collection"])
app.include_router(users_router, prefix="/api/v2", tags=["users"])


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def upload_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
