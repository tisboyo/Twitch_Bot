from fastapi import APIRouter
from fastapi import Request
from fastapi.params import Depends
from fastapi.params import Form
from fastapi.responses import HTMLResponse
from fastapi_sqlalchemy import db
from starlette.exceptions import HTTPException
from uvicorn.main import logger
from web_auth import AuthLevel
from web_auth import check_user

from models import AnnouncementCategories
from models import Announcements

router = APIRouter()


@router.get("/announcements", response_class=HTMLResponse)
async def get_announcements(request: Request, user=Depends(check_user(level=AuthLevel.admin))):
    try:
        result = (
            db.session.query(Announcements, AnnouncementCategories)
            .order_by(Announcements.id)
            .join(AnnouncementCategories)
            .all()
        )

        categories = db.session.query(AnnouncementCategories).order_by(AnnouncementCategories.id).all()

    except Exception as e:
        out = "I'm thinking as hard as I can, can you try refreshing? Thanks."
        logger.warning(e)

        return out

    out = """<html>
    <head>
        <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
    </head>
    <body>
        <script>
            function updateAnnouncementEnable(announcement_id, enable) {
                var xhttp;
                xhttp = new XMLHttpRequest();
                xhttp.onreadystatechange = function() {
                    if (this.readyState == 4 && this.status == 200) {
                    document.getElementById("status").innerHTML = this.responseText;
                    }
                };
                xhttp.open("POST", "/announcements/enable", true);
                xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
                xhttp.send("announcement_id="+announcement_id+"&enable="+enable);
            }
            function updateAnnouncementCategory(announcement_id, category) {
                var xhttp;
                xhttp = new XMLHttpRequest();
                xhttp.onreadystatechange = function() {
                    if (this.readyState == 4 && this.status == 200) {
                    document.getElementById("status").innerHTML = this.responseText;
                    }
                };
                xhttp.open("POST", "/announcements/category", true);
                xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
                xhttp.send("announcement_id="+announcement_id+"&category="+category);
            }
        </script>
        <table border=1>
        <tr><td colspan=5 align=center><div id="status">Change announcements</div></td></tr>
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
                <td>
                <form action="">
                <input type="checkbox" name="enabled" onchange="updateAnnouncementEnable({announcement.id}, this.checked)"
                    {"disabled" if user.mod else ""}
                    {"checked" if announcement.enabled else ""}>
                </form>
                </td>
                <td>
                <form action="">
                    <select name="level" onchange="updateAnnouncementCategory({announcement.id}, this.value)"
                    {"disabled" if user.mod else ""}>"""

        for c in categories:
            out += f"""<option value="{c.id}" {"selected" if c.id == category.id else ""}>{c.name}</option>"""

        out += f"""</select>
                </form></td>
                <td>{announcement.text}</td>
            </tr>"""

    out += """
           </table>
        </body>
    </html>"""
    return out


@router.post("/announcements/enable")
async def post_announcements_enabled(
    request: Request,
    announcement_id: int = Form(...),
    enable: bool = Form(...),
    user=Depends(check_user(level=AuthLevel.mod)),
):
    """Manual testing
    curl -d "announcement_id=3&enable=false" --request POST -b "session=SESSION_COOKIE" http://localhost:5000/announcements/enable
    """  # noqa E501

    query = db.session.query(Announcements).filter(Announcements.id == announcement_id).one_or_none()
    if query:
        query.enabled = enable
        db.session.commit()
        return HTMLResponse(f"Announcement #{query.id} {'enabled' if query.enabled else 'disabled'}.")
    else:
        # Announcement ID wasn't in database
        raise HTTPException(404)


@router.post("/announcements/category")
async def post_announcements_category(
    request: Request,
    announcement_id: int = Form(...),
    category: int = Form(...),
    user=Depends(check_user(level=AuthLevel.mod)),
):

    query = db.session.query(Announcements).filter(Announcements.id == announcement_id).one_or_none()
    if query:
        query.category = category
        db.session.commit()
        return HTMLResponse(f"Announcement #{query.id} category updated.")
    else:
        # Announcement ID wasn't in database
        raise HTTPException(404)
