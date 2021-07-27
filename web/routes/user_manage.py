from fastapi import APIRouter
from fastapi import Form
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi_sqlalchemy import db
from starlette.exceptions import HTTPException
from starlette.responses import RedirectResponse
from uvicorn.main import logger
from web_auth import check_user_valid
from web_auth import get_user

from models import WebAuth

router = APIRouter()


@router.get("/users", response_class=HTMLResponse)
async def get_users(request: Request):

    try:
        # Ensure logged in user
        check_user_valid(request)
        me = get_user(request)
        if not (me.mod or me.admin):
            raise HTTPException(403)

    except HTTPException:
        # Redirect to login if not
        return RedirectResponse("/login")

    try:
        result = (
            db.session.query(WebAuth)
            .order_by(WebAuth.admin.desc())
            .order_by(WebAuth.mod.desc())
            .order_by(WebAuth.name)
            .all()
        )

    except Exception as e:
        out = "I'm thinking as hard as I can, can you try refreshing? Thanks."
        logger.warning(e)

        return out

    out = """<html>
    <body>
        <script>
            function updateUserLevel(user, level) {
                var xhttp;
                xhttp = new XMLHttpRequest();
                xhttp.onreadystatechange = function() {
                    if (this.readyState == 4 && this.status == 200) {
                    document.getElementById("status").innerHTML = this.responseText;
                    }
                };
                xhttp.open("POST", "/update_user_level", true);
                xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
                xhttp.send("user_id="+user+"&level="+level);
            }
            function updateUserEnabled(user, enabled) {
                var xhttp;
                xhttp = new XMLHttpRequest();
                xhttp.onreadystatechange = function() {
                    if (this.readyState == 4 && this.status == 200) {
                    document.getElementById("status").innerHTML = this.responseText;
                    }
                };
                xhttp.open("POST", "/update_user_enabled", true);
                xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
                xhttp.send("user_id="+user+"&enabled="+enabled);
            }
        </script>
        <table border=1>
            <tr>
                <td colspan=3 align=center><div id="status">Change user levels.</div></td>
            </tr>
            <tr>
                <td>ID</td>
                <td>Name</td>
                <td>Level</td>
                <td>Enabled</td>
            </tr>"""
    for user in result:
        out += f"""
            <tr>
                <td>{user.id}</td>
                <td>{user.name}
                <td>
                    <form action="">
                        <!-- The 'n' after {user.id} is to signify a BigInt
                              because the user id is to long to be an integer. -->
                        <select name="level" onchange="updateUserLevel({user.id}n, this.value)"
                        {"disabled" if not me.admin else ""}>
                            <option value="User" {"selected" if user.user else ""}>User</option>
                            <option value="Mod" {"selected" if user.mod else ""}>Mod</option>
                            <option value="Admin" {"selected" if user.admin else ""}>Admin</option>
                        </select>
                    </form>
                </td>
                <td>
                    <form action="">
                        <!-- The 'n' after {user.id} is to signify a BigInt
                              because the user id is to long to be an integer. -->
                        <input type="checkbox" name="enabled" onchange="updateUserEnabled({user.id}n, this.checked)">
                    </form>

            </tr>"""

    out += """
        </table>
    </body>
</html>"""
    return out


@router.post("/update_user_level", response_class=HTMLResponse)
async def post_update_user_level(request: Request, user_id: int = Form(...), level: str = Form(...)):
    check_user_valid(request)
    user = get_user(request)
    if user.admin:
        query = db.session.query(WebAuth).filter(WebAuth.id == user_id).one_or_none()
        if query:

            return f"{query.name} updated to {level}"
        else:
            raise HTTPException(404)
    else:
        raise HTTPException(403)


@router.post("/update_user_enabled", response_class=HTMLResponse)
async def post_update_user_enabled(request: Request, user_id: int = Form(...), enabled: bool = Form(...)):
    check_user_valid(request)
    me = get_user(request)
    if me.admin or me.mod:
        query = db.session.query(WebAuth).filter(WebAuth.id == user_id).one_or_none()
        if query:

            return f'{query.name} {"enabled" if enabled else "disabled"}.'
        else:
            raise HTTPException(404)
    else:
        raise HTTPException(403)
