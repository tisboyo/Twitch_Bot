#!/usr/local/bin/python
from json import dumps
from json import loads
from os import getenv

import requests

client = getenv("CLIENT_ID") or getenv("client_id")
client_secret = getenv("CLIENT_SECRET") or getenv("client_secret")
auth = getenv("PUBSUB_OAUTH")
channel = getenv("TWITCH_CHANNEL")
host = getenv("WEB_HOSTNAME")

app_key = requests.post(
    "https://id.twitch.tv/oauth2/token",
    params={"client_id": client, "client_secret": client_secret, "grant_type": "client_credentials"},
)

auth = loads(app_key.content)

headers = {"client-id": client, "Authorization": f"Bearer {auth['access_token']}"}

hub = "https://api.twitch.tv/helix/webhooks/subscriptions"
r = requests.get(hub, headers=headers)
j = loads(r.text)
print(dumps(j, indent=1))
