from twitchbot import Command
import asyncio
from aiofile import AIOFile
import json

json_file = "topic.json"


async def load_json_file() -> dict:
    # Load the data file
    try:
        async with AIOFile(json_file, "r") as afp:
            data = json.loads(await afp.read())
            return data

    except FileNotFoundError:
        # Create the file because it didn't exist and return an empty dictionary
        async with AIOFile(json_file, "w+") as afp:
            await afp.write(json.dumps({}))

        return dict()


async def save_json_file(data) -> None:
    # Write the messages back to the file
    try:
        async with AIOFile(json_file, "w+") as afp:
            await afp.write(json.dumps(data))

    except FileNotFoundError as e:
        print(e)


@Command("topic")
async def topic(msg, *args):
    topic = await load_json_file()
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

    await save_json_file(topic_d)
    await msg.reply("🤖Topic set.")
