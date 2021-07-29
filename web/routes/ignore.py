from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi_sqlalchemy import db
from starlette.exceptions import HTTPException
from starlette.responses import RedirectResponse
from uvicorn.main import logger
from web_auth import check_user_valid

from models import IgnoreList

router = APIRouter()


@router.get("/ignore", response_class=HTMLResponse)
def get_ignore(request: Request):
    try:
        # Ensure logged in user
        check_user_valid(request)
    except HTTPException:
        # Redirect to login if not
        return RedirectResponse("/login")

    try:
        result = db.session.query(IgnoreList).order_by(IgnoreList.id).all()

    except Exception as e:
        out = "I'm thinking as hard as I can, can you try refreshing? Thanks."
        logger.warning(e)

        return out

    out = """<html>
    <body>
        <table border=1>
            <tr>
                <td>ID</td>
                <td>Enabled</td>
                <td>Pattern</td>
            </tr>"""
    for pattern in result:
        out += f"""
            <tr>
                <td>{pattern.id}</td>
                <td>{pattern.enabled}</td>
                <td>{pattern.pattern}</td>
            </tr>"""

    out += """
        </table>
    </body>
</html>"""
    return out
