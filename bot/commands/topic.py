from main import AddOhmsBot
from mods.database_models import Settings
from twitchbot import cfg
from twitchbot import channels
from twitchbot import Command
from twitchbot import CommandContext
from twitchbot.database.session import session


@Command("topic", context=CommandContext.BOTH)
async def topic(msg, *args):
    result = session.query(Settings).filter(Settings.key == "topic").one_or_none()
    topic = result.value if result is not None else None

    if not msg.is_whisper:
        if topic:
            await msg.reply(topic)
        else:
            # No topic was set
            await msg.reply("No current topic.")
    else:
        try:
            # Send message directly to channel 0
            await channels[cfg.channels[0]].send_message(topic)
        except Exception as e:
            print(e)


@Command("set_topic", permission="admin", context=CommandContext.BOTH)
async def set_topic(msg, *args):

    topic = ""
    for arg in args:
        topic += f"{arg} "

    rows_affected = session.query(Settings).filter(Settings.key == "topic").update({"value": topic})

    if not rows_affected:
        ins = Settings(key="topic", value=topic)
        session.add(ins)

    session.commit()

    await msg.reply(f"{AddOhmsBot.msg_prefix}Topic set.")
