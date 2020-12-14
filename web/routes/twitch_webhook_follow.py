import json
import socket
from os import getenv

from fastapi import APIRouter
from fastapi import Request
from fastapi.exceptions import HTTPException
from fastapi.responses import PlainTextResponse
from signing import is_request_valid

router = APIRouter()


@router.get("/twitch-webhook/follow")
async def twitch_webhook_follow_get(request: Request):
    params = dict(request.query_params)
    if params.get("hub.challenge", False):
        return PlainTextResponse(params["hub.challenge"])


@router.post("/twitch-webhook/follow")
async def twitch_webhook_follow_post(data: dict, request: Request):
    # [{'followed_at': '', 'from_id': '',
    # 'from_name': '', 'to_id': '', 'to_name': ''}]

    if await is_request_valid(request):
        data = data["data"][0]
        try:
            s = socket.socket()
            s.connect(("bot", 13337))

            # We don't actually need this, but we have to read it before the bot will accept commands
            s.recv(300).decode("utf8")
            # There are two entries returned, and we need to return both
            s.recv(300).decode("utf8")

            msg = dict(
                type="send_privmsg",
                channel=getenv("TWITCH_CHANNEL"),
                message=f"🤖 Thanks for the follow {data['from_name']}",
            )
            s.send((json.dumps(msg) + "\n").encode("utf8"))

            # Check if the message was successful
            resp = json.loads(s.recv(300))
            if resp.get("type", "fail") != "success":
                raise HTTPException(status_code=503)

            # Close the socket
            s.shutdown(socket.SHUT_RD)
        except ConnectionRefusedError:
            print("Unable to connect to bot for new follow.")
            raise HTTPException(status_code=503)

        except Exception as e:
            print(f"Unknown exception trying to send message to bot. {e}")
            raise HTTPException(status_code=503)
