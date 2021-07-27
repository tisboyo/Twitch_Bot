from os import getenv

import jwt
from fastapi.routing import APIRouter
from fastapi_sqlalchemy import db
from munch import munchify
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette_discord.client import DiscordOAuthClient
from uvicorn.main import logger

from models import WebAuth

router = APIRouter()

CLIENT_ID = getenv("DISCORD_CLIENT_ID")
CLIENT_SECRET = getenv("DISCORD_CLIENT_SECRET")
REDIRECT_URI = f"https://{getenv('WEB_HOSTNAME')}/callback"
webauth_client = DiscordOAuthClient(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)


def get_user(request: Request) -> dict:
    try:
        encoded = request.session.get("discord_user")
        user = jwt.decode(encoded, getenv("WEB_COOKIE_KEY"), algorithms="HS256")
    except Exception as e:
        print(e)
        raise HTTPException(401)

    query = db.session.query(WebAuth).filter(WebAuth.id == user["id"]).one_or_none()
    if query:
        user["enabled"] = query.enabled
        user["admin"] = query.admin
        user["mod"] = query.mod
        user["user"] = query.user

    new_user = munchify(user)
    return new_user


def check_user_valid(request: Request) -> dict:
    try:
        encoded = request.session.get("discord_user")
        user = jwt.decode(encoded, getenv("WEB_COOKIE_KEY"), algorithms="HS256")

    except jwt.exceptions.InvalidSignatureError:
        # JWT decode key is most likely invalid
        raise HTTPException(500)

    except jwt.exceptions.DecodeError:
        # Modified JWT or no session cookie set
        raise HTTPException(401)

    except Exception as e:
        print(e)
        raise HTTPException(500)

    if not user:
        raise HTTPException(401)

    # Check if the user is a permitted user, and is enabled
    if db.session.query(WebAuth).filter(WebAuth.id == int(user["id"]), WebAuth.enabled == True).one_or_none():  # noqa E712
        return True
    else:
        raise HTTPException(403)


@router.get("/login")
async def login_with_discord():
    return webauth_client.redirect()


@router.get("/logout")
async def logout(request: Request):
    request.session["discord_user"] = None


# NOTE: REDIRECT_URI should be this path.
@router.get("/callback")
async def callback(request: Request, code: str):
    user = await webauth_client.login(code)
    encoded = jwt.encode(user, getenv("WEB_COOKIE_KEY"), algorithm="HS256")
    request.session["discord_user"] = encoded
    logger.info(f"{user['username']} logged into webserver")

    # If the user doesn't exist in the database, insert them.
    # Doing the query without checking if they are enabled allows for
    # disabling users and them not being reinserted
    query = db.session.query(WebAuth).filter(WebAuth.id == int(user["id"])).one_or_none()
    if not query:
        new_user = WebAuth(
            id=user["id"],
            name=f"{user['username']}#{user['discriminator']}",
            enabled=True,
            user=True,
        )
        db.session.add(new_user)
        db.session.commit()

    return RedirectResponse("/")


@router.get("/user_data")
async def user_data(request: Request):
    check_user_valid(request)
    user = get_user(request)

    return user
