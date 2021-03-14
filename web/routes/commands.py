from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi_sqlalchemy import db
from twitchbot.database.models import CustomCommand
from uvicorn.main import logger

router = APIRouter()


@router.get("/commands", response_class=HTMLResponse)
async def get_commands(request: Request):
    try:
        result = db.session.query(CustomCommand).order_by(CustomCommand.id).all()

    except Exception as e:
        out = "I'm thinking as hard as I can, can you try refreshing? Thanks."
        logger.warning(e)

        return out

    out = """<html>
    <body>
        <table border=1>
            <tr>
                <td>ID</td>
                <td>Command</td>
                <td>Response</td>
            </tr>"""
    for command in result:
        out += f"""
            <tr>
                <td>{command.id}</td>
                <td>{command.name}
                <td>{command.response}</td>
            </tr>"""

    out += """
        </table>
    </body>
</html>"""
    return out
