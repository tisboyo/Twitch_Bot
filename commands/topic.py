from twitchbot import Command, CommandContext, channels, cfg

from data import save_data, load_data

save_file = "topic"


@Command("topic", context=CommandContext.BOTH)
async def topic(msg, *args):
    topic = await load_data(save_file)

    if not msg.is_whisper:
        try:
            await msg.reply(topic["topic"])
        except KeyError:
            # No topic was set
            await msg.reply("No current topic.")
    else:
        try:
            # Send message directly to channel 0
            await channels[cfg.channels[0]].send_message(topic["topic"])
        except Exception as e:
            print(e)


@Command("set_topic", permission="admin", context=CommandContext.BOTH)
async def set_topic(msg, *args):

    topic = ""
    for arg in args:
        topic += f"{arg} "

    topic_d = {"topic": topic}

    await save_data(save_file, topic_d)
    await msg.reply("🤖Topic set.")
