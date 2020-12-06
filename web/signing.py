import hmac
from hashlib import sha256
from os import getenv

from fastapi import Request


async def is_request_valid(request: Request) -> bool:
    body = await request.body()
    key = getenv("TWITCH_SIGNING_SECRET")

    x_hub_signature = request.headers["x-hub-signature"].replace("sha256=", "")

    body_signed = hmac.new(key.encode("utf-8"), msg=body, digestmod=sha256).hexdigest()

    return body_signed == x_hub_signature
