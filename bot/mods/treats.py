from helpers.points import Points
from main import AddOhmsBot
from twitchbot.command import ModCommand
from twitchbot.command import SubCommand
from twitchbot.enums import CommandContext
from twitchbot.modloader import Mod

mqtt_topic = AddOhmsBot.MQTT.Topics.dispense_treat_toggle


class Treats(Mod):
    name = "yay"

    def __init__(self):
        self.points = Points(emojis=5, unique_users=2, mod_commands=1, require_all=True, emoji_cap=3)

    @ModCommand(name, "treatme", context=CommandContext.BOTH, permission="admin")
    async def push_treat(self, msg, *args):
        if await AddOhmsBot.MQTT.send(mqtt_topic):
            await msg.reply(f"{AddOhmsBot.msg_prefix}Teleporting a treat")
        else:
            await msg.reply(f"{AddOhmsBot.msg_prefix}I couldn't do that at the moment. Sorry ☹️")

    @SubCommand(push_treat, "cooldown", permission="admin")
    async def treatme_cooldown(self, msg, *args):
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
