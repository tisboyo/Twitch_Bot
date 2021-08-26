from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import FileResponse

router = APIRouter()


@router.get("/trivia-answer-display", response_class=FileResponse)
async def get_poll_display(request: Request):
    return FileResponse("static_files/trivia_answer/trivia-answer-display.html")


@router.get("/trivia-answer.css", response_class=FileResponse)
async def get_poll_css(request: Request):
    return FileResponse("static_files/trivia_answer/trivia-answer.css")


@router.get("/poll-mqtt-source.js", response_class=FileResponse)
async def get_mqtt_source_js(request: Request):
    return FileResponse("static_files/trivia_answer/trivia-answer-mqtt-source.js")
