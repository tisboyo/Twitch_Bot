import json
from datetime import date
from os import getenv
from random import shuffle

from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from fastapi.responses import Response
from fastapi.templating import Jinja2Templates
from fastapi_sqlalchemy import db
from send_to_bot import send_command_to_bot
from sqlalchemy import func
from starlette.requests import Request
from starlette.responses import FileResponse
from starlette.responses import JSONResponse

from models import TriviaQuestions

router = APIRouter()

web_api_key = getenv("WEB_API_KEY")
templates = Jinja2Templates(directory="static_files/trivia")


@router.get("/trivia/q")
async def trivia_q(request: Request, key: str = None):
    if key != web_api_key:
        return Response(status_code=403)

    question = (
        db.session.query(TriviaQuestions)
        .filter(TriviaQuestions.last_used_date < date.today())
        .order_by(func.random())
        .limit(1)
        .one_or_none()
    )

    if not question:  # The query returned None
        print("We have used all of the trivia questions today!")
        return JSONResponse(
            {
                "text": "We've used ALL of the trivia questions today.",
            }
        )

    # Randomize answers, generate a new number order of indexes
    ans = json.loads(question.answers)
    ln = len(ans)
    new_order = [idx for idx in range(1, ln + 1)]
    shuffle(new_order)

    # Assign the new random indexes to the question text
    randomized_answers = dict()
    temp_counter = 0
    for k in ans:
        randomized_answers[str(new_order[temp_counter])] = ans[k]
        temp_counter += 1

    # Grab the correct answer from the new order
    answer_id = -1
    for a in randomized_answers:
        if bool(randomized_answers[a]["is_answer"]):
            answer_id = int(a)
            break

    # Build the json to return to the browser.
    jsonret = {
        "text": question.text,
        "answers": randomized_answers,
        "explain": question.explain,
    }

    try:
        # Send the question to TwitchBot
        await send_command_to_bot("trivia", ["q", question.id, answer_id])
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
