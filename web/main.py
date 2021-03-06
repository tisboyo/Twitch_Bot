import asyncio
from os import getenv

import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi_sqlalchemy import db
from fastapi_sqlalchemy import DBSessionMiddleware
from uvicorn.main import logger

from models import Settings

# noreorder
# Routes
from routes.announcements import router as announcements_router
from routes.commands import router as commands_router
from routes.docs import router as docs_router
from routes.dropbox import router as dropbox_router
from routes.poll_display import router as poll_router
from routes.send_command import router as send_command_router
from routes.send_message import router as send_message_router
from routes.topic import router as topic_router
from routes.twitch_webhook import router as twitch_webhook_router
from routes.ignore import router as ignore_router
from routes.trivia import router as trivia_router

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
app.include_router(docs_router)
app.include_router(dropbox_router)
app.include_router(poll_router)
app.include_router(send_command_router)
app.include_router(send_message_router)
app.include_router(topic_router)
app.include_router(twitch_webhook_router)
app.include_router(ignore_router)
app.include_router(trivia_router)


@app.on_event("startup")
async def startup_event():
    loop = asyncio.get_running_loop()
    logger.info("Adding MOAR OHMS! ΩΩΩ")

    async def keep_database_alive():
        while True:
            with db():
                logger.info("Database keep alive running.")
                q = db.session.query(Settings).filter(Settings.key == "topic").one_or_none()
                logger.info(f"Current twitch topic: {q.value}")

                await asyncio.sleep(3600)

    loop.create_task(keep_database_alive())


# @app.get("/")
# def root():
#     return {"Hello": "World"}


@app.get("/favicon.ico")
def favicon():
    return FileResponse("static_files/favicon.ico")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5000, ws="websockets", reload=True)
