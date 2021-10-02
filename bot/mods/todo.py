import aiohttp
from main import bot
from mods._database import session
from twitchbot import cfg
from twitchbot import channels
from twitchbot import CommandContext
from twitchbot import Mod
from twitchbot import ModCommand
from twitchbot.message import Message

from models import Settings


class TodoMod(Mod):
    name = "to_domod"

    def __init__(self):
        super().__init__()
        print("TodoMod loaded")

        query = session.query(Settings).filter(Settings.key == "to_do_webhook").one_or_none()
        self.webhook = query.value if query else None

    @ModCommand(name, "todo", context=CommandContext.CHANNEL, permission="todo")
    async def todo(self, msg: Message, *args):
        # Check if user is on ignore list
        if bot.user_ignored(str(msg.author)):
            return

        if self.webhook is None:
            await channels[cfg.channels[0]].send_message(
                bot.msg_prefix + "I'm missing a webhook address. @tisboyo broke me."
            )

        async with aiohttp.ClientSession() as session:
            response = await session.post(
                self.webhook, json={"content": msg.content, "username": f"TwitchBot: Todo by {msg.author}"}
            )
            if response.status == 204:
                message = "Thanks for the todo, I posted it to discord for review later."
                await channels[cfg.channels[0]].send_message(bot.msg_prefix + message)
