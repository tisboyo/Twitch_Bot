import re

import aiohttp
from main import bot
from mods._database import session
from twitchbot import cfg
from twitchbot import channels
from twitchbot import Message
from twitchbot import Mod
from twitchbot import ModCommand
from twitchbot.enums import CommandContext

from models import LinksToDiscordIgnoreList
from models import Settings


class LinksToDiscord(Mod):
    name = "linkstodiscord"

    def __init__(self):
        super().__init__()
        print("LinksToDiscord loaded")

        query = session.query(Settings).filter(Settings.key == "link_webhook").one_or_none()
        self.webhook = query.value if query else None
        self.session = session

    def find_url(self, string):
        # findall() has been used
        # with valid conditions for urls in string
        regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"  # noqa:E501
        url = re.findall(regex, string)
        return [x[0] for x in url]

    @ModCommand(name, "ignorelinks", context=CommandContext.BOTH, permission="admin")
    async def ignore_user(self, msg: Message, user: str):
        insert = LinksToDiscordIgnoreList(username=user.lower())
        session.add(insert)
        session.commit()
        await msg.reply(f"{bot.msg_prefix}I will now ignore links from {user}")

    @ModCommand(name, "allowlinks", context=CommandContext.BOTH, permission="admin")
    async def allow_user(self, msg: Message, user: str):
        query = (
            session.query(LinksToDiscordIgnoreList).filter(LinksToDiscordIgnoreList.username == user.lower()).one_or_none()
        )
        if query:
            session.delete(query)
            session.commit()
            await msg.reply(f"{bot.msg_prefix}I will now allow links from {user}")
        else:
            await msg.reply(f"{bot.msg_prefix}{user} wasn't on my ignore list.")

    async def on_privmsg_received(self, msg: Message):
        # Webhook not configured  or Ignore these users
        if self.webhook is None:
            return
        elif (  # User is in ignore list
            self.session.query(LinksToDiscordIgnoreList)
            .filter(LinksToDiscordIgnoreList.username == msg.author.lower())
            .one_or_none()
        ):
            return
        elif msg[0] == cfg.prefix:
            # Ignore all commands that have links in them
            return

        urls = self.find_url(msg.content)

        if len(urls):
            # for each in urls: # Trying out posting the entire message
            async with aiohttp.ClientSession() as session:
                response = await session.post(
                    self.webhook, json={"content": msg.content, "username": f"TwitchBot: Link by {msg.author}"}
                )
                if response.status == 204:
                    message = "Thanks for the link, I posted it to discord."
                    await channels[cfg.channels[0]].send_message(bot.msg_prefix + message)
