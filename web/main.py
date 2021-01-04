# import asyncio
import asyncio
from os import getenv

import uvicorn
from db import session
from fastapi import FastAPI
from fastapi.responses import FileResponse
from routes import announcements
from routes import commands
from routes import docs
from routes import dropbox
from routes import send_message
from routes import topic
from routes import twitch_webhook_follow
from uvicorn.main import logger

from models import Settings

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
base_domain = getenv("WEB_HOSTNAME")

app.include_router(announcements.router)
app.include_router(twitch_webhook_follow.router)
app.include_router(send_message.router)
app.include_router(docs.router)
app.include_router(commands.router)
app.include_router(dropbox.router)
app.include_router(topic.router)


@app.on_event("startup")
async def startup_event():
    loop = asyncio.get_running_loop()

    async def keep_database_alive():
        while True:
            logger.info("Database keep alive running.")
            q = session.query(Settings).filter(Settings.key == "topic").one_or_none()
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
