from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi_sqlalchemy import db
from starlette.exceptions import HTTPException
from starlette.responses import RedirectResponse
from twitchbot.database.models import CustomCommand
from uvicorn.main import logger
from web_auth import check_user_valid
from web_auth import get_user

router = APIRouter()


@router.get("/commands", response_class=HTMLResponse)
async def get_commands(request: Request):

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

    try:
        result = db.session.query(CustomCommand).order_by(CustomCommand.id).all()

    except Exception as e:
        out = "I'm thinking as hard as I can, can you try refreshing? Thanks."
        logger.warning(e)

        return out

    out = """
    <html>
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
