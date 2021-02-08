from alembic import config as alembic_config

# Update database models
alembicArgs = ["--raiseerr", "upgrade", "head"]
alembic_config.main(argv=alembicArgs)

import asyncio
import requests
from os import _exit

import version_check  # noqa: F401

from json import loads
from mqtt import MQTT
from twitchbot.bots import BaseBot
from twitchbot.config import get_client_id
from twitchbot.config import get_oauth
from twitchbot.config import cfg


class AddOhmsBot(BaseBot):
    MQTT = MQTT()
    msg_prefix = "🤖 "
    ATTN_ENABLE = True
    live = False
    location = "Lab"

    def __init__(self):
        super().__init__()

        # Check and set the status of the bot on startup.
        AddOhmsBot.live = self.check_live_status()
        print(f"Stream online: {AddOhmsBot.live}")

    def check_live_status(self):
        """This is NOT an Asynchronous Function. Do not use it once the bot is online."""

        # Check the stream status on startup
        url = f"https://api.twitch.tv/helix/streams?user_login={cfg.channels[0]}"

        headers = {
            "client-id": get_client_id(),
            "Authorization": f"Bearer {get_oauth(remove_prefix=True)}",
        }

        r = requests.get(url=url, headers=headers)
        data = loads(r.text)
        if data.get("error", False):
            print(f"{data['status']} {data['message']}")
            _exit(0)

        data = data["data"]
        if len(data) > 0:
            data = data[0]
            if data["type"] == "live":
                return True
            else:
                return False
        else:
            return False


if __name__ == "__main__":
    bot = AddOhmsBot()
    try:
        bot.run()
    except KeyboardInterrupt:
        print("Shutting down the bot... ")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(bot.shutdown())
        print("Bye")
