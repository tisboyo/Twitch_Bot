import asyncio
from os import getenv

import uvicorn
from fastapi import FastAPI
from fastapi.params import Depends
from fastapi.responses import FileResponse
from fastapi.responses import RedirectResponse
from fastapi_sqlalchemy import db
from fastapi_sqlalchemy import DBSessionMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from uvicorn.main import logger
from web_auth import AuthLevel
from web_auth import check_user
from web_auth import RequiresLoginException

from models import Settings

# noreorder
# Routes
from routes.announcements import router as announcements_router
from routes.commands import router as commands_router

# from routes.docs import router as docs_router
from routes.dropbox import router as dropbox_router
from routes.poll_display import router as poll_router
from routes.send_command import router as send_command_router
from routes.send_message import router as send_message_router
from routes.topic import router as topic_router
from routes.twitch_webhook import router as twitch_webhook_router
from routes.ignore import router as ignore_router
from routes.trivia import router as trivia_router
from web_auth import router as webauth_router
from routes.user_manage import router as user_manage_router
from routes.clips import router as clips_manage_router
from routes.auto_bahn import router as autoban_router
from routes.discord_webhooks import router as discord_webhooks_router
from routes.twitch_oauth import router as twitch_oauth_router
from routes.this_or_that import router as this_or_that_router


app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)


# Add Database handler
mysql_database = getenv("MYSQL_DATABASE")
mysql_user = getenv("MYSQL_USER")
mysql_pass = getenv("MYSQL_PASSWORD")
db_url = f"mysql+mysqlconnector://{mysql_user}:{mysql_pass}@mysql:3306/{mysql_database}"
app.add_middleware(DBSessionMiddleware, db_url=db_url)

# Include the routes
app.include_router(announcements_router)
app.include_router(commands_router)
# app.include_router(docs_router)
app.include_router(dropbox_router)
app.include_router(poll_router)
app.include_router(send_command_router)
app.include_router(send_message_router)
app.include_router(topic_router)
app.include_router(twitch_webhook_router)
app.include_router(ignore_router)
app.include_router(trivia_router)
app.include_router(webauth_router)
app.include_router(user_manage_router)
app.include_router(clips_manage_router)
app.include_router(autoban_router)
app.include_router(discord_webhooks_router)
app.include_router(twitch_oauth_router)
app.include_router(this_or_that_router)


@app.on_event("startup")
async def startup_event():
    loop = asyncio.get_running_loop()
    logger.info("Adding MOAR OHMS! ΩΩΩ")

    async def keep_database_alive():
        while True:
            with db():
                logger.info("Database keep alive running.")
                q = db.session.query(Settings).filter(Settings.key == "topic").one_or_none()
                if q:
                    logger.info(f"Current twitch topic: {q.value}")

                await asyncio.sleep(3600)

    loop.create_task(keep_database_alive())


@app.get("/")
def root(request: Request, user=Depends(check_user(level=AuthLevel.user))):
    return {"Hello": user.username}


@app.get("/favicon.ico")
def favicon():
    return FileResponse("static_files/favicon.ico")


@app.exception_handler(RequiresLoginException)
async def login_exception_handler(request: Request, exc: RequiresLoginException) -> RedirectResponse:
    """Sets a cookie for the url that made the request, and redirects to login"""
    response = RedirectResponse("/login")
    response.set_cookie(key="redirect", value=request.url.path, expires=180, secure=True, httponly=True)
    return response


app.add_middleware(SessionMiddleware, secret_key=getenv("SESSION_KEY"))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5000, ws="websockets", reload=True)
