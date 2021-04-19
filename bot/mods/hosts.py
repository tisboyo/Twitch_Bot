from asyncio import sleep
from datetime import date
from datetime import datetime

from aiofile import AIOFile
from aiohttp import ClientSession
from main import bot
from twitchbot import Mod
from twitchbot.channel import channels
from twitchbot.config import cfg
from twitchbot.config import get_client_id
from twitchbot.config import get_oauth
from twitchbot.util.task_util import add_task
from twitchbot.util.task_util import stop_task
from twitchbot.util.task_util import task_exist


class HostsMod(Mod):
    name = "hostsmod"
    task_name = "hostsmod"

    def __init__(self):
        super().__init__()
        self.hosters = list()

    async def timer_loop(self):

        # Grab the UID of channel 0
        headers = {
            "client-id": get_client_id(),
            "Authorization": f"Bearer {get_oauth(remove_prefix=True)}",
        }

        channel = cfg.channels[0]

        async with ClientSession() as session:
            params = [("login", channel)]
            r = await session.get(url=f"https://api.twitch.tv/helix/users?login={channel}", headers=headers)
            data = await r.json()
            try:
                channel_id = data["data"][0]["id"]
            except KeyError:
                print(data["error"], data["status"], data["message"])
                return

        while True:
            while bot.live:
                try:
                    # Try except to prevent loop from accidentally crashing, no known reasons to crash.
                    url = "https://tmi.twitch.tv/hosts"
                    params = [("include_logins", "1")]

                    # Add channel message came from to the parameters
                    params.append(("target", channel_id))

                    async with ClientSession() as session:
                        response = await session.get(url=url, params=params, headers=headers)

                        if response.status == 401:
                            print("OAuth token error.")
                            return

                        # Get the response as a json object.
                        response_js = await response.json()
                        hosts = response_js["hosts"]

                        if len(hosts) > 0:  # Being hosted
                            for host in hosts:
                                hoster = host["host_display_name"]
                                if hoster not in self.hosters:
                                    self.hosters.append(hoster)
                                    print(f"Hosted by {hoster}")

                                    # Send to channel
                                    await channels[cfg.channels[0]].send_message(
                                        f"{bot.msg_prefix} Thanks for hosting {hoster}"
                                    )

                                    # Log to json file
                                    async with AIOFile(
                                        f"irc_logs/{date.today().isoformat()}-{cfg.channels[0]}-hosted.log", "a"
                                    ) as afp:
                                        await afp.write(f"{datetime.now().isoformat()}:{hoster} \n")
                                        await afp.fsync()

                                    # Don't spam the channel
                                    await sleep(1)

                            # Overwrite the hosters seen so if someone stops hosting they are removed from the list
                            self.hosters = [host["host_display_name"] for host in hosts]

                    await sleep(60)  # Only check once a minute

                except Exception as e:
                    print(e)

            await sleep(60)  # Sleep before checking if live again.

    def restart_task(self):
        if task_exist(self.task_name):
            stop_task(self.task_name)

        # Temporarily disable until a new endpoint can be found. TODO
        # add_task(self.task_name, self.timer_loop())

    async def on_connected(self):
        self.restart_task()
