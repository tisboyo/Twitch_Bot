import asyncio
import re
from datetime import datetime
from json import loads
from os import environ
from time import sleep as blocking_sleep

import requests
import version_check  # noqa: F401
from mods._database import session
from mqtt import MQTT
from twitchbot.bots import BaseBot
from twitchbot.config import cfg
from twitchbot.config import get_client_id
from twitchbot.config import get_oauth

from models import IgnoreList
from models import Settings


try:
    # Icecream debugger, this try/except will create a fake ic builtin if the icecream library is not installed
    from icecream import install  # type: ignore

    install()
    ic.configureOutput(
        prefix="debug |", includeContext=True
    )  # If you are getting a flake8 error F821, add `builtins=ic` to bottom of .flake8
except ImportError:
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa: E731
    builtins = __import__("builtins")
    setattr(builtins, "ic", ic)


class AddOhmsBot(BaseBot):
    MQTT = MQTT()
    msg_prefix = "🤖 "
    ATTN_ENABLE = True
    live = False
    location = "Lab"
    treats_enabled = True
    poll_display_active = False

    def __init__(self):
        super().__init__()

        # Load the ignore list from the database on startup
        self.ignore_list_patterns = dict()
        query = session.query(IgnoreList).filter(IgnoreList.enabled == True).all()  # noqa E712
        for each in query:
            self.ignore_list_patterns[each.id] = each.pattern

        # Load IRC Oauth Token
        while not environ.get("oauth", False):
            query = session.query(Settings.value).filter(Settings.key == "twitch_irc_token").one_or_none()
            session.commit()  # Needed to clear the "cache" that doesn't exist for the next query of the same value
            if query:
                values = loads(query[0])
                environ["oauth"] = values["access_token"]
            else:
                print("IRC OAuth (Bot) token not found. Visit web interface to set.")
                blocking_sleep(60)

        # Load Pubsub Oauth Token
        while not environ.get("PUBSUB_OAUTH", False):
            query = session.query(Settings.value).filter(Settings.key == "twitch_pubsub_token").one_or_none()
            session.commit()  # Needed to clear the "cache" that doesn't exist for the next query of the same value
            if query:
                values = loads(query[0])
                environ["PUBSUB_OAUTH"] = values["access_token"]
            else:
                print("PubSub OAuth (Streamer) token not found. Visit web interface to set.")
                blocking_sleep(60)

        # Check and set the status of the bot on startup.
        AddOhmsBot.live = self.check_live_status()
        print(f"Stream online: {AddOhmsBot.live}")

    def check_live_status(self):
        """This is NOT an Asynchronous Function. Do not use it once the bot is online."""

        # Check the stream status on startup
        url = f"https://api.twitch.tv/helix/streams?user_login={cfg.channels[0]}"  # type:ignore

        headers = {
            "client-id": get_client_id(),
            "Authorization": f"Bearer {get_oauth(remove_prefix=True)}",
        }

        r = requests.get(url=url, headers=headers)
        data = loads(r.text)
        if data.get("error", False):
            print(f"{data['status']} {data['message']}")
            raise SystemExit

        data = data["data"]
        if len(data) > 0:
            data = data[0]
            if data["type"] == "live":
                return True
            else:
                return False
        else:
            return False

    def user_ignored(self, username: str) -> bool:
        """Returns True if the user is on the ignore list"""
        for pattern in self.ignore_list_patterns.values():
            if re.match(pattern, username):
                print(f"Ignoring command from {username} matching pattern {pattern}")
                return True

        # Nothing matched, so return False
        return False

    async def on_connected(self):
        # We need to send a mqtt message early to stabilize the mqtt connection. Lets hope this fixes it.
        await self.MQTT.send(self.MQTT.Topics.connected, datetime.now().isoformat(), retain=True)


bot = AddOhmsBot()  # Needs to be out here so it's able to be imported from other modules

if __name__ == "__main__":
    try:
        bot.run()
    except KeyboardInterrupt:
        print("Shutting down the bot... ")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(bot.shutdown())
        print("Bye")
