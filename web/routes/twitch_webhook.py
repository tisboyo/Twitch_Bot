import json
from os import getenv
from re import match

import websockets
from fastapi import APIRouter
from fastapi import Request
from fastapi.exceptions import HTTPException
from fastapi.responses import PlainTextResponse
from fastapi.responses import Response
from fastapi_sqlalchemy import db
from signing import is_request_valid
from starlette.status import HTTP_204_NO_CONTENT

from models import IgnoreList

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

        # Load the ignore list from the database on startup
        ignore_list_patterns = dict()
        query = db.session.query(IgnoreList).filter(IgnoreList.enabled == True).all()  # noqa E712
        for each in query:
            ignore_list_patterns[each.id] = each.pattern

        # Check the ignore list to see if the user matches any of the requirements to be ignored
        for pattern in ignore_list_patterns.values():
            if match(pattern, data["from_name"]):
                # Ignore the user, still return 204 so twitch doesn't keep resending.
                return Response(status_code=HTTP_204_NO_CONTENT)

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


@router.get("/twitch-webhook/stream")
async def twitch_webhook_stream_get(request: Request):
    params = dict(request.query_params)
    if params.get("hub.challenge", False):
        return PlainTextResponse(params["hub.challenge"])


@router.post("/twitch-webhook/stream")
async def twitch_webhook_stream_post(data: dict, request: Request):
    """
    {
    "data": [
        {
        "id": "0123456789",
        "user_id": "5678",
        "user_name": "wjdtkdqhs",
        "game_id": "21779",
        "community_ids": [],
        "type": "live",
        "title": "Best Stream Ever",
        "viewer_count": 417,
        "started_at": "2017-12-01T10:09:45Z",
        "language": "en",
        "thumbnail_url": "https://link/to/thumbnail.jpg"
        }
    ]
    }
    """

    if await is_request_valid(request):
        if len(data["data"]) > 0:
            data = data["data"][0]
            live = "true" if data.get("type", False) == "live" else "false"
        else:
            live = "false"

        uri = "ws://bot:13337"
        try:
            async with websockets.connect(uri) as s:
                # We don't actually need this, but we have to read it before the bot will accept commands
                await s.recv()
                # There are two entries returned, and we need to return both
                await s.recv()

                # Define the messages to send
                going_live_msg = dict(
                    type="run_command",
                    command="stream",
                    channel=getenv("TWITCH_CHANNEL"),
                    args=["live", live],
                )
                # Combine to an interable and loop over them
                messages = list()
                if live == "true":
                    # Commands sent when going live
                    messages.append(going_live_msg)
                else:
                    # Commands sent when going offline
                    messages.append(going_live_msg)

                for msg in messages:
                    await s.send((json.dumps(msg) + "\n").encode("utf8"))

                    # Check if the message was successful
                    resp = json.loads(await s.recv())
                    if resp.get("type", "fail") != "success":
                        raise HTTPException(status_code=503)

                # 204 is a No Content status code
                return Response(status_code=HTTP_204_NO_CONTENT)

        except ConnectionRefusedError:
            print("Unable to connect to bot for stream status change")
            raise HTTPException(status_code=503)

        except Exception as e:
            print(f"Unknown exception trying to send message to bot. {e}")
            raise HTTPException(status_code=503)
