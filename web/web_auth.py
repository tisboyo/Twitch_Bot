import enum
from functools import lru_cache
from os import getenv

import jwt
from fastapi.exceptions import HTTPException
from fastapi.params import Depends
from fastapi.requests import Request
from fastapi.responses import RedirectResponse
from fastapi.routing import APIRouter
from fastapi_sqlalchemy import db
from munch import munchify
from starlette_discord.client import DiscordOAuthClient
from uvicorn.main import logger

from models import WebAuth

router = APIRouter()

CLIENT_ID = getenv("DISCORD_CLIENT_ID")
CLIENT_SECRET = getenv("DISCORD_CLIENT_SECRET")
REDIRECT_URI = f"https://{getenv('WEB_HOSTNAME')}/callback"
webauth_client = DiscordOAuthClient(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)


class AuthLevel(enum.Enum):
    user = enum.auto()
    mod = enum.auto()
    admin = enum.auto()


class RequiresLoginException(Exception):
    pass


def check_user(level: AuthLevel = AuthLevel.admin):
    """Checks the logged in user and redirects to login if they aren't the correct AuthLevel"""

    # The nested function is so we can get the level from the function and still pass the request in
    def check_user_req(request: Request):
        try:
            # Ensure logged in user
            check_jwt_valid(request)
            user = build_user(request)
            if level is AuthLevel.user and any([user.user, user.mod, user.admin]):
                return user
            elif level is AuthLevel.mod and any([user.mod, user.admin]):
                return user
            elif level is AuthLevel.admin and user.admin:
                return user
            else:
                raise HTTPException(403)

        except HTTPException:
            # Redirect to login if not logged in
            raise RequiresLoginException  # Defined in web_auth.py, handled on main.py

    return check_user_req


@lru_cache
def check_valid_api_key(level: AuthLevel) -> bool:
    """Check the api_key passed and determine if it is valid for the user in the request"""

    # The nested function is so we can get the level from the function and still pass the request in
    def check_api_key(request: Request):

        if not request.query_params.get("key", False):
            # key paramater not specified
            raise HTTPException(403)

        query = (
            db.session.query(WebAuth)
            .filter(WebAuth.api_key == request.query_params["key"], WebAuth.enabled == True)  # noqa E712
            .one_or_none()
        )

        if query:
            if level == AuthLevel.admin and query.admin:
                return request.query_params["key"]
            elif level == AuthLevel.mod and any([query.admin, query.mod]):
                return request.query_params["key"]
            elif level == AuthLevel.user and any([query.admin, query.mod, query.user]):
                return request.query_params["key"]
            else:
                raise HTTPException(403)
        else:
            raise HTTPException(403)

    return check_api_key


def build_user(request: Request) -> dict:
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

    # Convert the user id to an integer instead of a string
    user["id"] = int(user["id"])

    new_user = munchify(user)
    return new_user


def check_jwt_valid(request: Request) -> dict:
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
        print(new_user)
        # db.session.add(new_user)
        # db.session.commit()

    redirect_path = request.cookies.get("redirect", "/")
    response = RedirectResponse(redirect_path)
    response.delete_cookie("redirect")
    return response


@router.get("/user_data")
async def user_data(request: Request, user=Depends(check_user)):
    return user
