import datetime
from asyncio import sleep
from json import dumps

from helpers.points import Points
from helpers.points import Status
from main import bot
from twitchbot.command import ModCommand
from twitchbot.command import SubCommand
from twitchbot.message import Message
from twitchbot.modloader import Mod
from twitchbot.permission import perms
from twitchbot.util.task_util import add_task
from twitchbot.util.task_util import stop_task
from twitchbot.util.task_util import task_exist

mqtt_topic_dispense = bot.MQTT.Topics.dispense_treat_toggle
mqtt_topic_treat_in_queue = bot.MQTT.Topics.treat_in_queue
mqtt_topic_treat_status = bot.MQTT.Topics.treat_status
trigger_emoji = "balden3TreatMe"


class Treats(Mod):
    name = "treats"
    task_name = "treats_task"

    def __init__(self):
        self.points = Points(
            emojis=4, unique_users=2, mod_commands=1, require_all=True, emoji_cap=2, timeout_seconds=60 * 10
        )
        self.reminder_enable = False
        self.ready_for_trigger = True
        self.treat_disabled_check = datetime.datetime.min
        self.treat_in_queue = False
        self.last_treat_reminder = datetime.datetime.min

    async def timer_loop(self):
        print("Timer loop started")
        while True:
            now = datetime.datetime.now()

            # Check if the last use has expired, and reset it if so.
            if self.points.timeout_expire > now:
                self.treat_in_queue = False
                await bot.MQTT.send(mqtt_topic_treat_in_queue, 0)

            if self.treat_in_queue:
                if now > (self.last_treat_reminder + datetime.timedelta(seconds=5)):
                    if await bot.MQTT.send(mqtt_topic_treat_in_queue, 1):
                        print("A treat is still in the queue, reminder sent.")
                    else:
                        print("A treat is still in the queue, MQTT problem.")

                    self.last_treat_reminder = now

            else:
                # Stop the loop since there isn't a treat in the queue.
                stop_task(self.task_name)
                print("Stopping treat reminder loop")

            await sleep(1)

    async def on_raw_message(self, msg: Message):
        # If the message is a system message, we're done here
        if not msg.author or not msg.content:
            return

        emoji_count = msg.content.count(trigger_emoji)
        if emoji_count > 0:
            if not bot.treats_enabled:
                # If treatbot is disabled and we haven't said something in the last 5 minutes, let the user know
                if (self.treat_disabled_check + datetime.timedelta(minutes=5)) < datetime.datetime.now():
                    await msg.reply(f"{bot.msg_prefix} Sorry, no treats today.")
                    self.treat_disabled_check = datetime.datetime.now()

            elif self.points.check(msg, emojis=emoji_count):
                # This can ONLY run when the mod_command has also been run
                # So sending the actual treat is the appropriate action.
                await self.send_treat_status(self.points.status())
                await self.send_treat(msg)

            else:  # Check how many more we need
                # Make sure to refresh the status here because it was modified with self.points.check
                status = self.points.status()
                if status.emojis_required > status.emojis and self.reminder_enable:
                    await self.send_treat_status(status)
                    await msg.reply(self.build_required_message(status))
                    self.reminder_enable = False
                elif status.emojis >= status.emojis_required:
                    await self.send_treat_status(status)
                    #await self.send_treat_in_queue(msg)
                    await self.send_treat(msg)

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
                f"{bot.msg_prefix} Send balden3TreatMe to help trigger the Treat Bot!"
            )  # TODO #136 Change phrasing eventually

    @SubCommand(push_treat, "enable", permission="admin")
    async def treatbot_enable(self, msg, *args):
        bot.treats_enabled = True
        await msg.reply(f"{bot.msg_prefix} Treats are enabled. balden3Yay balden3Yay balden3TreatMe balden3TreatMe")

    @SubCommand(push_treat, "disable", permission="admin")
    async def treatbot_disable(self, msg, *args):
        bot.treats_enabled = False
        await msg.reply(f"{bot.msg_prefix} Treats are disabled. 😔")

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
        self.treat_in_queue = False
        if await bot.MQTT.send(mqtt_topic_dispense, 1):
            await msg.reply(f"{bot.msg_prefix}Treats!! balden3Yay balden3Yay balden3Yay")

            # Reset the treat in queue, if the first MQTT message failed, this one will too, so no use checking.
            await bot.MQTT.send(mqtt_topic_treat_in_queue, 0)

            return True
        else:
            await msg.reply(f"{bot.msg_prefix}I ran into a problem with MQTT. Sorry ☹️")
            return False

    async def send_treat_in_queue(self, msg: Message) -> bool:
        self.treat_in_queue = True
        self.last_treat_reminder = datetime.datetime.now()  # Remember when we sent the initial reminder
        add_task(self.task_name, self.timer_loop())  # Start the loop for reminders
        if await bot.MQTT.send(mqtt_topic_treat_in_queue, 1):
            await msg.reply(f"{bot.msg_prefix}A treat is in the queue!!")
            return True
        else:
            await msg.reply(f"{bot.msg_prefix}A treat is in the queue!! (But there's an MQTT problem too)")
            return False

    async def send_treat_status(self, status: Status) -> bool:
        status_d = dict(current=status.emojis, needed=status.emojis_required)
        status_d["complete"] = True if status.emojis >= status.emojis_required else False
        status_json = dumps(status_d)
        if await bot.MQTT.send(mqtt_topic_treat_status, status_json):
            return True
        else:
            print("MQTT Error sending treat status.")
            return False

    def restart_task(self):
        if task_exist(self.task_name):
            stop_task(self.task_name)

        add_task(self.task_name, self.timer_loop())

    # async def on_connected(self):
    #     self.restart_task()
