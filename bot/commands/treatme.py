from main import AddOhmsBot
from twitchbot import Command
from twitchbot import SubCommand

mqtt_topic = AddOhmsBot.MQTT.Topics.dispense_treat_toggle


@Command("treatme")
async def push_treat(msg, *args):
    if await AddOhmsBot.MQTT.send(mqtt_topic):
        await msg.reply(f"{AddOhmsBot.msg_prefix}Teleporting a treat")
    else:
        await msg.reply(f"{AddOhmsBot.msg_prefix}I couldn't do that at the moment. Sorry ☹️")


@SubCommand(push_treat, "cooldown", permission="admin")
async def treatme_cooldown(msg, *args):
    try:
        new_cooldown = int(args[0])

        # Update the database
        AddOhmsBot.MQTT.set_cooldown(mqtt_topic, new_cooldown)

        await msg.reply(f"Treatme cooldown changed to {new_cooldown}")

    except IndexError:
        # Happens if no arguments are presented
        await msg.reply(f"Current cooldown is {AddOhmsBot.MQTT.get_cooldown(mqtt_topic)} seconds.")
        return

    except ValueError:
        await msg.reply("Invalid value.")

    except Exception as e:
        print(type(e), e)
        return
