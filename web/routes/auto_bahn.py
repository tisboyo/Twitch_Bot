from fastapi import APIRouter
from fastapi import Request
from fastapi.exceptions import HTTPException
from fastapi.params import Depends
from fastapi.params import Form
from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse
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


@router.get("/autoban/manage/")
async def autoban_manage(request: Request, user=Depends(check_user(level=AuthLevel.admin))):
    return RedirectResponse("/autoban/manage.html")


@router.get("/autoban/manage.html")
async def autoban_manage_html(request: Request, user=Depends(check_user(level=AuthLevel.admin))):

    result = db.session.query(BotRegex).order_by(BotRegex.id).all()

    response = templates.TemplateResponse("manage.html.jinja", {"request": request, "result": result})
    response.set_cookie("msg", "")
    return response


@router.get("/autoban/manage.js")
async def autoban_manage_js(request: Request, user=Depends(check_user(level=AuthLevel.admin))):

    return FileResponse("static_files/autoban/manage.js")


@router.post("/autoban/manage/enable")
async def autoban_manage_enable(
    request: Request,
    regex_id: int = Form(...),
    enable: bool = Form(...),
    user=Depends(check_user(level=AuthLevel.admin)),
):
    query = db.session.query(BotRegex).filter(BotRegex.id == regex_id).one_or_none()
    if query:
        query.enabled = enable
        db.session.commit()
        return HTMLResponse(f"BotRegex #{query.id} {'enabled' if query.enabled else 'disabled'}.")
    else:
        # Announcement ID wasn't in database
        raise HTTPException(404)


@router.post("/autoban/manage/delete")
async def autoban_manage_delete(
    request: Request, regex_id: int = Form(...), user=Depends(check_user(level=AuthLevel.admin))
):
    query = db.session.query(BotRegex).filter(BotRegex.id == regex_id).one_or_none()

    if query:
        db.session.query(BotRegex).filter(BotRegex.id == regex_id).delete
        db.session.commit()
        print(f"{user.username} Deleted BotRegEx: {query.pattern}")
        return HTMLResponse(f"Deleted: {query.pattern}")
    else:
        # Announcement ID wasn't in database
        raise HTTPException(404)
