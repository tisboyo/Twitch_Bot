from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from models import Announcements, session

router = APIRouter()


@router.get("/announcements", response_class=HTMLResponse)
def get_announcements(request: Request):
    result = session.query(Announcements).order_by(Announcements.id).all()

    out = """<html>
    <body>
        <table border=1>
            <tr>
                <td>ID</td>
                <td>Times<br />Sent</td>
                <td>Enabled</td>
                <td>Text</td>
            </tr>"""
    for each in result:
        out += f"""
            <tr>
                <td>{each.id}</td>
                <td>{each.times_sent}</td>
                <td>{"Y" if each.enabled else "N"}</td>
                <td>{each.text}</td>
            </tr>"""

    out += """
        </table>
    </body>
</html>"""
    return out
