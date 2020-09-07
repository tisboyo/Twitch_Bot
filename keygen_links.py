import json

with open("configs/config.json") as f:
    data = json.load(f)

client_id = data["client_id"]

irc = f"https://id.twitch.tv/oauth2/authorize?response_type=token&client_id={client_id}&redirect_uri=https://twitchapps.com/tokengen/&scope=chat:read+chat:edit+channel:moderate+whispers:read+whispers:edit+channel_editor"
helix = f"https://id.twitch.tv/oauth2/authorize?response_type=token&client_id={client_id}&redirect_uri=https://twitchapps.com/tokengen/&scope=channel%3Aread%3Aredemptions%20channel%3Amoderate%20bits%3Aread%20channel_subscriptions"

print("Use this link for IRC OAuth")
print(irc)
print("-" * 100)
print("Use this link for PubSub Oauth")
print(helix)
