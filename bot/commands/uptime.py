import datetime

import aiohttp
from dateutil import parser
from dateutil.tz import tzutc
from main import AddOhmsBot
from twitchbot import Command
from twitchbot.config import get_client_id
from twitchbot.config import get_oauth


@Command("uptime")
async def uptime(msg, *args):
    url = "https://api.twitch.tv/helix/streams"
    params = list()  # Create empty list for query parameters

    headers = {
        "client-id": get_client_id(),
        "Authorization": f"Bearer {get_oauth(remove_prefix=True)}",
    }

    # Add channel message came from to the parameters
    params.append(("user_login", msg.channel_name))

    async with aiohttp.ClientSession() as session:
        response = await session.get(url=url, params=params, headers=headers)

        if response.status == 401:
            print("OAuth token error.")
            return

        # Get the response as a json object.
        response_js = await response.json()

        if len(response_js["data"]) <= 0:
            await msg.reply(
                f"{AddOhmsBot.msg_prefix} Unable to query uptime at the moment. Most likely less than 5 minutes or offline."
            )

        else:
            started_at = response_js["data"][0]["started_at"]
            started_at = parser.isoparse(started_at)
            now = datetime.datetime.now(tz=tzutc())
            duration = now - started_at  # + datetime.timedelta(hours=1)
            days, seconds = duration.days, duration.seconds
            hours = days * 24 + seconds // 3600
            minutes = (seconds % 3600) // 60

            h = str(hours) + " hours and " if hours > 0 else ""
            await msg.reply(f"{AddOhmsBot.msg_prefix}Stream has been live for {h}{minutes} minutes.")
