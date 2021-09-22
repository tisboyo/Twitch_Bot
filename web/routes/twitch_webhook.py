import hmac
from hashlib import sha256
from os import getenv
from re import match

from fastapi import APIRouter
from fastapi import Request
from fastapi.exceptions import HTTPException
from fastapi.params import Depends
from fastapi.responses import PlainTextResponse
from fastapi.responses import Response
from fastapi_sqlalchemy import db
from send_to_bot import send_command_to_bot
from starlette import status as http_status

from models import IgnoreList

router = APIRouter()


def check_twitch_signature():
    """Checks the incoming signature on the header of the twitch message to verify it's authenticity"""
    signing_secret = getenv("TWITCH_SIGNING_SECRET")

    def check_signature(request: Request):
        message_signature = request.headers["Twitch-Eventsub-Message-Signature".lower()][
            7:
        ]  # Strip the sha256= off the front
        message_id = request.headers["Twitch-Eventsub-Message-Id".lower()]
        message_timestamp = request.headers["Twitch-Eventsub-Message-Timestamp".lower()]
        message_body = request._body.decode("utf-8")
        bmessage = bytes(message_id + message_timestamp + message_body, "utf-8")
        digested_message = hmac.new(bytes(signing_secret, "utf-8"), bmessage, sha256).hexdigest()

        valid = hmac.compare_digest(message_signature, digested_message)

        if not valid:
            raise HTTPException(http_status.HTTP_403_FORBIDDEN)
        else:
            return True

    return check_signature


@router.post("/twitch/eventsub/channel.follow")
async def twitch_eventsub_follow_post(data: dict, request: Request, signed=Depends(check_twitch_signature())):
    # Challenge is sent when the event is first setup only
    if data.get("challenge", False):
        return PlainTextResponse(data["challenge"])

    event_data = data["event"]

    # Check if the follower is in the ignore list
    # Load the ignore list from the database on startup
    ignore_list_patterns = dict()
    query = db.session.query(IgnoreList).filter(IgnoreList.enabled == True).all()  # noqa E712
    for each in query:
        ignore_list_patterns[each.id] = each.pattern

    # Check the ignore list to see if the user matches any of the requirements to be ignored
    for pattern in ignore_list_patterns.values():
        if match(pattern, event_data["user_name"]):
            # Ignore the user, still return 204 so twitch doesn't keep resending.
            return Response(status_code=http_status.HTTP_204_NO_CONTENT)

    # Send data to the twitchbot
    ret = await send_command_to_bot("follow", [event_data["user_name"]])
    return ret


@router.post("/twitch/eventsub/stream.online")
async def twitch_eventsub_stream_online_post(data: dict, request: Request, signed=Depends(check_twitch_signature())):
    # Challenge is sent when the event is first setup only
    if data.get("challenge", False):
        return PlainTextResponse(data["challenge"])

    event_data = data["event"]

    if event_data["broadcaster_user_login"] == getenv("TWITCH_CHANNEL"):
        ret = await send_command_to_bot("stream", ["live", "true"])
        await send_command_to_bot("wig", ["reset"])
        return ret
    else:
        return Response(status_code=http_status.HTTP_204_NO_CONTENT)


@router.post("/twitch/eventsub/stream.offline")
async def twitch_eventsub_stream_offline_post(data: dict, request: Request, signed=Depends(check_twitch_signature())):
    # Challenge is sent when the event is first setup only
    if data.get("challenge", False):
        return PlainTextResponse(data["challenge"])

    event_data = data["event"]

    if event_data["broadcaster_user_login"] == getenv("TWITCH_CHANNEL"):
        ret = await send_command_to_bot("stream", ["live", "false"])
        await send_command_to_bot("wig", ["reset"])
        return ret
    else:
        return Response(status_code=http_status.HTTP_204_NO_CONTENT)
