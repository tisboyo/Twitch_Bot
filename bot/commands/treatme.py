from main import AddOhmsBot
from twitchbot import Command
from twitchbot import SubCommand
from twitchbot.database.session import session

from mods.database_models import Settings

# Key that is sent to Adafruit.IO
aio_key = "dispense-treat-toggle"

# Set a default cooldown
q = session.query(Settings.value).filter(Settings.key == "treatbot_mqtt_cooldown").one_or_none()
if q is None:
    # Value wasn't in the database, lets insert it.
    insert = Settings(key="treatbot_mqtt_cooldown", value=300)
    session.add(insert)
    AddOhmsBot.AIO.mqtt_cooldown[aio_key] = 300
else:
    AddOhmsBot.AIO.mqtt_cooldown[aio_key] = int(q[0])


@Command("treatme")
async def push_treat(msg, *args):
    if AddOhmsBot().AIO.send(aio_key):
        await msg.reply(f"{AddOhmsBot.msg_prefix}Teleporting a treat")
    else:
        await msg.reply(f"{AddOhmsBot.msg_prefix}I couldn't do that at the moment. Sorry ☹️")


@SubCommand(push_treat, "cooldown", permission="admin")
async def treatme_cooldown(msg, *args):
    cooldown = AddOhmsBot.AIO.mqtt_cooldown

    try:
        new_cooldown = int(args[0])
        cooldown[aio_key] = new_cooldown
        session.query(Settings).filter(Settings.key == "treatbot_mqtt_cooldown").update({"value": new_cooldown})
        await msg.reply(f"Treatme cooldown changed to {new_cooldown}")

    except IndexError:
        await msg.reply(f"Current cooldown is {cooldown[aio_key]} seconds.")
        return

    except ValueError:
        await msg.reply("Invalid value.")

    except Exception as e:
        print(type(e), e)
        return
