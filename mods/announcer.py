from twitchbot import (
    cfg,
    Mod,
    task_exist,
    stop_task,
    add_task,
    channels,
    ModCommand,
    Message,
)
from asyncio import sleep
from aiofile import AIOFile
import json
from datetime import datetime

json_file = "messages.json"


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

    async def load_json_file(self) -> dict:
        # Load the data file
        try:
            async with AIOFile(json_file, "r") as afp:
                data = json.loads(await afp.read())
                return data

        except FileNotFoundError:
            # Create the file because it didn't exist and return an empty dictionary
            async with AIOFile(json_file, "w+") as afp:
                await afp.write(json.dumps({}))

            return dict()

    async def save_json_file(self, data) -> None:
        # Write the messages back to the file
        try:
            async with AIOFile(json_file, "w+") as afp:
                await afp.write(json.dumps(data))

        except FileNotFoundError as e:
            print(e)

    async def timer_loop(self):
        while True:
            await sleep(self.delay)
            # This is done so the loop will continue to run and not exit out because the loop has ended
            # if done as a while enabled
            if self.enable:

                data = await self.load_json_file()

                # Make sure there are entries in the dictioary
                if len(data) == 0:
                    # Use continue instead of return so more can be added once the bot is run
                    continue

                # Returns a list of tuples of the dictionary
                sorted_data = sorted(data.items(), key=lambda x: x[1])

                # Grab the message text
                message = sorted_data[0][0]

                # Send the message
                await channels[self.chan].send_message("🤖" + message)

                # Update the last time sent of the message
                data[message] = str(datetime.now())

                await self.save_json_file(data)

    @ModCommand(name, "announce_enable", permission="admin")
    async def announce_enable(self, msg, *args):
        self.enable = True
        print("Enabling announcements.")
        await channels[self.chan].send_message(
            "🤖Announcements, announcements, ANNOUNCEMENTS!"
        )

    @ModCommand(name, "announce_disable", permission="admin")
    async def announce_disable(self, msg, *args):
        self.enable = False
        print("Disabling announcements.")
        await channels[self.chan].send_message("🤖Disabling announcements")

    @ModCommand(name, "announce_time", permission="admin")
    async def announce_time(self, msg, time: int):
        try:
            self.delay = int(time)
            self.restart_task()
            await msg.reply(f"🤖New announce time is {time} seconds")
        except ValueError:
            await msg.reply("🤖Invalid time, please use an integer in seconds")

    @ModCommand(name, "announce", permission="admin")
    async def announce(self, msg, *args):

        message = ""

        # Build the message
        for arg in args:
            message += f"{arg} "

        print(f"Adding to announce: {message}", end="")

        data = await self.load_json_file()
        data[message] = str(0)
        await self.save_json_file(data)
        print("...done")

    def restart_task(self):
        if task_exist(self.task_name):
            stop_task(self.task_name)

        add_task(self.task_name, self.timer_loop())

    async def on_connected(self):
        self.restart_task()