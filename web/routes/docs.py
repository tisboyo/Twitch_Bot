import base64
from datetime import timedelta
from os import getenv

from auth import ACCESS_TOKEN_EXPIRE_MINUTES
from auth import authenticate_user
from auth import basic_auth
from auth import BasicAuth
from auth import create_access_token
from auth import get_current_active_user
from auth import Token
from auth import User
from auth import users_db
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.params import Depends
from fastapi.routing import APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from starlette.responses import JSONResponse
from starlette.responses import RedirectResponse
from starlette.responses import Response

router = APIRouter()


@router.post("/token", response_model=Token)
async def route_login_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/logout")
async def route_logout_and_remove_cookie():
    response = RedirectResponse(url="/")
    response.delete_cookie("Authorization", domain=getenv("WEB_HOSTNAME"))
    return response


@router.get("/login")
async def login_basic(auth: BasicAuth = Depends(basic_auth)):
    if not auth:
        response = Response(headers={"WWW-Authenticate": "Basic"}, status_code=401)
        return response

    try:
        decoded = base64.b64decode(auth).decode("ascii")
        username, _, password = decoded.partition(":")
        user = authenticate_user(users_db, username, password)
        if not user:
            raise HTTPException(status_code=400, detail="Incorrect email or password")

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"sub": username}, expires_delta=access_token_expires)

        token = jsonable_encoder(access_token)

        response = RedirectResponse(url="/docs")
        response.set_cookie(
            "Authorization",
            value=f"Bearer {token}",
            domain=getenv("WEB_HOSTNAME"),
            httponly=True,
            max_age=1800,
            expires=1800,
        )
        return response

    except Exception:
        response = Response(headers={"WWW-Authenticate": "Basic"}, status_code=401)
        return response


@router.get("/openapi.json")
async def get_open_api_endpoint(current_user: User = Depends(get_current_active_user)):
    return JSONResponse(get_openapi(title="FastAPI", version=1, routes=router.routes))


@router.get("/docs")
async def get_documentation(current_user: User = Depends(get_current_active_user)):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")
