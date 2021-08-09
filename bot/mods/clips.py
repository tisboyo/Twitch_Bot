import datetime
import re

from main import bot
from mods._database import session
from sqlalchemy import func
from twitchbot import CommandContext
from twitchbot import Mod
from twitchbot import ModCommand
from twitchbot import SubCommand
from twitchbot.message import Message

from models import Clips


class ClipMod(Mod):
    name = "clipmod"

    def __init__(self):
        super().__init__()
        print("ClipMod loaded")
        self.last_random_clip_time = datetime.datetime.now()

    @ModCommand(name, "clip", context=CommandContext.CHANNEL)
    async def clip(self, msg: Message, *args):
        # Check if user is on ignore list
        if bot.user_ignored(str(msg.author)):
            return

        query = None  # Just to appease the linters

        parts_len = len(msg.parts)
        if parts_len == 1:
            # Base command only
            if (self.last_random_clip_time + datetime.timedelta(minutes=5)) < datetime.datetime.now():
                query = (
                    session.query(Clips)
                    .filter(Clips.enabled == True)  # noqa:E712
                    .order_by(func.random())
                    .limit(1)
                    .one_or_none()
                )
                self.last_random_clip_time = datetime.datetime.now()

        elif parts_len == 2:
            name = msg.parts[1]
            query = session.query(Clips).filter(Clips.name == name.lower(), Clips.enabled == True).one_or_none()  # noqa:E712

        if query:
            await msg.reply(
                f"{bot.msg_prefix} {query.title if query.title else query.name}: https://clips.twitch.tv/{query.url}"
            )

    @SubCommand(clip, "add", permission="admin")
    async def clip_add(self, msg: Message, *args):
        """Add twitch clips to the database"""

        try:
            name = msg.parts[2]

            regex = r"(https?:\/\/(www\.|clips\.)?twitch\.tv\/(baldengineer\/clip\/)?(?P<clip_id>[A-Za-z0-9]*)?)"
            match = re.search(regex, msg.parts[3])

        except IndexError:
            await msg.reply(f"{bot.msg_prefix} Usage: !clip add <name> <clip url>")
            return

        if match and match.group("clip_id"):  # Only query if the url was valid and has a clip id
            clip_id = match.group("clip_id")

            query = session.query(Clips).filter(Clips.name == name.lower()).one_or_none()
            if not query:
                # name didn't exist, so it's time to add it
                clip = Clips(name=name.lower(), enabled=True, url=clip_id)

                session.add(clip)
                session.commit()
                await msg.reply(f"{bot.msg_prefix} {name} has been added to the clip database.")
            else:
                await msg.reply(f"{bot.msg_prefix} Sorry, {name} already exists in the clip database.")
        else:
            await msg.reply(f"{bot.msg_prefix} Sorry, that's not a valid clip url.")
