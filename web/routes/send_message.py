import socket
from os import getenv

from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from fastapi.params import Body
from fastapi.params import Depends
from fastapi.params import Security
from fastapi.responses import JSONResponse
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_401_UNAUTHORIZED

router = APIRouter()

API_KEY = getenv("WEB_API_KEY")
API_KEY_NAME = "access_token"

api_key_header = APIKeyHeader(name=API_KEY_NAME)


async def check_for_valid_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == API_KEY:
        return True
    else:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)


@router.post("/post_message")
async def post_message(
    body: dict = Body(..., example={"message": "Post your message here, it will be relayed to twitch chat"}),
    authorized: bool = Depends(check_for_valid_api_key),
):
    if body.get("message", False):
        try:
            s = socket.socket()
            s.connect(("bot", 13337))

            # We don't actually need this, but we have to read it before the bot will accept commands
            s.recv(300).decode("utf8")

            # Send the channel that we are connecting to
            s.send(f"{getenv('TWITCH_CHANNEL')}\n".encode("utf8"))
            s.send(f"🤖 {body['message']}\n".encode("utf8"))

            # Close the socket
            s.shutdown(socket.SHUT_RD)
            return JSONResponse({"success": True})

        except ConnectionRefusedError:
            print("Unable to connect to bot.")
            return JSONResponse({"success": False, "detail": "Unable to connect to bot."})

        except Exception as e:
            print(f"Unknown exception trying to send message to bot. {e}")
            return JSONResponse({"success": False, "detail": e})
