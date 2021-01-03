#!/usr/local/bin/python
import pathlib
from os import getenv

import dropbox

api_key = getenv("DROPBOX_OAUTH")
paths = pathlib.Path("/db_backup/").glob("**/*.sql")
target = "/twitchbotdb-backup/"  # Dropbox path to save file

d = dropbox.Dropbox(api_key)

filename = "*.txt"
# filepath = folder / filename

for path in paths:
    targetfile = target + path.name
    with path.open("rb") as f:
        meta = d.files_upload(f.read(), targetfile, mode=dropbox.files.WriteMode("overwrite"))
        print(f"{path.name} uploaded.")
