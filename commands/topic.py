from twitchbot import Command
import asyncio
from aiofile import AIOFile
import json
from data import save_data, load_data

save_file = "topic"


@Command("topic")
async def topic(msg, *args):
    topic = await load_data(save_file)
    try:
        await msg.reply(topic["topic"])
    except KeyError:
        # No topic was set
        await msg.reply("No current topic.")


@Command("set_topic", permission="admin")
async def set_topic(msg, *args):

    topic = ""
    for arg in args:
        topic += f"{arg} "

    topic_d = {"topic": topic}

    await save_data(save_file, topic_d)
    await msg.reply("🤖Topic set.")
