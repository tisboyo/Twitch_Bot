import datetime
import enum
from functools import lru_cache
from os import getenv

import jwt
from fastapi import Security
from fastapi.exceptions import HTTPException
from fastapi.params import Depends
from fastapi.requests import Request
from fastapi.responses import RedirectResponse
from fastapi.responses import Response
from fastapi.routing import APIRouter
from fastapi.security.api_key import APIKeyHeader
from fastapi.security.api_key import APIKeyQuery
from fastapi_sqlalchemy import db
from munch import munchify
from oauthlib.oauth2.rfc6749.errors import InvalidClientIdError
from starlette_discord.client import DiscordOAuthClient
from uvicorn.main import logger

from models import WebAuth

router = APIRouter()

CLIENT_ID = getenv("DISCORD_CLIENT_ID")
CLIENT_SECRET = getenv("DISCORD_CLIENT_SECRET")
REDIRECT_URI = f"https://{getenv('WEB_HOSTNAME')}/callback"
webauth_client = DiscordOAuthClient(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)
cookie_life = 604800  # In seconds, 604800 = 7 days


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
            user = build_user(request)
            if user.expires < datetime.datetime.now():
                # Cookie is expired if the timestamp for it is before now
                raise HTTPException(401)

            if level is AuthLevel.user and any([user.user, user.mod, user.admin]):
                return user
            elif level is AuthLevel.mod and any([user.mod, user.admin]):
                return user
            elif level is AuthLevel.admin and user.admin:
                return user
            else:
                raise HTTPException(403)

        except HTTPException:

            if request.method == "POST":  # If a post request, just return a 403 so there isn't a redirect
                raise HTTPException(403)
            else:  # Redirect to login if not logged in
                raise RequiresLoginException  # Defined in web_auth.py, handled on main.py

    return check_user_req


@lru_cache
def check_valid_api_key(level: AuthLevel) -> bool:
    """Check the api_key passed and determine if it is valid for the user in the request"""
    API_KEY_NAME = "key"
    api_key_query = APIKeyQuery(name=API_KEY_NAME, auto_error=False)
    api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

    # The nested function is so we can get the level from the function and still pass the request in
    def check_api_key(
        request: Request,
        api_key_query: str = Security(api_key_query),
        api_key_header: str = Security(api_key_header),
    ):

        key = api_key_header or api_key_query  # request.query_params["key"]
        if key is None:
            raise HTTPException(401)

        # if not request.query_params.get("key", False):
        #     # key paramater not specified
        #     raise HTTPException(403, "`key` parameter not passed")

        query = db.session.query(WebAuth).filter(WebAuth.api_key == key, WebAuth.enabled == True).one_or_none()  # noqa E712

        if query:
            if level == AuthLevel.admin and query.admin:
                return key
            elif level == AuthLevel.mod and any([query.admin, query.mod]):
                return key
            elif level == AuthLevel.user and any([query.admin, query.mod, query.user]):
                return key
            else:
                raise HTTPException(403)
        else:
            raise HTTPException(401)

    return check_api_key


def build_user(request: Request) -> dict:
    try:
        check_jwt_valid(request)
        encoded = request.cookies["_session"]
        user = jwt.decode(encoded, getenv("WEB_COOKIE_KEY"), algorithms="HS256")
    except HTTPException as e:
        raise HTTPException(e.status_code)

    query = db.session.query(WebAuth).filter(WebAuth.id == user["id"]).one_or_none()
    if query:
        user["enabled"] = query.enabled
        user["admin"] = query.admin
        user["mod"] = query.mod
        user["user"] = query.user

    # Convert the user id to an integer instead of a string
    user["id"] = int(user["id"])

    # Convert cookie expiration to datetime object
    user["expires"] = datetime.datetime.fromisoformat(user["expires"])

    new_user = munchify(user)
    return new_user


def check_jwt_valid(request: Request) -> dict:
    try:
        encoded = request.cookies["_session"]
        user = jwt.decode(encoded, getenv("WEB_COOKIE_KEY"), algorithms="HS256")

    except jwt.exceptions.InvalidSignatureError:
        # JWT decode key is most likely invalid
        raise HTTPException(500)

    except jwt.exceptions.DecodeError:
        # Modified JWT or no session cookie set
        raise HTTPException(401)

    except KeyError:
        raise HTTPException(401)

    except Exception as e:
        logger.warning(f"{type(e)} {e}")
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
    response = Response("Bye!", status_code=418)
    response.delete_cookie("_session")
    return response


# NOTE: REDIRECT_URI should be this path.
@router.get("/callback")
async def callback(request: Request, code: str):
    try:
        user = await webauth_client.login(code)
    except InvalidClientIdError:
        raise HTTPException(403)

    user["expires"] = str(datetime.datetime.now() + datetime.timedelta(seconds=cookie_life))
    encoded = jwt.encode(user, getenv("WEB_COOKIE_KEY"), algorithm="HS256")
    logger.info(f"    {user['username']} logged into webserver")

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
        logger.info(new_user)
        # Temporarily disabled intentionally
        # db.session.add(new_user)
        # db.session.commit()

    redirect_path = request.cookies.get("redirect", "/")
    response = RedirectResponse(redirect_path)
    response.delete_cookie("redirect")
    response.set_cookie("_session", encoded, max_age=cookie_life, secure=True, httponly=True)
    return response


@router.get("/user_data")
async def user_data(request: Request, user=Depends(check_user(level=AuthLevel.user))):
    return user
