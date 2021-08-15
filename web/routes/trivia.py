import json
from datetime import date
from random import shuffle

from fastapi import APIRouter
from fastapi.datastructures import UploadFile
from fastapi.exceptions import HTTPException
from fastapi.params import File
from fastapi.requests import Request
from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from fastapi.responses import RedirectResponse
from fastapi.responses import Response
from fastapi.templating import Jinja2Templates
from fastapi_sqlalchemy import db
from send_to_bot import send_command_to_bot
from sqlalchemy import func
from web_auth import AuthLevel
from web_auth import check_user_valid
from web_auth import check_valid_api_key
from web_auth import get_user

from models import TriviaQuestions


router = APIRouter()

templates = Jinja2Templates(directory="static_files/trivia")


@router.get("/trivia/q")
async def trivia_q(request: Request, key: str = None):
    if not check_valid_api_key(key, AuthLevel.admin):
        return Response(status_code=403)

    question = (
        db.session.query(TriviaQuestions)
        .filter(TriviaQuestions.last_used_date < date.today(), TriviaQuestions.enabled == True)  # noqa:E712
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

    # Update the last used date to today, so the question isn't repeated
    question.last_used_date = date.today()
    db.session.commit()
    return JSONResponse(jsonret)


@router.post("/trivia/end")
async def trivia_end(key: str = None):
    if not check_valid_api_key(key, AuthLevel.admin):
        return Response(status_code=403)

    print("Trivia ended")
    await send_command_to_bot("trivia", ["end"])
    return Response(status_code=204)


# Static file returns
@router.get("/trivia")
async def trivia_index(request: Request, key: str = None):
    if not check_valid_api_key(key, AuthLevel.admin):
        return Response(status_code=403)

    return templates.TemplateResponse("index.html", {"request": request, "key": key})


@router.get("/trivia/trivia.js")
async def trivia_js(request: Request, key: str = None):
    if not check_valid_api_key(key, AuthLevel.admin):
        return Response(status_code=403)

    return FileResponse("static_files/trivia/trivia.js")


@router.get("/trivia/trivia.css")
async def trivia_css(request: Request):
    return FileResponse("static_files/trivia/trivia.css")


@router.get("/trivia/laptop-background-transparent.png")
async def trivia_background(request: Request, key: str = None):
    if not check_valid_api_key(key, AuthLevel.admin):
        return Response(status_code=403)

    return FileResponse("static_files/trivia/laptop-background-transparent.png")


@router.get("/trivia/manage/")
async def trivia_manage(request: Request):
    try:
        # Ensure logged in user
        check_user_valid(request)
        me = get_user(request)
        if not (me.admin):
            raise HTTPException(403)

    except HTTPException:
        # Redirect to login if not
        response = RedirectResponse("/login")
        response.set_cookie(key="redirect", value=request.url.path)
        return response

    out = """
    <html>
        <body>
            <form method="post" enctype="multipart/form-data" action="/trivia/manage/upload">
                <input type="file" id="trivia" name="questions">
                <input type="submit" value="Upload" name="submit">
            </form>

            Download current <a href="/trivia/manage/download">questions.txt</a>
        </body>
    </html>"""
    return HTMLResponse(out)


@router.post("/trivia/manage/upload")
async def trivia_manage_upload(request: Request, questions: UploadFile = File(...)):
    try:
        # Ensure logged in user
        check_user_valid(request)
        me = get_user(request)
        if not (me.admin):
            raise HTTPException(403)

    except HTTPException:
        # Redirect to login if not
        response = RedirectResponse("/login")
        response.set_cookie(key="redirect", value=request.url.path)
        return response

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
async def trivia_manage_download(request: Request):
    try:
        # Ensure logged in user
        check_user_valid(request)
        me = get_user(request)
        if not (me.admin):
            raise HTTPException(403)

    except HTTPException:
        # Redirect to login if not
        response = RedirectResponse("/login")
        response.set_cookie(key="redirect", value=request.url.path)
        return response

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
