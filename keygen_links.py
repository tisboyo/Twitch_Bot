import json

with open("configs/config.json") as f:
    data = json.load(f)

client_id = data["client_id"]

irc = f"https://id.twitch.tv/oauth2/authorize?response_type=token&client_id={client_id}&redirect_uri=https://twitchapps.com/tokengen/&scope=chat:read+chat:edit+channel:moderate+whispers:read+whispers:edit+channel_editor"
pubsub = f"https://id.twitch.tv/oauth2/authorize?response_type=token&client_id={client_id}&redirect_uri=https://twitchapps.com/tokengen/&scope=channel:read:redemptions+channel:moderate+bits:read+channel_subscriptions"

print("Use this link for IRC OAuth - Use the BOT Account")
print(irc)
print("-" * 100)
print("Use this link for PubSub Oauth - Use the Streamer Account")
print(pubsub)
