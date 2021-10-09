import datetime
import json
from os import getenv

from fastapi import APIRouter
from fastapi.params import Depends
from fastapi.params import Form
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi_sqlalchemy import db
from starlette.requests import Request
from web_auth import AuthLevel
from web_auth import check_user

from models import Settings

router = APIRouter()
templates = Jinja2Templates(directory="static_files/twitch")


@router.get("/twitch/oauth")
async def get_twitch_oauth(request: Request, user=Depends(check_user(level=AuthLevel.admin))):
    return RedirectResponse("/twitch/oauth.html")


@router.get("/twitch/oauth.html")
async def get_twitch_oauth_html(request: Request, user=Depends(check_user(level=AuthLevel.admin))):
    updated = dict()

    query = db.session.query(Settings).filter(Settings.key == "twitch_irc_token").one_or_none()
    if query:
        js = json.loads(query.value)
        updated["irc"] = js["updated"]

    query = db.session.query(Settings).filter(Settings.key == "twitch_pubsub_token").one_or_none()
    if query:
        js = json.loads(query.value)
        updated["pubsub"] = js["updated"]

    response = templates.TemplateResponse("oauth.html.jinja", {"request": request, "updated": updated})

    return response


@router.get("/twitch/oauth.js")
async def get_twitch_oauth_js(request: Request, user=Depends(check_user(level=AuthLevel.admin))):
    response = templates.TemplateResponse("oauth.js", {"request": request})
    return response


@router.get("/twitch/oauth/start/irc")
async def get_twitch_oauth_start_irc(request: Request, user=Depends(check_user(level=AuthLevel.admin))):
    client_id = getenv("CLIENT_ID") or getenv("client_id")
    web_hostname = getenv("WEB_HOSTNAME")

    irc_scope = [
        "chat:read",
        "chat:edit",
        "channel:moderate",
        "whispers:read",
        "whispers:edit",
        "channel_editor",
        "channel:manage:polls",
    ]
    return_url = f"https://{web_hostname}/twitch/oauth/process.html"
    redirect = f"https://id.twitch.tv/oauth2/authorize?response_type=token&client_id={client_id}&redirect_uri={return_url}&force_verify=true&state=irc&scope={'+'.join(irc_scope)}"  # noqa:E501

    return RedirectResponse(redirect)


@router.get("/twitch/oauth/start/pubsub")
async def get_twitch_oauth_start_pubsub(request: Request, user=Depends(check_user(level=AuthLevel.admin))):
    client_id = getenv("CLIENT_ID") or getenv("client_id")
    web_hostname = getenv("WEB_HOSTNAME")
    pubsub_scope = [
        "channel:read:redemptions",
        "channel:moderate+bits:read",
        "channel_subscriptions",
        "channel:manage:polls",
    ]
    return_url = f"https://{web_hostname}/twitch/oauth/process.html"
    redirect = f"https://id.twitch.tv/oauth2/authorize?response_type=token&client_id={client_id}&redirect_uri={return_url}&force_verify=true&state=pubsub&scope={'+'.join(pubsub_scope)}"  # noqa:E501
    return RedirectResponse(redirect)


@router.get("/twitch/oauth/process.html")
async def get_twitch_oauth_process(request: Request, user=Depends(check_user(level=AuthLevel.admin))):
    response = templates.TemplateResponse("oauth_process.html.jinja", {"request": request})
    return response


@router.get("/twitch/oauth/process.js")
async def get_twitch_oauth_process_js(request: Request, user=Depends(check_user(level=AuthLevel.admin))):
    return FileResponse("static_files/twitch/oauth_process.js")


@router.post("/twitch/oauth/save")
async def post_twitch_oauth_save(
    request: Request,
    type: str = Form(...),
    access_token: str = Form(...),
    user=Depends(check_user(level=AuthLevel.admin)),
):
    if type == "irc":
        v = json.dumps({"access_token": f"oauth:{access_token}", "updated": datetime.datetime.now()}, default=str)
        updated = db.session.query(Settings).filter(Settings.key == "twitch_irc_token").update({"value": v})
        if not updated:
            ins = Settings(key="twitch_irc_token", value=v)
            db.session.add(ins)
        db.session.commit()

        return JSONResponse(
            {
                "message": "IRC key updated.",
                "last_update": datetime.datetime.now().isoformat(),
                "redirect": "/twitch/oauth.html",
            }
        )

    elif type == "pubsub":
        v = json.dumps({"access_token": access_token, "updated": datetime.datetime.now()}, default=str)
        updated = db.session.query(Settings).filter(Settings.key == "twitch_pubsub_token").update({"value": v})
        if not updated:
            ins = Settings(key="twitch_pubsub_token", value=v)
            db.session.add(ins)
        db.session.commit()

        return JSONResponse(
            {
                "message": "PubSub key updated.",
                "last_update": datetime.datetime.now().isoformat(),
                "redirect": "/twitch/oauth.html",
            }
        )

    return JSONResponse({"message": "Error"})
