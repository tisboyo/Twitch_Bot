import json
import socket
from os import getenv

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

# api_key_header = APIKeyHeader(name=API_KEY_NAME)


# async def check_for_valid_api_key(api_key_header: str = Security(api_key_header)):
#     if api_key_header == API_KEY:
#         return api_key_header
#     else:
#         raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)


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
    if body.get("message", False):
        try:
            s = socket.socket()
            # s.settimeout(0.25)
            s.connect(("bot", 13337))

            # We don't actually need this, but we have to read it before the bot will accept commands
            print(s.recv(300))

            # There are two entries returned, and we need to retrieve both
            print(s.recv(300))

            msg = dict(
                type="send_privmsg",
                channel=getenv("TWITCH_CHANNEL"),
                message=f"🤖 {body['message']}",
            )
            msg_txt = json.dumps(msg) + "\n"
            s.send(msg_txt.encode("utf8"))
            s.send("\n".encode("utf8"))
            # Check if the message was successful
            resp = json.loads(s.recv(300))
            print(resp)
            if resp.get("type", "fail") != "success":
                return JSONResponse({"success": False, "detail": "Error sending bot message."})

            # Close the socket
            s.shutdown(socket.SHUT_RD)
            return JSONResponse({"success": True})

        except ConnectionRefusedError:
            print("Unable to connect to bot.")
            return JSONResponse({"success": False, "detail": "Unable to connect to bot."})

        except Exception as e:
            print(f"Unknown exception trying to send message to bot. {e}")
            return JSONResponse({"success": False, "detail": str(e)})
