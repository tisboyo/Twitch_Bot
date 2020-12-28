from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import FileResponse

router = APIRouter()


@router.get("/poll-display", response_class=FileResponse)
async def get_poll_display(request: Request):
    return FileResponse("static_files/poll-display.html")


@router.get("/poll-display.js", response_class=FileResponse)
async def get_poll_js(request: Request):
    return FileResponse("static_files/poll-display.js")
