from os import getenv

from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from fastapi.responses import Response
from fastapi.templating import Jinja2Templates
from send_to_bot import send_command_to_bot
from starlette.requests import Request
from starlette.responses import FileResponse
from starlette.responses import JSONResponse


router = APIRouter()

web_api_key = getenv("WEB_API_KEY")
templates = Jinja2Templates(directory="static_files/trivia")


@router.get("/trivia/q")
async def trivia_q(request: Request, key: str = None):
    if key != web_api_key:
        return Response(status_code=403)

    jsonret = {
        "text": "What fictional device enables time travel?",
        "answers": {
            "4": {"text": "Warp Core", "is_answer": 0},
            "1": {"text": "Flux Capacitor", "is_answer": 1},
            "3": {"text": "Reluctance Inductor", "is_answer": 0},
            "2": {"text": "A Key", "is_answer": 0},
        },
        "explain": "Back to the Future established that with 1.21 GW the Flux Capacitor is what makes time travel possible.",
        "last_used_date": "",
        "created_date": "2019-11-24",
        "created_by": "baldengineer",
        "reference": "",
    }

    question = 16
    answer = 2

    try:
        await send_command_to_bot("trivia", ["q", question, answer])
    except HTTPException:
        return JSONResponse(
            {
                "text": "Unable to connect to TwitchBot for Trivia",
                "answers": {
                    "1": {"text": "Fire Tisboyo."},
                    "2": {"text": "Sacrifice some Ohms to the bot gods."},
                    "3": {"text": "Kick AWS for breaking the bot."},
                    "4": {"text": "Did the Twitch API key expire again?"},
                },
                "explain": "Lets try again and see if it wakes up this time.",
            }
        )

    return JSONResponse(jsonret)


@router.post("/trivia/end")
async def trivia_end(key: str = None):
    if key != web_api_key:
        return Response(status_code=403)

    print("end trivia")


# Static file returns
@router.get("/trivia")
async def trivia_index(request: Request, key: str = None):
    if key != web_api_key:
        return Response(status_code=403)

    return templates.TemplateResponse("index.html", {"request": request, "key": key})


@router.get("/trivia/trivia.js")
async def trivia_js(request: Request, key: str = None):
    if key != web_api_key:
        return Response(status_code=403)

    return FileResponse("static_files/trivia/trivia.js")


@router.get("/trivia/trivia.css")
async def trivia_css(request: Request):
    return FileResponse("static_files/trivia/trivia.css")


@router.get("/trivia/laptop-background-transparent.png")
async def trivia_background(request: Request, key: str = None):
    if key != web_api_key:
        return Response(status_code=403)

    return FileResponse("static_files/trivia/laptop-background-transparent.png")
