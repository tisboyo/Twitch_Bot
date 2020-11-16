from main import AddOhmsBot
from twitchbot import cfg
from twitchbot import channels
from twitchbot import Command
from twitchbot import CommandContext
from twitchbot import SubCommand

from mods._database_models import session
from mods._database_models import Settings


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


@SubCommand(topic, "set", permission="admin")
async def set_topic(msg, *args):

    topic = ""
    for arg in args:
        topic += f"{arg} "

    try:
        rows_affected = session.query(Settings).filter(Settings.key == "topic").update({"value": topic})

        if not rows_affected:
            ins = Settings(key="topic", value=topic)
            session.add(ins)

        session.commit()
    except Exception as e:
        session.rollback()
        print("SQLAlchemy Error, rolling back.")
        print(e)

    await msg.reply(f"{AddOhmsBot.msg_prefix}Topic set.")
