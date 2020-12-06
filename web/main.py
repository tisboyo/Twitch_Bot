# import asyncio
from os import getenv

import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from routes import announcements
from routes import docs
from routes import send_message
from routes import twitch_webhook_follow

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
base_domain = getenv("WEB_HOSTNAME")

app.include_router(announcements.router)
app.include_router(twitch_webhook_follow.router)
app.include_router(send_message.router)
app.include_router(docs.router)


@app.on_event("startup")
async def startup_event():
    pass


@app.get("/")
def root():
    return {"Hello": "World"}


@app.get("/favicon.ico")
def favicon():
    return FileResponse("static_files/favicon.ico")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5000, ws="websockets", reload=True)
