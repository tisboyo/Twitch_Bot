from twitchbot import (
    cfg,
    Mod,
    task_exist,
    stop_task,
    add_task,
    channels,
    Command,
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
    delay = 900  # seconds

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
            chan = cfg.channels[0]
            await channels[chan].send_message("🤖" + message)

            # Update the last time sent of the message
            data[message] = str(datetime.now())

            await self.save_json_file(data)

    @Command("announce", permission="admin")
    async def announce(self, *args):

        msg = ""

        # Build the message
        for arg in args:
            msg += f"{arg} "

        print(f"Adding to announce: {msg}", end="")
        # For some reason self isn't being passed properly in this function
        data = await AutoMessageStarterMod.load_json_file(self)
        data[msg] = str(0)
        await AutoMessageStarterMod.save_json_file(self, data)
        print("...done")

    async def on_connected(self):
        if task_exist(self.task_name):
            stop_task(self.task_name)

        add_task(self.task_name, self.timer_loop())
