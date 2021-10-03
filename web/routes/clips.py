import re

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from fastapi.params import Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi_sqlalchemy import db
from starlette.exceptions import HTTPException
from starlette.responses import FileResponse
from starlette.responses import RedirectResponse
from web_auth import AuthLevel
from web_auth import check_user
from web_auth import check_valid_api_key

from models import Clips

router = APIRouter()
templates = Jinja2Templates(directory="static_files/clips")


@router.get("/clips", response_class=HTMLResponse)
async def clips(request: Request, user=Depends(check_user(level=AuthLevel.admin))):
    return RedirectResponse("/clips/manage.html")


@router.get("/clips/manage.html", response_class=HTMLResponse)
async def clips_manage_html(request: Request, user=Depends(check_user(level=AuthLevel.admin))):

    result = db.session.query(Clips).order_by(Clips.id).all()
    message = request.cookies.get("clipmsg", "") or "Manage Clips"
    response = templates.TemplateResponse(
        "manage.html.jinja", {"request": request, "result": result, "user": user, "message": message}
    )

    response.set_cookie("clipmsg", "")
    return response


@router.get("/clips/manage.js", response_class=HTMLResponse)
async def clips_manage_js(request: Request, user=Depends(check_user(level=AuthLevel.admin))):
    return FileResponse("static_files/clips/manage.js")


@router.get("/clips/json")
async def get_clips_json(request: Request, user=Depends(check_valid_api_key(level=AuthLevel.admin))):
    result = db.session.query(Clips).filter(Clips.enabled == True).order_by(Clips.id).all()  # noqa E712
    return result


@router.post("/clips/delete")
async def post_clips_delete(request: Request, clip_id: int = Form(...), user=Depends(check_user(level=AuthLevel.admin))):
    db.session.query(Clips).filter(Clips.id == clip_id).delete()
    db.session.commit()

    print(f"{user.username} Deleted clip id:{clip_id}")
    response = RedirectResponse("/clips", status_code=303)
    response.set_cookie("clipmsg", f"Deleted clip id:{clip_id}")
    return response


@router.post("/clips/enable")
async def post_clips_enabled(
    request: Request, clip_id: int = Form(...), enable: bool = Form(...), user=Depends(check_user(level=AuthLevel.admin))
):
    query = db.session.query(Clips).filter(Clips.id == clip_id).one_or_none()
    if query:
        query.enabled = enable
        db.session.commit()
        return HTMLResponse(f"Clip #{query.id} {'enabled' if query.enabled else 'disabled'}.")
    else:
        # Announcement ID wasn't in database
        raise HTTPException(404)


@router.post("/clips/add")
async def post_clips_add(
    request: Request,
    enabled: bool = Form(default=False),
    name: str = Form(...),
    title: str = Form(default=""),
    url: str = Form(...),
    user=Depends(check_user(level=AuthLevel.admin)),
):

    regex = r"(https?:\/\/(www\.|clips\.)?twitch\.tv\/(baldengineer\/clip\/)?(?P<clip_id>[A-Za-z0-9_\-]*)?)"
    match = re.search(regex, url)

    # Define this up here so we can set the clipmsg cookie throughout
    response = RedirectResponse("/clips/manage.html", status_code=303)

    if match and match.group("clip_id"):  # Only query if the url was valid and has a clip id
        clip_id = match.group("clip_id")

        query = db.session.query(Clips).filter(Clips.name == name.lower()).one_or_none()
        if not query:
            # name didn't exist, so it's time to add it
            clip = Clips(name=name.lower(), enabled=enabled, title=title, url=clip_id, added_by=user.username)

            db.session.add(clip)
            db.session.commit()
            response.set_cookie("clipmsg", f"{name} has been added to the clip database.", expires=5)
        else:
            response.set_cookie("clipmsg", f"Sorry, {name} already exists in the clip database.", expires=5)
    else:
        response.set_cookie("clipmsg", "Sorry, that's not a valid clip url.", expires=5)

    return response
