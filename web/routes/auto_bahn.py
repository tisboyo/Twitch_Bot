from fastapi import APIRouter
from fastapi import Request
from fastapi.params import Depends
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from web_auth import AuthLevel
from web_auth import check_user

# from fastapi.responses import HTMLResponse
# from fastapi_sqlalchemy import db
# from uvicorn.main import logger


router = APIRouter()
templates = Jinja2Templates(directory="static_files/autoban")


@router.get("/autoban")
async def autoban(request: Request, user=Depends(check_user(level=AuthLevel.admin))):
    return RedirectResponse("/autoban/manage")


@router.get("/autoban/manage")
async def autoban_manage(request: Request, user=Depends(check_user(level=AuthLevel.admin))):
    return templates.TemplateResponse("manage.html.jinja")
