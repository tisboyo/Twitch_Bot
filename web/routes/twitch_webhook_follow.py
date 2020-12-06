import socket
from os import getenv

from fastapi import APIRouter
from fastapi import Request
from fastapi.exceptions import HTTPException
from fastapi.responses import PlainTextResponse

router = APIRouter()


@router.get("/twitch-webhook/follow")
async def twitch_webhook_follow_get(request: Request):
    params = dict(request.query_params)
    if params.get("hub.challenge", False):
        return PlainTextResponse(params["hub.challenge"])


@router.post("/twitch-webhook/follow")
async def twitch_webhook_follow_post(body: dict):
    # [{'followed_at': '', 'from_id': '',
    # 'from_name': '', 'to_id': '', 'to_name': ''}]
    data = body["data"][0]

    if data.get("from_name", False):
        try:
            s = socket.socket()
            s.connect(("bot", 13337))

            # We don't actually need this, but we have to read it before the bot will accept commands
            s.recv(300).decode("utf8")

            # Send the channel that we are connecting to
            s.send(f"{getenv('TWITCH_CHANNEL')}\n".encode("utf8"))
            s.send(f"🤖 Thanks for the follow @{data['from_name']}\n".encode("utf8"))

            # Close the socket
            s.shutdown(socket.SHUT_RD)
        except ConnectionRefusedError:
            print("Unable to connect to bot for new follow.")
            raise HTTPException(status_code=503)

        except Exception as e:
            print(f"Unknown exception trying to send new follow to bot. {e}")
            raise HTTPException(status_code=503)
