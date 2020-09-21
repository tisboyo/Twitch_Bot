import re

import aiohttp
from twitchbot import cfg
from twitchbot import channels
from twitchbot import Message
from twitchbot import Mod


class LinksToDiscord(Mod):
    name = "linkstodiscord"

    def __init__(self):
        super().__init__()
        print("LinksToDiscord loaded")
        self.webhook = cfg.webhookurl

    def find_url(self, string):
        # findall() has been used
        # with valid conditions for urls in string
        regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"  # noqa:E501
        url = re.findall(regex, string)
        return [x[0] for x in url]

    async def on_privmsg_received(self, msg: Message):
        # Webhook not configured  or Ignore these users
        if self.webhook is None or msg.author in ["addohms", "streamlabs"]:
            return

        urls = self.find_url(msg.content)

        if len(urls):
            for each in urls:
                async with aiohttp.ClientSession() as session:
                    response = await session.post(
                        self.webhook, json={"content": each, "username": f"TwitchBot for {msg.author}"}
                    )
                    if response.status == 204:
                        message = "Thanks for the link, I posted it to discord."
                        await channels[cfg.channels[0]].send_message("🤖" + message)
