from fastapi import APIRouter
from fastapi.params import Depends
from fastapi.params import Form
from fastapi.templating import Jinja2Templates
from fastapi_sqlalchemy import db
from starlette.requests import Request
from starlette.responses import FileResponse
from starlette.responses import RedirectResponse
from web_auth import AuthLevel
from web_auth import check_user

from models import ThisOrThat

router = APIRouter()
templates = Jinja2Templates(directory="static_files/this_or_that")


@router.get("/thisorthat")
async def get_thisorthat(request: Request, user=Depends(check_user(level=AuthLevel.admin))):
    return RedirectResponse("/thisorthat/manage.html")


@router.get("/thisorthat/manage.html")
async def get_thisorthat_html(request: Request, user=Depends(check_user(level=AuthLevel.admin))):
    results = db.session.query(ThisOrThat).order_by(ThisOrThat.id).all()
    message = request.cookies.get("totmsg", "") or "Manage `This or That`"
    response = templates.TemplateResponse(
        "manage.html.jinja", {"request": request, "result": results, "user": user, "message": message}
    )
    response.set_cookie("totmsg", "")
    return response


@router.get("/thisorthat/manage.js")
async def get_thisorthat_js(request: Request, user=Depends(check_user(level=AuthLevel.admin))):
    return FileResponse("static_files/thisorthat/manage.js")


@router.post("/thisorthat/add")
async def get_thisorthat_add(
    request: Request,
    enabled: bool = Form(default=False),
    answer_1: str = Form(...),
    answer_2: str = Form(...),
    user=Depends(check_user(level=AuthLevel.admin)),
):
    pass


@router.post("/thisorthat/delete")
async def get_thisorthat_delete(request: Request, item_id: int = Form(...), user=Depends(check_user(level=AuthLevel.admin))):
    pass


@router.post("/thisorthat/enable")
async def get_thisorthat_enable(
    request: Request, item_id: int = Form(...), enable: bool = Form(...), user=Depends(check_user(level=AuthLevel.admin))
):
    pass
