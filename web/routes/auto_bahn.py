from fastapi import APIRouter
from fastapi import Request
from fastapi.params import Depends
from fastapi.templating import Jinja2Templates
from fastapi_sqlalchemy import db
from starlette.responses import RedirectResponse
from web_auth import AuthLevel
from web_auth import check_user

from models import BotRegex

# from fastapi.responses import HTMLResponse
# from uvicorn.main import logger


router = APIRouter()
templates = Jinja2Templates(directory="static_files/autoban")


@router.get("/autoban")
async def autoban(request: Request, user=Depends(check_user(level=AuthLevel.admin))):
    return RedirectResponse("/autoban/manage")


@router.get("/autoban/manage")
async def autoban_manage(request: Request, user=Depends(check_user(level=AuthLevel.admin))):

    result = db.session.query(BotRegex).order_by(BotRegex.id).all()

    return templates.TemplateResponse("manage.html.jinja", {"request": request, "result": result})
