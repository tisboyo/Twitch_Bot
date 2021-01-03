#!/usr/local/bin/python
import pathlib
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
    api_key = session.query(Settings).filter(Settings.key == "dropbox_api_key").one_or_none().value
except AttributeError:
    print("API Key Error.")
    _exit(1)

paths = pathlib.Path("/db_backup/").glob("**/*.sql")
target = f"/twitchbotdb-{webhost}/"  # Dropbox path to save file

d = dropbox.Dropbox(api_key)

filename = "*.txt"
# filepath = folder / filename

for path in paths:
    targetfile = target + path.name
    with path.open("rb") as f:
        try:
            meta = d.files_upload(f.read(), targetfile, mode=dropbox.files.WriteMode("overwrite"))
        except dropbox.exceptions.AuthError:
            print("Dropbox auth key error")
            continue

        print(f"{path.name} uploaded.")
