from helpers.points import Points
from main import AddOhmsBot
from twitchbot.command import ModCommand
from twitchbot.command import SubCommand
from twitchbot.message import Message
from twitchbot.modloader import Mod

mqtt_topic = AddOhmsBot.MQTT.Topics.yay_toggle


class Yay(Mod):
    name = "yay"

    def __init__(self):
        self.points = Points(emojis=5, unique_users=2, emoji_cap=3)

    async def on_raw_message(self, msg: Message):
        # If the message is a system message, we're done here
        if not msg.author or not msg.content:
            return

        how_many_yays = msg.content.count("balden3Yay")
        if how_many_yays > 0:
            if self.points.check(msg, emojis=how_many_yays):
                await self.send_yay(msg)

        else:
            # If it doesn't include a Yay, we don't care about it at all
            return

    async def send_yay(self, msg: Message) -> bool:
        if await AddOhmsBot.MQTT.send(mqtt_topic, 1):
            await msg.reply(f"{AddOhmsBot.msg_prefix}Yay! balden3Yay balden3Yay balden3Yay")
            return True
        else:
            await msg.reply(f"{AddOhmsBot.msg_prefix}I ran into a problem with MQTT. Sorry ☹️")
            return False

    @ModCommand(name, "yay", permission="admin")
    async def yay(self, msg, *args):
        # Parent command does nothing.
        pass

    @SubCommand(yay, "cooldown", permission="admin")
    async def yay_cooldown(self, msg, *args):
        """Cooldown for yays"""
        try:
            new_cooldown = int(args[0])

            # Update the database
            AddOhmsBot.MQTT.set_cooldown(mqtt_topic, new_cooldown)

            await msg.reply(f"Treatme cooldown changed to {new_cooldown}")

        except IndexError:
            await msg.reply(f"Current cooldown is {AddOhmsBot.MQTT.get_cooldown(mqtt_topic)} seconds.")
            return

        except ValueError:
            await msg.reply("Invalid value.")

        except Exception as e:
            print(type(e), e)
            return
