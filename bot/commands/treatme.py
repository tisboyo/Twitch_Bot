from main import AddOhmsBot
from twitchbot import Command
from twitchbot import SubCommand

# Key that is sent to Adafruit.IO
aio_key = "stream/dispense-treat-toggle"


@Command("treatme")
async def push_treat(msg, *args):
    if await AddOhmsBot.MQTT.send(aio_key):
        await msg.reply(f"{AddOhmsBot.msg_prefix}Teleporting a treat")
    else:
        await msg.reply(f"{AddOhmsBot.msg_prefix}I couldn't do that at the moment. Sorry ☹️")


@SubCommand(push_treat, "cooldown", permission="admin")
async def treatme_cooldown(msg, *args):
    try:
        new_cooldown = int(args[0])

        # Update the database
        AddOhmsBot.MQTT.set_cooldown(aio_key, new_cooldown)

        await msg.reply(f"Treatme cooldown changed to {new_cooldown}")

    except IndexError:
        await msg.reply(f"Current cooldown is {AddOhmsBot.MQTT.get_cooldown(aio_key)} seconds.")
        return

    except ValueError:
        await msg.reply("Invalid value.")

    except Exception as e:
        print(type(e), e)
        return
