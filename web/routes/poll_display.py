from os import getenv

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from fastapi.responses import FileResponse
from starlette.responses import RedirectResponse
from web_auth import AuthLevel
from web_auth import check_user

router = APIRouter()


@router.get("/obs_poll")
async def get_obs_poll(
    request: Request,
    user=Depends(check_user(level=AuthLevel.mod)),
):
    mqtt_user = getenv("MQTT_USER")
    mqtt_pass = getenv("MQTT_KEY")

    url = (
        f"{request.base_url}poll-display?"
        f"url={request.base_url.hostname}&"
        "port=9883&"
        f"username={mqtt_user}&"
        f"password={mqtt_pass}"
    )

    return RedirectResponse(url)


@router.get("/poll-display", response_class=FileResponse)
async def get_poll_display(request: Request):
    return FileResponse("static_files/poll/poll-display.html")


@router.get("/poll.css", response_class=FileResponse)
async def get_poll_css(request: Request):
    return FileResponse("static_files/poll/poll.css")


@router.get("/poll-mqtt-source.js", response_class=FileResponse)
async def get_mqtt_source_js(request: Request):
    return FileResponse("static_files/poll/poll-mqtt-source.js")


@router.get("/mononoki-Regular.woff2", response_class=FileResponse)
async def get_mononoki(request: Request):
    return FileResponse("static_files/mononoki-Regular.woff2")
