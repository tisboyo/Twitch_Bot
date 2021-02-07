import json
from os import getenv
from re import match

import websockets
from fastapi import APIRouter
from fastapi import Request
from fastapi.exceptions import HTTPException
from fastapi.responses import PlainTextResponse
from fastapi.responses import Response
from signing import is_request_valid
from starlette.status import HTTP_204_NO_CONTENT

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

        if match("heder[0-9]{6}", data["from_name"]):
            # Ignore the spam follow bot
            return

        uri = "ws://bot:13337"
        try:
            async with websockets.connect(uri) as s:
                # We don't actually need this, but we have to read it before the bot will accept commands
                await s.recv()
                # There are two entries returned, and we need to return both
                await s.recv()

                msg = dict(
                    type="send_privmsg",
                    channel=getenv("TWITCH_CHANNEL"),
                    message=f"🤖 Thanks for the follow {data['from_name']}",
                )
                await s.send((json.dumps(msg) + "\n").encode("utf8"))

                # Check if the message was successful
                resp = json.loads(await s.recv())
                if resp.get("type", "fail") != "success":
                    raise HTTPException(status_code=503)

                # 204 is a No Content status code
                return Response(status_code=HTTP_204_NO_CONTENT)

        except ConnectionRefusedError:
            print("Unable to connect to bot for new follow.")
            raise HTTPException(status_code=503)

        except Exception as e:
            print(f"Unknown exception trying to send message to bot. {e}")
            raise HTTPException(status_code=503)
