from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi_sqlalchemy import db
from uvicorn.main import logger

from models import AnnouncementCategories
from models import Announcements

router = APIRouter()


@router.get("/announcements", response_class=HTMLResponse)
async def get_announcements(request: Request):
    try:
        result = (
            db.session.query(Announcements, AnnouncementCategories)
            .order_by(Announcements.id)
            .join(AnnouncementCategories)
            .all()
        )

    except Exception as e:
        out = "I'm thinking as hard as I can, can you try refreshing? Thanks."
        logger.warning(e)

        return out

    out = """<html>
    <body>
        <table border=1>
            <tr>
                <td>ID</td>
                <td>Times<br />Sent</td>
                <td>Enabled</td>
                <td>Category</td>
                <td>Text</td>
            </tr>"""
    for announcement, category in result:
        out += f"""
            <tr>
                <td>{announcement.id}</td>
                <td>{announcement.times_sent}</td>
                <td>{"Y" if announcement.enabled else "N"}</td>
                <td>{category.name}
                <td>{announcement.text}</td>
            </tr>"""

    out += """
        </table>
    </body>
</html>"""
    return out
