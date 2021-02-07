#!/usr/local/bin/python
import datetime
from json import loads
from os import _exit
from os import getenv

import requests

client = getenv("CLIENT_ID") or getenv("client_id")
auth = getenv("PUBSUB_OAUTH")
channel = getenv("TWITCH_CHANNEL")
host = getenv("WEB_HOSTNAME")
signing_secret = getenv("TWITCH_SIGNING_SECRET")

headers = {"client-id": client, "Authorization": f"Bearer {auth}"}
r = requests.get(f"https://api.twitch.tv/helix/users?login={channel}", headers=headers)
data = loads(r.text)
try:
    channel_id = data["data"][0]["id"]
except KeyError:
    print(data["error"], data["status"], data["message"])
    print(f"{client=}")
    print(f"{auth=}")
    _exit(0)


hub = "https://api.twitch.tv/helix/webhooks/hub"

urls = [  # Format is Request, then fastapi path for Twitch to Post to.
    (  # User Follows
        f"https://api.twitch.tv/helix/users/follows?first=1&to_id={channel_id}",
        "/twitch-webhook/follow",
    ),
    (  # Stream changes
        f"https://api.twitch.tv/helix/streams?user_id={channel_id}",
        "/twitch-webhook/stream",
    ),
]

for url in urls:
    data = {
        "hub.callback": f"https://{host}{url[1]}",
        "hub.mode": "subscribe",
        "hub.topic": url[0],
        "hub.lease_seconds": 90000,  # 25 hours
        "hub.secret": signing_secret,
    }
    r = requests.post(hub, data=data, headers=headers)
    print(datetime.datetime.now().isoformat(), r, f"{url[1]}")
