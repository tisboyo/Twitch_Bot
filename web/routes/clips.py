import re

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
        </script>"""
    out += f"""
        <table border=1>
        <tr><td colspan=10 align=center>
            <div id="status">
        {request.cookies.get('clipmsg') if request.cookies.get('clipmsg') else 'Manage Clips.'}
            </div>
            </td>
        </tr>
            <tr>
                <td>ID</td>
                <td>Enabled</td>
                <td>Name</td>
                <td>Title</td>
                <td>URL</td>
                <td>Added By</td>
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
                <td>{clip.added_by}</td>
                <td><form action="/clips/delete" method=POST>
                    <button name="clip_id" value={clip.id} onclick="return confirm('Do you really want to delete this clip?');">🗑️</button>
                    </form>
                </td>
            </tr>
        """

    out += """
        </table>
        <p>
        <form method=POST action="/clips/add">
        <table border=1>
            <tr><td colspan=10 align=center>Insert new Clip</td></tr>
            <tr>
                <td>Enabled</td>
                <td>Name</td>
                <td>Title</td>
                <td>URL</td>
            </tr>
            <tr>
                <td><input type="checkbox" name="enabled"></td>
                <td><input type="text" name="name"></td>
                <td><input type="text" name="title"></td>
                <td><input type="text" name="url"></td>
                <td><input type="submit" value="Save"></td>
            </tr>
        </table>
    </body>
    </html>"""

    response = HTMLResponse(out)
    response.set_cookie("clipmsg", "")
    return response


@router.get("/clips/json")
async def get_clips_json(request: Request):
    result = db.session.query(Clips).filter(Clips.enabled == True).order_by(Clips.id).all()  # noqa E712
    return result


@router.post("/clips/delete")
async def post_clips_delete(request: Request, clip_id: int = Form(...)):
    check_user_valid(request)
    me = get_user(request)
    if me.admin:

        db.session.query(Clips).filter(Clips.id == clip_id).delete()
        db.session.commit()

        print(f"{me.username} Deleted clip id:{clip_id}")
        response = RedirectResponse("/clips", status_code=303)
        response.set_cookie("clipmsg", f"Deleted clip id:{clip_id}")
        return response
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


@router.post("/clips/add")
async def post_clips_add(
    request: Request,
    enabled: bool = Form(default=False),
    name: str = Form(...),
    title: str = Form(default=""),
    url: str = Form(...),
):
    try:
        # Ensure logged in user
        check_user_valid(request)
        me = get_user(request)

    except HTTPException:
        # Redirect to login if not
        response = RedirectResponse("/login")
        response.set_cookie(key="redirect", value=request.url.path)
        return response

    regex = r"(https?:\/\/(www\.|clips\.)?twitch\.tv\/(baldengineer\/clip\/)?(?P<clip_id>[A-Za-z0-9]*)?)"
    match = re.search(regex, url)

    # Define this up here so we can set the clipmsg cookie throughout
    response = RedirectResponse("/clips", status_code=303)

    if match and match.group("clip_id"):  # Only query if the url was valid and has a clip id
        clip_id = match.group("clip_id")

        query = db.session.query(Clips).filter(Clips.name == name.lower()).one_or_none()
        if not query:
            # name didn't exist, so it's time to add it
            clip = Clips(name=name.lower(), enabled=enabled, title=title, url=clip_id, added_by=me.username)

            db.session.add(clip)
            db.session.commit()
            response.set_cookie("clipmsg", f"{name} has been added to the clip database.")
        else:
            response.set_cookie("clipmsg", f"Sorry, {name} already exists in the clip database.")
    else:
        response.set_cookie("clipmsg", "Sorry, that's not a valid clip url.")

    return response
