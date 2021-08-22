import json
from os import getenv

import websockets
from fastapi import APIRouter
from fastapi.params import Body
from fastapi.params import Depends
from fastapi.responses import JSONResponse
from web_auth import AuthLevel
from web_auth import check_valid_api_key

router = APIRouter()


@router.post("/post_message")
async def post_message(
    body: dict = Body(..., example={"message": "Post your message here, it will be relayed to twitch chat"}),
    api_key=Depends(check_valid_api_key(level=AuthLevel.admin)),
):
    """Manual testing
    curl --header "Content-Type: application/json" --header "key: testKey" --request POST --data '{"message":"Test message sent from a json post"}' http://localhost:5000/post_message
    curl --header "Content-Type: application/json" --request POST --data '{"message":"Test"}' http://localhost:5000/post_message?key=testKey
    """  # noqa E501
    if body.get("message", False):
        uri = "ws://bot:13337"
        try:
            async with websockets.connect(uri) as s:

                # We don't actually need this, but we have to read it before the bot will accept commands
                await s.recv()

                # There are two entries returned, and we need to retrieve both
                await s.recv()

                msg = dict(
                    type="send_privmsg",
                    channel=getenv("TWITCH_CHANNEL"),
                    message=f"🤖 {body['message']}",
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
