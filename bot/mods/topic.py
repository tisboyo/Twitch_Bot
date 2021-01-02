from main import AddOhmsBot
from mods._database import session
from twitchbot import cfg
from twitchbot import Channel
from twitchbot import channels
from twitchbot import CommandContext
from twitchbot import Mod
from twitchbot import ModCommand
from twitchbot import SubCommand

from models import Settings


class TopicMod(Mod):
    name = "topicmod"

    def __init__(self):
        pass

    @ModCommand(name, "topic", context=CommandContext.BOTH)
    async def topic(self, msg, *args):
        topic = self.get_topic()

        if not msg.is_whisper:
            if topic:
                await msg.reply(f"{AddOhmsBot.msg_prefix}{topic}")
            else:
                # No topic was set
                await msg.reply(f"{AddOhmsBot.msg_prefix}No current topic.")
        else:
            try:
                # Send message directly to channel 0
                await channels[cfg.channels[0]].send_message(topic)
            except Exception as e:
                print(e)

    @SubCommand(topic, "set", permission="admin")
    async def set_topic(self, msg, *args):

        topic = ""
        for arg in args:
            topic += f"{arg} "

        rows_affected = session.query(Settings).filter(Settings.key == "topic").update({"value": topic})

        if not rows_affected:
            ins = Settings(key="topic", value=topic)
            session.add(ins)

        session.commit()

        await msg.reply(f"{AddOhmsBot.msg_prefix}Topic set.")

    def get_topic(self):
        result = session.query(Settings).filter(Settings.key == "topic").one_or_none()
        topic = result.value if result is not None else None
        return topic

    async def on_channel_raided(self, channel: Channel, raider: str, viewer_count: int) -> None:
        topic = self.get_topic()

        try:
            # Send message directly to channel 0
            await channels[cfg.channels[0]].send_message(
                f"{AddOhmsBot.msg_prefix}Welcome raiders, the current topic is {topic}"
            )
        except Exception as e:
            print(e)
