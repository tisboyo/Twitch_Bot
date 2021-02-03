from helpers.points import Points
from helpers.points import Status
from main import AddOhmsBot
from twitchbot.command import ModCommand
from twitchbot.command import SubCommand
from twitchbot.enums import CommandContext
from twitchbot.message import Message
from twitchbot.modloader import Mod

mqtt_topic = AddOhmsBot.MQTT.Topics.dispense_treat_toggle
trigger_emoji = "balden3TreatMe"


class Treats(Mod):
    name = "treats"

    def __init__(self):
        self.points = Points(
            emojis=6, unique_users=4, mod_commands=1, require_all=True, emoji_cap=2, timeout_seconds=60 * 10
        )
        self.reminder_enable = True
        self.ready_for_trigger = True

    async def on_raw_message(self, msg: Message):
        # If the message is a system message, we're done here
        if not msg.author or not msg.content:
            return

        emoji_count = msg.content.count(trigger_emoji)
        if emoji_count > 0:
            if self.points.check(msg, emojis=emoji_count):
                await self.send_treat(msg)
            else:  # Check how many more we need
                status = self.points.status()

                if status.emojis_required >= status.emojis and self.reminder_enable:
                    await msg.reply(f"{AddOhmsBot.msg_prefix} {self.build_required_message(status)}")
                    self.reminder_enable = False
                elif status.emojis >= status.emojis_required:
                    await msg.reply(f"{AddOhmsBot.msg_prefix} A treat is in the queue!!")

        else:
            # If it doesn't include a Yay, we don't care about it at all
            self.reminder_enable = True  # Allow the reminder to be sent again
            return

    @ModCommand(name, "treatme", context=CommandContext.BOTH, permission="admin")
    async def push_treat(self, msg, *args):
        if self.points.check(msg, mod_commands=1):
            await self.send_treat(msg)
        else:
            status = self.points.status()
            await msg.reply(self.build_required_message(status))

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

    def build_required_message(self, status: Status) -> str:
        """Build a message to send to chat with requirements to get a treat"""

        req_users = self.points.unique_users_required - len(status.unique_users["emojis"])
        # Build message to send to chat
        required = f"{AddOhmsBot.msg_prefix}Moar {trigger_emoji} "
        if req_users <= self.points.unique_users_required and self.points.unique_users_required > 0:
            required += "from moar users "
        required += "required for a treat!"

        return required

    async def send_treat(self, msg: Message) -> bool:
        if await AddOhmsBot.MQTT.send(mqtt_topic, 1):
            await msg.reply(f"{AddOhmsBot.msg_prefix}Treats!! balden3Yay balden3Yay balden3Yay")
            return True
        else:
            await msg.reply(f"{AddOhmsBot.msg_prefix}I ran into a problem with MQTT. Sorry ☹️")
            return False
