import aiohttp
from fastapi import APIRouter
from fastapi import Request
from fastapi.params import Depends
from fastapi.params import Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi_sqlalchemy import db
from starlette.responses import FileResponse
from starlette.responses import RedirectResponse
from web_auth import AuthLevel
from web_auth import check_user

from models import Settings

router = APIRouter()
templates = Jinja2Templates(directory="static_files/discord")


@router.get("/discord/webhook_manage", response_class=HTMLResponse)
def discord_webhook(request: Request, user=Depends(check_user(level=AuthLevel.admin))):
    return RedirectResponse("/discord/webhook_manage.html")


@router.get("/discord/webhook_manage.html", response_class=HTMLResponse)
def discord_webhook_html(request: Request, user=Depends(check_user(level=AuthLevel.admin))):

    key_list = ["to_do_webhook", "link_webhook", "ban_webhook"]

    result = db.session.query(Settings).filter(Settings.key.in_(key_list)).all()

    response = templates.TemplateResponse("webhook_manage.html.jinja", {"request": request, "result": result})
    return response


@router.get("/discord/webhook_manage.js", response_class=FileResponse)
def discord_webhook_js(request: Request, user=Depends(check_user(level=AuthLevel.admin))):
    return FileResponse("static_files/discord/webhook_manage.js")


@router.post("/discord/webhook_manage/save", response_class=HTMLResponse)
async def discord_webhook_manage_save(
    request: Request,
    webhook_name: str = Form(...),
    webhook_url: str = Form(...),
    user=Depends(check_user(level=AuthLevel.admin)),
):
    print(webhook_name, webhook_url)

    async with aiohttp.ClientSession() as session:
        response = await session.post(
            webhook_url,
            json={"content": "Testing webhook address", "username": f"TwitchBot: Webhook Test by {user.username}"},
        )
        if response.status == 204:
            result = db.session.query(Settings).filter(Settings.key == webhook_name).update({Settings.value: webhook_url})
            db.session.commit()
            if result:
                return "Updated"
            else:
                return "Database update error."

        else:
            return f"Error: {response.reason} {response.status}"
