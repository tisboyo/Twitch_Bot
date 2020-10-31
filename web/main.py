# import asyncio
from os import getenv

import uvicorn
from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import PlainTextResponse

app = FastAPI()
base_domain = getenv("WEB_HOSTNAME")


@app.on_event("startup")
async def startup_event():
    urls = [  # Format is Request, then fastapi path for Twitch to Post to.
        (  # User Follows
            "https://api.twitch.tv/helix/users/follows?first=1&to_id=461713054",
            "/twitch-webhook/follow",
        ),
    ]

    for url in urls:
        await subscribe(url)


async def subscribe(urls: tuple):
    # print(urls)
    post_url = f"{base_domain}{urls[1]}"
    print(urls[0], post_url)


@app.get("/")
def root():
    return {"Hello": "World"}


@app.get("/twitch-webhook/follow")
def twitch_webhook_follow_get(request: Request):
    params = dict(request.query_params)
    if params.get("hub.challenge", False):
        return PlainTextResponse(params["hub.challenge"])


@app.post("/twitch-webhook/follow")
def twitch_webhook_follow_post(body: dict):
    data = body["data"]
    print(data)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5000, ws="websockets", reload=True)
