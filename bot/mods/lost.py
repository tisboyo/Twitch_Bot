import json
from asyncio import sleep

from main import bot
from mods._database import session
from twitchbot import Channel
from twitchbot import CommandContext
from twitchbot import Mod
from twitchbot import ModCommand
from twitchbot.message import Message

from models import Settings


class LostMod(Mod):
    name = "lostmod"

    def __init__(self):
        super().__init__()
        print("LostMod loaded")
        result = session.query(Settings).filter(Settings.key == "lost_count").one_or_none()
        self.lost_count = json.loads(result.value) if result is not None else {"session": 0, "total": 0}
        self.not_live_updated = False

    async def on_channel_joined(self, channel: Channel):
        while True:
            if not bot.live:
                if not self.not_live_updated:
                    # Reset the session if the stream is not live
                    self.lost_count["session"] = 0

                    # Update the session key if it hasn't been updated since going offline
                    session.query(Settings).filter(Settings.key == "lost_count").update(
                        {"value": json.dumps(self.lost_count)}
                    )

                self.not_live_updated = True
            else:
                # Reset keeping track if the session count has been updated since going offline
                self.not_live_updated = False

            await sleep(60)

    @ModCommand(name, "lost", context=CommandContext.BOTH, cooldown=180)
    async def lost(self, msg: Message, *args):
        # Check if user is on ignore list
        if bot.user_ignored(str(msg.author)):
            return

        # Increase both counts
        self.lost_count["session"] += 1
        self.lost_count["total"] += 1

        rows_affected = (
            session.query(Settings).filter(Settings.key == "lost_count").update({"value": json.dumps(self.lost_count)})
        )

        if not rows_affected:
            ins = Settings(key="lost_count", value=json.dumps(self.lost_count))
            session.add(ins)

        session.commit()

        await msg.reply(
            f"@baldengineer has lost {self.lost_count['session']} things so far today, {self.lost_count['total']} total."
        )
