from fastapi import APIRouter
from fastapi.responses import Response
from send_to_bot import send_command_to_bot

router = APIRouter()


@router.get("/trivia")
async def trivia(question: int = -1, answer: int = -1):
    if question == -1 or answer == -1:
        return Response(status_code=418)

    ret = await send_command_to_bot("trivia", ["q", question, answer])
    return Response(status_code=ret.status_code)


@router.post("/endtrivia")
async def end_trivia():
    print("end trivia")
