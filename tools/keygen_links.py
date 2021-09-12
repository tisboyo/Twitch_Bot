#!/usr/bin/python3
import json
from os import getenv

from dotenv import load_dotenv

load_dotenv()

with open("../bot/configs/config.json") as f:
    data = json.load(f)


client_id = getenv("TWITCH_CLIENT_ID") if data["client_id"].startswith("env_") else data["client_id"]

# https://id.twitch.tv/oauth2/authorize?response_type=code&client_id=8bmp6j83z5w4mepq0dn0q1a7g186azi&redirect_uri=https%3A%2F%2Fstreamlabs.com%2Fauth&scope=user_read+channel_subscriptions+user_subscriptions+chat%3Aread+channel_editor+bits%3Aread+channel%3Aread%3Asubscriptions+channel%3Aread%3Apolls+channel%3Amanage%3Apolls&state=fe7e59317354dc538f8207a420422b0fdcddfede
irc_scope = [
    "chat:read",
    "chat:edit",
    "channel:moderate",
    "whispers:read",
    "whispers:edit",
    "channel_editor",
    "channel:manage:polls",
]
irc = f"https://id.twitch.tv/oauth2/authorize?response_type=token&client_id={client_id}&redirect_uri=https://twitchapps.com/tokengen/&scope={'+'.join(irc_scope)}"  # noqa:E501

pubsub_scope = [
    "channel:read:redemptions",
    "channel:moderate+bits:read",
    "channel_subscriptions",
    "channel:manage:polls",
]

pubsub = f"https://id.twitch.tv/oauth2/authorize?response_type=token&client_id={client_id}&redirect_uri=https://twitchapps.com/tokengen/&scope={'+'.join(pubsub_scope)}"  # noqa:E501

print("Use this link for IRC OAuth - Use the BOT Account")
print(irc)
print("-" * 100)
print("Use this link for PubSub Oauth - Use the Streamer Account")
print(pubsub)
