import json
from os import getenv

import websockets
from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from fastapi.params import Body
from fastapi.params import Depends
from fastapi.params import Security
from fastapi.responses import JSONResponse
from fastapi.security.api_key import APIKey
from fastapi.security.api_key import APIKeyCookie
from fastapi.security.api_key import APIKeyHeader
from fastapi.security.api_key import APIKeyQuery
from starlette.status import HTTP_401_UNAUTHORIZED

router = APIRouter()

API_KEY = getenv("WEB_API_KEY")
API_KEY_NAME = "access_token"


api_key_query = APIKeyQuery(name=API_KEY_NAME, auto_error=False)
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
api_key_cookie = APIKeyCookie(name=API_KEY_NAME, auto_error=False)


async def get_api_key(
    api_key_query: str = Security(api_key_query),
    api_key_header: str = Security(api_key_header),
    api_key_cookie: str = Security(api_key_cookie),
):
    if api_key_query == API_KEY:
        return api_key_query
    elif api_key_header == API_KEY:
        return api_key_header
    elif api_key_cookie == API_KEY:
        return api_key_cookie
    else:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")


@router.post("/post_message")
async def post_message(
    body: dict = Body(..., example={"message": "Post your message here, it will be relayed to twitch chat"}),
    api_key: APIKey = Depends(get_api_key),
):
    """Manual testing
    curl --header "Content-Type: application/json" --header "access_token: testKey" --request POST --data '{"message":"Test message sent from a json post"}' http://localhost:5000/post_message
    curl --header "Content-Type: application/json" --request POST --data '{"message":"Test"}' http://localhost:5000/post_message?access_token=testKey
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
