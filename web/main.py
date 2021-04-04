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
import routes.announcements
import routes.commands
import routes.docs
import routes.dropbox
import routes.poll_display
import routes.send_command
import routes.send_message
import routes.topic
import routes.twitch_webhook
import routes.ignore
import routes.trivia

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

# Add Database handler
mysql_database = getenv("MYSQL_DATABASE")
mysql_user = getenv("MYSQL_USER")
mysql_pass = getenv("MYSQL_PASSWORD")
db_url = f"mysql+mysqlconnector://{mysql_user}:{mysql_pass}@mysql:3306/{mysql_database}"
app.add_middleware(DBSessionMiddleware, db_url=db_url)

# Include the routes
app.include_router(routes.announcements.router)
app.include_router(routes.twitch_webhook.router)
app.include_router(routes.send_message.router)
app.include_router(routes.docs.router)
app.include_router(routes.commands.router)
app.include_router(routes.poll_display.router)
app.include_router(routes.dropbox.router)
app.include_router(routes.topic.router)
app.include_router(routes.send_command.router)
app.include_router(routes.ignore.router)
app.include_router(routes.trivia.router)


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
