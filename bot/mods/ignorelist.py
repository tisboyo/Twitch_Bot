import re

from main import bot
from mods._database import session
from twitchbot import Message
from twitchbot import Mod
from twitchbot import ModCommand
from twitchbot.command import SubCommand
from twitchbot.enums import CommandContext

from models import IgnoreList


class Ignore(Mod):
    name = "ignoremod"

    def __init__(self):
        super().__init__()
        print("Ignore Mod loaded")

    @ModCommand(name, "ignore", context=CommandContext.BOTH, permission="admin")
    async def ignore(self, msg: Message):
        pass

    @SubCommand(ignore, "add", permission="admin")
    async def ignore_add(self, msg: Message, pattern: str):

        # Check if the regex is valid, return error if not.
        try:
            re.compile(pattern)
        except re.error:
            await msg.reply(f"{bot.msg_prefix}Invalid regex pattern.")
            return

        # Will not support a space in the pattern, but that doesn't matter because usernames can't have spaces
        query = session.query(IgnoreList).filter(IgnoreList.pattern == pattern).one_or_none()
        if query is None:
            # Pattern didn't exist, so add it.
            insert = IgnoreList(pattern=pattern)
            session.add(insert)
            session.commit()
            session.refresh(insert)
            await msg.reply(f"{bot.msg_prefix}I will now ignore links from {pattern}")
            bot.ignore_list_patterns[insert.id] = pattern

        else:
            await msg.reply(f"{bot.msg_prefix}That pattern is already in the database.")

    @SubCommand(ignore, "del", permission="admin")
    async def ignore_del(self, msg: Message, id: int):
        id = int(id)  # Library may not actually convert to an integer

        query = session.query(IgnoreList).filter(IgnoreList.id == id).one_or_none()
        if query:
            session.delete(query)
            session.commit()
            await msg.reply(f"{bot.msg_prefix}I will no longer ignore {query.pattern}")
            del bot.ignore_list_patterns[id]
        else:
            await msg.reply(f"{bot.msg_prefix}ID:{id} doesn't exist.")

    @SubCommand(ignore, "enable", permission="admin")
    async def ignore_enable(self, msg: Message, id: int):
        id = int(id)  # Library may not actually convert to an integer
        query = session.query(IgnoreList).filter(IgnoreList.id == id).update({IgnoreList.enabled: True})
        session.commit()
        if query:
            await msg.reply(f"{bot.msg_prefix}ID:{id} enabled.")
            if id not in bot.ignore_list_patterns.keys():
                bot.ignore_list_patterns[id] = query.pattern

        else:
            await msg.reply(f"{bot.msg_prefix}Invalid ID.")

    @SubCommand(ignore, "disable", permission="admin")
    async def ignore_disable(self, msg: Message, id: int):
        id = int(id)  # Library may not actually convert to an integer
        query = session.query(IgnoreList).filter(IgnoreList.id == id).update({IgnoreList.enabled: False})
        session.commit()
        if query:
            await msg.reply(f"{bot.msg_prefix}ID:{id} disabled.")
            if id in bot.ignore_list_patterns.keys():
                del bot.ignore_list_patterns[id]
        else:
            await msg.reply(f"{bot.msg_prefix}Invalid ID.")
