#!/usr/local/bin/python
import pathlib
from datetime import datetime
from os import _exit
from os import getenv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

import dropbox
from models import Settings

mysql_database = getenv("MYSQL_DATABASE")
mysql_user = getenv("MYSQL_USER")
mysql_pass = getenv("MYSQL_PASSWORD")
webhost = getenv("WEB_HOSTNAME")

engine = create_engine(f"mysql+mysqlconnector://{mysql_user}:{mysql_pass}@mysql:3306/{mysql_database}")

session = scoped_session(sessionmaker(bind=engine))

try:
    access_token = session.query(Settings).filter(Settings.key == "dropbox_api_key").one_or_none().value
    refresh_token = session.query(Settings).filter(Settings.key == "dropbox_api_refresh_token").one_or_none().value
    client_id = session.query(Settings.value).filter(Settings.key == "dropbox_client_id").one_or_none().value
    client_secret = session.query(Settings.value).filter(Settings.key == "dropbox_client_secret").one_or_none().value


except AttributeError:
    print("API Key Error.")
    _exit(1)

except ValueError:
    print("API Key Expiration error.")
    _exit(1)

d = dropbox.Dropbox(
    oauth2_access_token=access_token, oauth2_refresh_token=refresh_token, app_key=client_id, app_secret=client_secret
)

# Refresh the access token if needed.
d.check_and_refresh_access_token()

paths = pathlib.Path("/db_backup/").glob("**/*.sql")
target = f"/twitchbotdb-{webhost}/"  # Dropbox path to save file

for path in paths:
    targetfile = target + path.name
    with path.open("rb") as f:
        try:
            now = datetime.now()
            meta = d.files_upload(f.read(), targetfile, mode=dropbox.files.WriteMode("overwrite"))
            if meta.server_modified > now:
                print(f"{path.name} uploaded.")

        except dropbox.exceptions.AuthError:
            print("Dropbox auth key error")
            continue
