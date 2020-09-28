from asyncio import sleep
from datetime import datetime

from twitchbot import add_task
from twitchbot import cfg
from twitchbot import channels
from twitchbot import Mod
from twitchbot import ModCommand
from twitchbot import stop_task
from twitchbot import task_exist
from twitchbot.database.session import session

from main import AddOhmsBot
from mods.database_models import Announcements


class AutoMessageStarterMod(Mod):
    name = "automsg"
    task_name = "automessage"

    def __init__(self):
        self.enable = True
        self.delay = 900  # seconds
        self.chan = cfg.channels[0]

    @property
    def delay(self):
        return self.__delay

    @delay.setter
    def delay(self, time: int):
        self.__delay = int(time)
        print(f"Announcement message delay is {self.delay} seconds")

    async def timer_loop(self):
        while True:
            # Try except to prevent loop from accidentally crashing, no known reasons to crash.
            try:
                await sleep(self.delay)
                # This is done so the loop will continue to run and not exit out because the loop has ended
                # if done as a while enabled
                if self.enable:

                    # data = await load_data(self.__savefile)
                    result = session.query(Announcements).order_by(Announcements.last_sent).first()

                    # Make sure there are entries in the dictioary
                    if result is None:
                        # Use continue instead of return so more can be added once the bot is run
                        continue

                    # Send the message
                    await channels[self.chan].send_message(AddOhmsBot.msg_prefix + result.text)

                    # Update the last time sent of the message
                    session.query(Announcements).filter(Announcements.id == result.id).update({"last_sent": datetime.now()})
                    session.commit()

            except Exception as e:
                print(e)

    @ModCommand(name, "announce_enable", permission="admin")
    async def announce_enable(self, msg, *args):
        self.enable = True
        print("Enabling announcements.")
        await channels[self.chan].send_message(f"{AddOhmsBot.msg_prefix}Announcements, announcements, ANNOUNCEMENTS!")

    @ModCommand(name, "announce_disable", permission="admin")
    async def announce_disable(self, msg, *args):
        self.enable = False
        print("Disabling announcements.")
        await channels[self.chan].send_message(f"{AddOhmsBot.msg_prefix}Disabling announcements")

    @ModCommand(name, "announce_time", permission="admin")
    async def announce_time(self, msg, time: int = 0):
        try:
            # Make sure we receive a positive number
            if int(time) < 1:
                raise ValueError

            self.delay = int(time)
            self.restart_task()
            await msg.reply(f"{AddOhmsBot.msg_prefix}New announce time is {time} seconds")
        except ValueError:
            await msg.reply(f"{AddOhmsBot.msg_prefix}Invalid time, please use an integer in seconds")

    @ModCommand(name, "announce", permission="admin")
    async def announce(self, msg, *args):

        message = ""

        # Build the message
        for arg in args:
            message += f"{arg} "

        print(f"Adding to announce: {message}", end="")

        announcement_object = Announcements(text=message)
        session.add(announcement_object)
        session.commit()

        print("...done")

    def restart_task(self):
        if task_exist(self.task_name):
            stop_task(self.task_name)

        add_task(self.task_name, self.timer_loop())

    async def on_connected(self):
        self.restart_task()
