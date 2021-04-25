import json

from main import bot
from mods._database import session
from twitchbot import cfg
from twitchbot import Channel
from twitchbot import channels
from twitchbot import CommandContext
from twitchbot import Mod
from twitchbot import ModCommand
from twitchbot import SubCommand
from twitchbot.util.command_util import run_command

from models import Settings


class TopicMod(Mod):
    name = "topicmod"

    def __init__(self):
        pass

    @ModCommand(name, "project", context=CommandContext.CHANNEL)
    async def project(self, msg, *args):
        """Alias command for topic"""
        await run_command("topic", msg)

    @ModCommand(name, "step", context=CommandContext.BOTH)
    async def step(self, msg, *args):
        await run_command("topic", msg, ["step", *args])

    @ModCommand(name, "topic", context=CommandContext.BOTH)
    async def topic(self, msg, *args):
        # Check if user is on ignore list
        if bot.user_ignored(str(msg.author)):
            return

        topic = get_topic()

        if not msg.is_whisper:
            if topic:
                await msg.reply(f"{bot.msg_prefix}{topic}")
            else:
                # No topic was set
                await msg.reply(f"{bot.msg_prefix}No current topic.")
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

        topic_dict = {"topic": topic}

        if save_topic(topic_dict):
            await msg.reply(f"{bot.msg_prefix}Topic set.")

    @SubCommand(topic, "goal", permission="admin")
    async def set_topic_goal(self, msg, *args):

        goal = ""
        for arg in args:
            goal += f"{arg} "

        topic = get_topic(raw=True)
        topic["goal"] = goal

        if save_topic(topic):
            await msg.reply(f"{bot.msg_prefix}Goal set.")

    @SubCommand(topic, "step", permission="admin")
    async def set_topic_step(self, msg, *args):
        step = ""
        for arg in args:
            step += f"{arg} "

        topic = get_topic(raw=True)
        topic["step"] = step

        if save_topic(topic):
            await msg.reply(f"{bot.msg_prefix}Step set.")

    @SubCommand(topic, "link", permission="admin")
    async def set_topic_link(self, msg, *args):
        note = ""
        for arg in args:
            note += f"{arg} "

        topic = get_topic(raw=True)
        topic["note"] = note

        if save_topic(topic):
            await msg.reply(f"{bot.msg_prefix}Link set.")

    async def on_channel_raided(self, channel: Channel, raider: str, viewer_count: int) -> None:
        topic = get_topic()

        try:
            # Send message directly to channel 0
            await channels[cfg.channels[0]].send_message(f"{bot.msg_prefix}Welcome raiders, the current topic is {topic}")
        except Exception as e:
            print(e)


def get_topic(raw=False):
    result = session.query(Settings).filter(Settings.key == "topic").one_or_none()
    topic = result.value if result is not None else None

    if raw:
        return json.loads(topic)

    try:
        topic = json.loads(topic)

        # Check that a topic is set
        if topic.get("topic", False):
            # Build the topic
            topic_text = topic["topic"]
            topic_text = f"{topic_text}Goal: {topic['goal']} " if topic.get("goal", False) else topic_text
            topic_text = f"{topic_text}Currently: {topic['step']} " if topic.get("step", False) else topic_text
            topic_text = f"{topic_text}Notes/Info: {topic['notes']}" if topic.get("notes", False) else topic_text
            return topic_text
        else:
            return None

    except json.decoder.JSONDecodeError:
        # Stored value was not a json string
        return topic


def save_topic(topic: dict):
    topic_json = json.dumps(topic)

    rows_affected = session.query(Settings).filter(Settings.key == "topic").update({"value": topic_json})

    if not rows_affected:
        ins = Settings(key="topic", value=topic_json)
        session.add(ins)

    session.commit()

    return True
