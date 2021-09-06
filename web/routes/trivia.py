import json
from datetime import date
from os import getenv
from pathlib import Path

from fastapi import APIRouter
from fastapi.datastructures import UploadFile
from fastapi.params import Depends
from fastapi.params import File
from fastapi.requests import Request
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse
from fastapi.responses import RedirectResponse
from fastapi.responses import Response
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi_sqlalchemy import db
from send_to_bot import send_command_to_bot
from uvicorn.main import logger
from web_auth import AuthLevel
from web_auth import check_user
from web_auth import check_valid_api_key

from models import TriviaQuestions


router = APIRouter()

templates = Jinja2Templates(directory="static_files/trivia")

# /trivia/play Load this to play trivia in OBS


@router.get("/trivia/play")
async def trivia_new(
    request: Request,
    key=Depends(check_valid_api_key(level=AuthLevel.admin)),
):
    mqtt_user = getenv("MQTT_USER")
    mqtt_pass = getenv("MQTT_KEY")

    url = (
        f"{request.base_url}trivia/play.html?"
        f"url={request.base_url.hostname}&"
        "port=9883&"
        f"username={mqtt_user}&"
        f"password={mqtt_pass}&"
        f"key={key}"
    )

    return RedirectResponse(url)


@router.get("/trivia/play.html")
async def trivia_play(request: Request, key: str = Depends(check_valid_api_key(level=AuthLevel.admin))):
    return templates.TemplateResponse("play.html", {"request": request, "key": key})


@router.get("/trivia/play.js")
async def trivia_play_js(request: Request, key: str = Depends(check_valid_api_key(level=AuthLevel.admin))):
    return FileResponse("static_files/trivia/play.js")


@router.get("/trivia/play.css")
async def trivia_play_css(request: Request):
    return FileResponse("static_files/trivia/play.css")


@router.get("/trivia/sounds/{sound_id}")
async def trivia_play_wav(
    request: Request, key: str = Depends(check_valid_api_key(level=AuthLevel.admin)), sound_id="default"
):
    def iterfile():

        audio_file_path = Path(__file__).resolve().parent / ".." / "static_files" / "trivia" / "sounds"
        question_file = audio_file_path / f"{sound_id}.wav"
        default_file = audio_file_path / "default.wav"
        if question_file.is_file():
            audio_file = question_file
        else:
            audio_file = default_file

        with open(audio_file, mode="rb") as file_like:
            yield from file_like

    return StreamingResponse(iterfile(), media_type="audio/wav")


@router.get("/trivia/images/{image_id}")
async def trivia_play_jpg(
    request: Request, key: str = Depends(check_valid_api_key(level=AuthLevel.admin)), image_id="default"
):
    image_file_path = Path(__file__).resolve().parent / ".." / "static_files" / "trivia" / "images"
    question_file_jpg = image_file_path / f"{image_id}.jpg"
    question_file_png = image_file_path / f"{image_id}.png"
    question_file_gif = image_file_path / f"{image_id}.gif"
    default_file = image_file_path / "default.png"

    if question_file_jpg.is_file():
        return FileResponse(question_file_jpg)
    elif question_file_png.is_file():
        return FileResponse(question_file_png)
    elif question_file_gif.is_file():
        return FileResponse(question_file_gif)
    else:
        # return Response(None, status_code=204)
        return FileResponse(default_file)


@router.get("/trivia/start")
async def trivia_start(request: Request, key: str = Depends(check_valid_api_key(level=AuthLevel.admin)), debug: str = "0"):
    logger.info("Trivia started")
    if debug.lower() == "true":
        debug = "1"
    return await send_command_to_bot("trivia", ["start", debug])


@router.post("/trivia/end")
async def trivia_end(request: Request, key: str = Depends(check_valid_api_key(level=AuthLevel.admin))):
    logger.info("Trivia ended")
    return await send_command_to_bot("trivia", ["end"])


@router.get("/trivia/laptop-background-transparent.png")
async def trivia_background(request: Request, key: str = Depends(check_valid_api_key(level=AuthLevel.admin))):
    # return FileResponse("static_files/trivia/newlt.png")
    return FileResponse("static_files/trivia/laptop-background-transparent.png")


# /trivia/leaders - Show the current leaderboard for all questions


@router.get("/trivia/leaders")
async def trivia_leaders(
    request: Request,
    key=Depends(check_valid_api_key(level=AuthLevel.admin)),
):
    mqtt_user = getenv("MQTT_USER")
    mqtt_pass = getenv("MQTT_KEY")

    url = (
        f"{request.base_url}trivia/leaders.html?"
        f"url={request.base_url.hostname}&"
        "port=9883&"
        f"username={mqtt_user}&"
        f"password={mqtt_pass}&"
        f"key={key}"
    )

    return RedirectResponse(url)


@router.get("/trivia/leaders.html", response_class=FileResponse)
async def trivia_leaders_html(request: Request, key: str = Depends(check_valid_api_key(level=AuthLevel.admin))):
    return templates.TemplateResponse("leaders.html", {"request": request, "key": key})


@router.get("/trivia/leaders.css", response_class=FileResponse)
async def trivia_leaders_css(request: Request):
    return FileResponse("static_files/trivia/leaders.css")


@router.get("/trivia/leaders.js", response_class=FileResponse)
async def trivia_leaders_js(request: Request):
    return FileResponse("static_files/trivia/leaders.js")


# /trivia/question_answers - Shows the results of the question as it plays


@router.get("/trivia/question_answers")
async def trivia_question_answers(
    request: Request,
    key=Depends(check_valid_api_key(level=AuthLevel.admin)),
):
    mqtt_user = getenv("MQTT_USER")
    mqtt_pass = getenv("MQTT_KEY")

    url = (
        f"{request.base_url}trivia/question_answers.html?"
        f"url={request.base_url.hostname}&"
        "port=9883&"
        f"username={mqtt_user}&"
        f"password={mqtt_pass}&"
        f"key={key}"
    )

    return RedirectResponse(url)


@router.get("/trivia/question_answers.html", response_class=FileResponse)
async def trivia_question_results(request: Request):
    return FileResponse("static_files/trivia/question_answers.html")


@router.get("/trivia/question_answers.css", response_class=FileResponse)
async def trivia_question_results_css(request: Request):
    return FileResponse("static_files/trivia/question_answers.css")


@router.get("/trivia/question_answers.js", response_class=FileResponse)
async def trivia_question_results_js(request: Request):
    return FileResponse("static_files/trivia/question_answers.js")


# /trivia/manage - Trivia management


@router.get("/trivia/manage/")
async def trivia_manage(request: Request, user=Depends(check_user(level=AuthLevel.admin))):
    return templates.TemplateResponse("manage.html", {"request": request})


@router.post("/trivia/manage/upload")
async def trivia_manage_upload(
    request: Request, questions: UploadFile = File(...), user=Depends(check_user(level=AuthLevel.admin))
):

    # Read the file and decode it to a dictionary
    value = await questions.read()
    value = value.decode("utf-8")
    value = json.loads(value)
    questions = value["quiz"]

    update_log = list()

    for id, question in questions.items():
        query = db.session.query(TriviaQuestions).filter(TriviaQuestions.id == id).one_or_none()
        if query:
            try:
                # Update question if the question text is the same or force_update is set
                if question["text"] == query.text or question.get("force_update", False):

                    if question["text"] != query.text and question.get("force_update", False):
                        # Update question text if it is different and force_update is set
                        query.text = question["text"]
                        update_log.append(f"#{id} text updated. (force_update flag was set)")

                    if query.answers != json.dumps(question["answers"]):
                        # Update answers
                        query.answers = json.dumps(question["answers"])
                        update_log.append(f"#{id} answers updated.")

                    if query.explain != question["explain"]:
                        # Update explanation
                        query.explain = question["explain"]
                        update_log.append(f"#{id} explanation updated.")

                    if query.created_by != question["created_by"]:
                        # Update created_by
                        query.created_by = question["created_by"]
                        update_log.append(f"#{id} created by updated.")

                    if query.reference != question["reference"]:
                        # Update reference text
                        query.reference = question["reference"]
                        update_log.append(f"#{id} reference updated.")

                    if query.enabled != question["enabled"]:
                        # Update enabled status
                        query.enabled = question["enabled"]
                        update_log.append(f"#{id} {'enabled' if question['enabled'] else 'disabled'}")

                    # Set the last update status to today
                    query.last_update_date = str(date.today())

            except KeyError as e:
                update_log.append(f"#{id} Error in json. Key: {e} was missing.")

        else:  # New question
            new_question = TriviaQuestions(
                id=int(id),
                text=question["text"],
                answers=json.dumps(question["answers"]),
                explain=question["explain"],
                last_used_date=str(date.min),
                last_update_date=str(date.today()),
                created_date=str(date.today()),
                created_by=question["created_by"],
                reference=question["reference"],
                enabled=question["enabled"],
            )
            db.session.add(new_question)
            update_log.append(f"#{id} added.")

        db.session.commit()

    update_log.append("Finished.")

    return JSONResponse(update_log)


@router.get("/trivia/manage/download")
async def trivia_manage_download(request: Request, user=Depends(check_user(level=AuthLevel.admin))):

    query = db.session.query(TriviaQuestions).order_by(TriviaQuestions.id).all()
    return_dict = {"quiz": {}}
    for u in query:
        temp_dict = u.__dict__
        question_id = temp_dict["id"]
        # Manipulate the json into a dictionary for the answers, overwriting the string
        temp_dict["answers"] = json.loads(temp_dict["answers"])
        del temp_dict["_sa_instance_state"]  # Don't want to send this in the file
        del temp_dict["id"]  # The ID doesn't belong in the question data
        return_dict["quiz"][question_id] = temp_dict  # Append the current temp to the returned dictionary

    questions_txt = json.dumps(return_dict, indent=4, sort_keys=True, default=str).encode("utf-8")
    return Response(questions_txt, headers={"Content-Disposition": "attachment; filename=questions.txt"})
