from os import getenv

from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import FileResponse
from starlette.responses import RedirectResponse

router = APIRouter()


@router.get("/trivia/results_obs")
async def get_obs_poll(request: Request):
    mqtt_user = getenv("MQTT_USER")
    mqtt_pass = getenv("MQTT_KEY")

    url = (
        f"{request.base_url}trivia/results?"
        f"url={request.base_url.hostname}&"
        "port=9883&"
        f"username={mqtt_user}&"
        f"password={mqtt_pass}"
    )

    return RedirectResponse(url)


@router.get("/trivia/results", response_class=FileResponse)
async def get_poll_display(request: Request):
    return FileResponse("static_files/trivia_display/trivia_display.html")


@router.get("/trivia/trivia_display.css", response_class=FileResponse)
async def get_poll_css(request: Request):
    return FileResponse("static_files/trivia_display/trivia_display.css")


@router.get("/trivia/trivia_mqtt.js", response_class=FileResponse)
async def get_mqtt_source_js(request: Request):
    return FileResponse("static_files/trivia_display/trivia_mqtt.js")


@router.get("/trivia/mononoki-Regular.woff2", response_class=FileResponse)
async def get_mononoki(request: Request):
    return FileResponse("static_files/mononoki-Regular.woff2")
