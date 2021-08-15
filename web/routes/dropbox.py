import json
from datetime import datetime
from datetime import timedelta
from os import getenv

import aiohttp
from fastapi import APIRouter
from fastapi import Request
from fastapi_sqlalchemy import db
from starlette.exceptions import HTTPException
from starlette.responses import RedirectResponse
from web_auth import check_user_valid
from web_auth import get_user

from models import Settings

router = APIRouter()

return_uri = f"https://{getenv('WEB_HOSTNAME')}/dropbox-response"


@router.get("/dropbox")  # , response_class=RedirectResponse)
async def get_dropbox(request: Request):
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
        client_id = db.session.query(Settings.value).filter(Settings.key == "dropbox_client_id").one_or_none().value
    except AttributeError:
        print("Dropbox Client ID not set")
        return

    if client_id is not None:
        redir_uri = f"https://www.dropbox.com/oauth2/authorize?client_id={client_id}&token_access_type=offline&redirect_uri={return_uri}&response_type=code"  # noqa E501
        return RedirectResponse(redir_uri)


@router.get("/dropbox-response")
async def post_dropbox(request: Request):
    try:
        client_id = db.session.query(Settings.value).filter(Settings.key == "dropbox_client_id").one_or_none().value
        client_secret = db.session.query(Settings.value).filter(Settings.key == "dropbox_client_secret").one_or_none().value
    except AttributeError:
        print("Dropbox Client ID or Secret not set.")
        return

    if client_id is not None:
        params = dict(request.query_params)
        key = params["code"]

        req_url = "https://api.dropboxapi.com/oauth2/token"
        req_post_data = dict(code=key, grant_type="authorization_code", redirect_uri=return_uri)
        req_auth = aiohttp.BasicAuth(client_id, client_secret)

        async with aiohttp.ClientSession() as aiohttp_session:
            async with aiohttp_session.post(req_url, data=req_post_data, auth=req_auth) as resp:
                resp = json.loads(await resp.text())
                try:
                    new_token = resp["access_token"]
                    account_id = resp["account_id"]
                    refresh_token = resp["refresh_token"]
                    key_expires = datetime.now() + timedelta(seconds=(resp["expires_in"] - 5))

                    valid_account = db.session.query(Settings).filter(Settings.key == "dropbox_account_id").one_or_none()

                    if valid_account:
                        # Make sure the same account is being used
                        if valid_account.value != account_id:
                            return
                    else:
                        # No account was in the database, so add it.
                        insert = Settings(key="dropbox_account_id", value=account_id)
                        db.session.add(insert)

                    # Update the API key in the database
                    api_key_updated = (
                        db.session.query(Settings)
                        .filter(Settings.key == "dropbox_api_key")
                        .update({Settings.value: new_token})
                    )

                    api_refresh_token_updated = (
                        db.session.query(Settings)
                        .filter(Settings.key == "dropbox_api_refresh_token")
                        .update({Settings.value: refresh_token})
                    )
                    api_expires_updated = (
                        db.session.query(Settings)
                        .filter(Settings.key == "dropbox_api_key_expires")
                        .update({Settings.value: key_expires})
                    )
                    if not api_key_updated:
                        # Insert into the database if it wasn't updatable
                        insert_key = Settings(key="dropbox_api_key", value=new_token)
                        db.session.add(insert_key)

                    if not api_refresh_token_updated:
                        insert_refresh = Settings(key="dropbox_api_refresh_token", value=refresh_token)
                        db.session.add(insert_refresh)

                    if not api_expires_updated:
                        insert_refresh = Settings(key="dropbox_api_key_expires", value=key_expires)
                        db.session.add(insert_refresh)

                    db.session.commit()

                except KeyError as e:
                    # KeyError happens if both an access_token and account_id are not sent
                    print(e)
                    pass

        return "Done"
