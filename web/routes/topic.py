import json
from os import getenv

import websockets
from fastapi import APIRouter
from fastapi.params import Body
from fastapi.params import Depends
from fastapi.responses import JSONResponse
from fastapi_sqlalchemy import db
from starlette.requests import Request
from web_auth import AuthLevel
from web_auth import check_user
from web_auth import check_valid_api_key

from models import Settings

router = APIRouter()


@router.get("/topic")
async def get_topic(request: Request, user=Depends(check_user(level=AuthLevel.admin))):
    topic = db.session.query(Settings).filter(Settings.key == "topic").one_or_none()
    topic = topic.value  # type: ignore
    db.session.commit()  # Required so the object updates and gets new data on the next run.
    return JSONResponse({"topic": topic})


@router.post("/topic")
async def post_topic(
    body: dict = Body(..., example={"message": "Post your message here, it will be relayed to twitch chat"}),
    api_key=Depends(check_valid_api_key(level=AuthLevel.admin)),
):
    """Manual testing
    curl --header "Content-Type: application/json" --header "access_token: testKey" --request POST --data '{"topic":"Test topic sent from a json post"}' http://localhost:5000/topic
    curl --header "Content-Type: application/json" --request POST --data '{"topic":"Test"}' http://localhost:5000/topic?access_token=testKey
    """  # noqa E501
    if body.get("topic", False):
        uri = "ws://bot:13337"
        try:
            async with websockets.connect(uri) as s:

                # We don't actually need this, but we have to read it before the bot will accept commands
                await s.recv()

                # There are two entries returned, and we need to retrieve both
                await s.recv()

                topic = f"set {body['topic']}".split()  # 'set' is the subcommand and needs to be sent as part of the args
                msg = dict(
                    type="run_command",
                    command="!topic",
                    channel=getenv("TWITCH_CHANNEL"),
                    args=topic,
                    silent=True,
                )
                msg_txt = json.dumps(msg) + "\n"
                await s.send(msg_txt.encode("utf8"))
                await s.send("\n".encode("utf8"))
                # Check if the message was successful
                resp = json.loads(await s.recv())
                print(resp)
                if resp.get("type", "fail") != "success":
                    return JSONResponse({"success": False, "detail": "Error sending bot message."})

                return JSONResponse({"success": True})

        except ConnectionRefusedError:
            print("Unable to connect to bot.")
            return JSONResponse({"success": False, "detail": "Unable to connect to bot."})

        except Exception as e:
            print(f"Unknown exception trying to send message to bot. {e}")
            return JSONResponse({"success": False, "detail": str(e)})
