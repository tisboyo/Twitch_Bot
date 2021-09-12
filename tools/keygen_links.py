#!/usr/bin/python3
import json
from os import getenv

from dotenv import load_dotenv

load_dotenv()

with open("../bot/configs/config.json") as f:
    data = json.load(f)


client_id = getenv("TWITCH_CLIENT_ID") if data["client_id"].startswith("env_") else data["client_id"]


irc = f"https://id.twitch.tv/oauth2/authorize?response_type=token&client_id={client_id}&redirect_uri=https://twitchapps.com/tokengen/&scope=chat:read+chat:edit+channel:moderate+whispers:read+whispers:edit+channel_editor+channel:manage:polls"  # noqa:E501
pubsub = f"https://id.twitch.tv/oauth2/authorize?response_type=token&client_id={client_id}&redirect_uri=https://twitchapps.com/tokengen/&scope=channel:read:redemptions+channel:moderate+bits:read+channel_subscriptions+channel:manage:polls"  # noqa:E501

print("Use this link for IRC OAuth - Use the BOT Account")
print(irc)
print("-" * 100)
print("Use this link for PubSub Oauth - Use the Streamer Account")
print(pubsub)
