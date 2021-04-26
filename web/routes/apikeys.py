from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi_sqlalchemy import db
from uvicorn.main import logger
from main import app


router = APIRouter()


async def setup(router):
    @router.get("/", response_class=HTMLResponse)
    async def apikeys_view(request: Request):
        print(request)
