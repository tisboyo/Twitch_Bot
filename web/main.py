from os import getenv

import uvicorn
from easyauth.client import EasyAuthClient
from easyauth.server import EasyAuthServer
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi_sqlalchemy import DBSessionMiddleware
from uvicorn.main import logger


app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)


# Add Database handler
mysql_database = getenv("MYSQL_DATABASE")
mysql_user = getenv("MYSQL_USER")
mysql_pass = getenv("MYSQL_PASSWORD")
db_url = f"mysql+mysqlconnector://{mysql_user}:{mysql_pass}@mysql:3306/{mysql_database}"
app.add_middleware(DBSessionMiddleware, db_url=db_url)


@app.on_event("startup")
async def startup_event():
    # loop = asyncio.get_running_loop()
    logger.info("Adding MOAR OHMS! ΩΩΩ")
    # Start the authorization server
    await EasyAuthServer.create(app, "/auth/token", logger=logger)

    # Handle for the authorization client
    app.auth_client = await EasyAuthClient.create(app, "/auth/token", logger=logger, debug=True)

    # Include the routes
    # app.include_router(docs_router)
    # app.include_router(send_command_router)
    # app.include_router(send_message_router)
    # app.include_router(topic_router)

    # Routers for authenticated
    announcements_router = app.auth_client.create_api_router(prefix="/announcements")
    apikey_router = app.auth_client.create_api_router(prefix="/keys")
    commands_router = app.auth_client.create_api_router(prefix="/commands")
    dropbox_router = app.auth_client.create_api_router(prefix="/dropbox")
    ignore_router = app.auth_client.create_api_router(prefix="/ignore")
    poll_router = app.auth_client.create_api_router(prefix="/poll")

    # Authenticated routes
    from routes.announcements import setup as announcements_setup
    from routes.apikeys import setup as apikeys_setup
    from routes.commands import setup as commands_setup
    from routes.dropbox import setup as dropbox_setup
    from routes.ignore import setup as ignore_setup
    from routes.poll_display import setup as poll_setup

    # Run setups for each authenticated route
    await announcements_setup(announcements_router)
    await apikeys_setup(apikey_router)
    await commands_setup(commands_router)
    await dropbox_setup(dropbox_router)
    await ignore_setup(ignore_router)
    await poll_setup(poll_router)

    # Public Routes
    from routes.dropbox import router as dropbox_router
    from routes.poll_display import router as poll_router
    from routes.trivia import router as trivia_router
    from routes.twitch_webhook import router as twitch_router

    # Include public routes
    app.include_router(dropbox_router)
    app.include_router(poll_router)
    app.include_router(trivia_router)
    app.include_router(twitch_router)


@app.get("/favicon.ico")
def favicon():
    return FileResponse("static_files/favicon.ico")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5000, ws="websockets", reload=True)
