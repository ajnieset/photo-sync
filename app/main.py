from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

from .routes import upload


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

templates = Jinja2Templates(directory="templates")
app = FastAPI(lifespan=lifespan)

app.include_router(upload.router)

@app.get("/")
def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")