from fastapi import APIRouter
from fastapi import Form
from fastapi import Request
from fastapi.exceptions import HTTPException
from fastapi.params import Depends
from fastapi.responses import HTMLResponse
from fastapi_sqlalchemy import db
from uvicorn.main import logger
from web_auth import AuthLevel
from web_auth import check_user

from models import WebAuth

router = APIRouter()

headers = {"Cache-Control": "no-store"}


@router.get("/users", response_class=HTMLResponse)
async def get_users(request: Request, me=Depends(check_user(level=AuthLevel.admin))):
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
    <head>
        <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
    </head>
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
                xhttp.open("POST", "/users/level", true);
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
                xhttp.open("POST", "/users/enable", true);
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
                        {"disabled" if not me.admin or (user.id == me.id) else ""}>
                            <option value="user" {"selected" if user.user else ""}>User</option>
                            <option value="mod" {"selected" if user.mod else ""}>Mod</option>
                            <option value="admin" {"selected" if user.admin else ""}>Admin</option>
                        </select>
                    </form>
                </td>
                <td>
                    <form action="">
                        <!-- The 'n' after {user.id} is to signify a BigInt
                              because the user id is to long to be an integer. -->
                        <input type="checkbox" name="enabled" onchange="updateUserEnabled({user.id}n, this.checked)"
                        {"disabled" if (me.mod and user.admin) or (user.id == me.id) else ""}
                        {"checked" if user.enabled else ""}>
                    </form>

            </tr>"""

    out += """
        </table>
    </body>
</html>"""
    return HTMLResponse(out, headers=headers)


@router.post("/users/level", response_class=HTMLResponse)
async def post_user_level(
    request: Request,
    user_id: int = Form(...),
    level: str = Form(...),
    user=Depends(
        check_user(level=AuthLevel.admin),
    ),
):
    if user.admin:
        query = db.session.query(WebAuth).filter(WebAuth.id == user_id).one_or_none()
        if query:
            if level == "user":
                query.user = True
                query.mod = False
                query.admin = False
            elif level == "mod":
                query.user = False
                query.mod = True
                query.admin = False
            elif level == "admin":
                query.user = False
                query.mod = False
                query.admin = True
            else:
                return HTMLResponse(f"{level} is unknown.", headers=headers)

            db.session.commit()
            return HTMLResponse(f"{query.name} updated to {level}", headers=headers)
        else:
            raise HTTPException(404)
    else:
        raise HTTPException(403)


@router.post("/users/enable", response_class=HTMLResponse)
async def post_user_enable(
    request: Request,
    user_id: int = Form(...),
    enabled: bool = Form(...),
    user=Depends(check_user(level=AuthLevel.admin)),
):

    if user.admin or user.mod:
        query = db.session.query(WebAuth).filter(WebAuth.id == user_id).one_or_none()
        if query:
            # Mods can only enable/disable users, admins can modify anyone
            if (user.mod and not (query.admin or query.mod)) or user.admin:
                query.enabled = enabled
                db.session.commit()
                return HTMLResponse(f'{query.name} {"enabled" if enabled else "disabled"}.', headers=headers)
            else:
                # Mods can't modify mods/admins
                raise HTTPException(403)
        else:
            # User wasn't found in the database.
            raise HTTPException(404)
    else:
        # User wasn't an admin or mod
        raise HTTPException(403)
