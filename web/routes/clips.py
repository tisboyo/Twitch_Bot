from fastapi import APIRouter
from fastapi import Request
from fastapi.params import Form
from fastapi.responses import HTMLResponse
from fastapi_sqlalchemy import db
from starlette.exceptions import HTTPException
from starlette.responses import RedirectResponse
from uvicorn.main import logger
from web_auth import check_user_valid
from web_auth import get_user

from models import Clips

router = APIRouter()


@router.get("/clips", response_class=HTMLResponse)
async def get_clips(request: Request):

    try:
        # Ensure logged in user
        check_user_valid(request)
        me = get_user(request)

    except HTTPException:
        # Redirect to login if not
        response = RedirectResponse("/login")
        response.set_cookie(key="redirect", value=request.url.path)
        return response

    try:
        result = db.session.query(Clips).order_by(Clips.id).all()

    except Exception as e:
        out = "I'm thinking as hard as I can, can you try refreshing? Thanks."
        logger.warning(e)

        return out

    out = """
    <html>
    <head>
        <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
    </head>
    <body>
        <script>
            function updateClipEnable(clip_id, enable) {
                var xhttp;
                xhttp = new XMLHttpRequest();
                xhttp.onreadystatechange = function() {
                    if (this.readyState == 4 && this.status == 200) {
                    document.getElementById("status").innerHTML = this.responseText;
                    }
                };
                xhttp.open("POST", "/clips/enable", true);
                xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
                xhttp.send("clip_id="+clip_id+"&enable="+enable);
            }
        </script>
        <table border=1>
        <tr><td colspan=5 align=center><div id="status">Manage Clips</div></td></tr>
            <tr>
                <td>ID</td>
                <td>Enabled</td>
                <td>Name</td>
                <td>Title</td>
                <td>URL</td>
                <td>Delete</td>
            </tr>"""
    for clip in result:
        out += f"""
            <tr>
                <td>{clip.id}</td>
                <td>
                    <form action="" >
                    <input type="checkbox" name="enabled" onchange="updateClipEnable({clip.id}, this.checked)"
                        {"disabled" if not me.admin else ""}
                        {"checked" if clip.enabled else ""}>
                    </form>
                </td>
                <td>{clip.name}</td>
                <td>{clip.title}</td>
                <td><a href=https://clips.twitch.tv/{clip.url} target=_blank>{clip.url}</a></td>
                <td><form action="/clips/delete" method=POST>
                    <button name="clip_id" value={clip.id} onclick="return confirm('Do you really want to delete this clip?');">🗑️</button>
                    </form>
                </td>
            </tr>
        </table>
    </body>
    </html>"""
    return out


@router.get("/clips/json")
async def get_clips_json(request: Request):
    result = db.session.query(Clips).order_by(Clips.id).all()
    return result


@router.post("/clips/delete")
async def post_clips_delete(request: Request, clip_id: int = Form(...)):
    check_user_valid(request)
    me = get_user(request)
    if me.admin:

        db.session.query(Clips).filter(Clips.id == clip_id).delete()
        db.session.commit()

        print(f"Deleted clip id:{clip_id}")
        return RedirectResponse("/clips", status_code=303)
    else:
        raise HTTPException(403)


@router.post("/clips/enable")
async def post_clips_enabled(request: Request, clip_id: int = Form(...), enable: bool = Form(...)):
    check_user_valid(request)
    me = get_user(request)

    if me.admin:
        query = db.session.query(Clips).filter(Clips.id == clip_id).one_or_none()
        if query:
            query.enabled = enable
            db.session.commit()
            return HTMLResponse(f"Clip #{query.id} {'enabled' if query.enabled else 'disabled'}.")
        else:
            # Announcement ID wasn't in database
            raise HTTPException(404)

    else:
        # User wasn't an admin or mod
        raise HTTPException(403)
