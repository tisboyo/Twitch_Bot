import datetime
from asyncio import sleep

from helpers.points import Points
from helpers.points import Status
from main import bot
from twitchbot.command import ModCommand
from twitchbot.command import SubCommand
from twitchbot.message import Message
from twitchbot.modloader import Mod
from twitchbot.permission import perms

mqtt_topic_dispense = bot.MQTT.Topics.dispense_treat_toggle
mqtt_topic_treat_in_queue = bot.MQTT.Topics.treat_in_queue
trigger_emoji = "balden3TreatMe"


class Treats(Mod):
    name = "treats"

    def __init__(self):
        self.points = Points(
            emojis=6, unique_users=4, mod_commands=1, require_all=True, emoji_cap=2, timeout_seconds=60 * 10
        )
        self.reminder_enable = True
        self.ready_for_trigger = True
        self.last_lab_check = datetime.datetime.min

    async def on_raw_message(self, msg: Message):
        # If the message is a system message, we're done here
        if not msg.author or not msg.content:
            return

        emoji_count = msg.content.count(trigger_emoji)
        if emoji_count > 0:
            if bot.location != "Lab":
                # If we aren't in the Lab and we haven't said something in the last 5 minutes, let the user know
                if (self.last_lab_check + datetime.timedelta(minutes=5)) < datetime.datetime.now():
                    await msg.reply(f"{bot.msg_prefix} Sorry, no treats today. We are in the {bot.location}.")
                    self.last_lab_check = datetime.datetime.now()
                    print(self.last_lab_check)

            elif self.points.check(msg, emojis=emoji_count):
                await self.send_treat(msg)

            else:  # Check how many more we need
                status = self.points.status()

                if status.emojis_required >= status.emojis and self.reminder_enable:
                    await msg.reply(self.build_required_message(status))
                    self.reminder_enable = False
                elif status.emojis >= status.emojis_required:
                    await self.send_treat_in_queue(msg)

        else:
            # If it doesn't include a Treat, we don't care about it at all
            self.reminder_enable = True  # Allow the reminder to be sent again
            return

    @ModCommand(name, "treatmenow", permission="admin")
    async def treatme_now(self, msg: Message, *args):
        print("Force sending a treat.")
        await self.send_treat(msg)

    @ModCommand(name, "treatme")
    async def push_treat(self, msg: Message, *args):
        if perms.has_permission(msg.channel.name, str(msg.author), "admin"):
            if self.points.check(msg, mod_commands=1):
                await self.send_treat(msg)
            elif msg.args[0] == "test":
                # Use for testing the bots
                await self.send_treat_in_queue(msg)
                await sleep(3)
                await self.send_treat(msg)
            else:
                status = self.points.status()
                await msg.reply(self.build_required_message(status))
        else:
            # Check if user is on ignore list
            if bot.user_ignored(str(msg.author)):
                return

            await msg.reply(
                f"{bot.msg_prefix} NEW! Send balden3TreatMe to trigger the Treat Bot!"
            )  # TODO #136 Change phrasing eventually

    @SubCommand(push_treat, "cooldown", permission="admin")
    async def treatme_cooldown(self, msg, *args):
        try:
            new_cooldown = int(args[0])

            # Update the database
            bot.MQTT.set_cooldown(mqtt_topic_dispense, new_cooldown)

            await msg.reply(f"Treatme cooldown changed to {new_cooldown}")

        except IndexError:
            # Happens if no arguments are presented
            await msg.reply(f"Current cooldown is {bot.MQTT.get_cooldown(mqtt_topic_dispense)} seconds.")
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
        required = f"{bot.msg_prefix}Moar {trigger_emoji} "
        if req_users <= self.points.unique_users_required and self.points.unique_users_required > 0:
            required += "from moar users "
        required += "required for a treat!"

        return required

    async def send_treat(self, msg: Message) -> bool:
        if await bot.MQTT.send(mqtt_topic_dispense, 1):
            await msg.reply(f"{bot.msg_prefix}Treats!! balden3Yay balden3Yay balden3Yay")
            return True
        else:
            await msg.reply(f"{bot.msg_prefix}I ran into a problem with MQTT. Sorry ☹️")
            return False

    async def send_treat_in_queue(self, msg: Message) -> bool:
        if await bot.MQTT.send(mqtt_topic_treat_in_queue, 1):
            await msg.reply(f"{bot.msg_prefix}A treat is in the queue!!")
            return True
        else:
            await msg.reply(f"{bot.msg_prefix}A treat is in the queue!! (But there's an MQTT problem too)")
            return False
