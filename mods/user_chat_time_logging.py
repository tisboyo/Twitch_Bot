from datetime import datetime, timedelta

from data import load_data, save_data

from twitchbot import Mod, Channel, cfg, channels
import re
from typing import Union


class UserChatTimeLogging(Mod):
    def __init__(self) -> None:
        super().__init__()
        print("UserChatTimeLogging loaded")
        self.user_data = dict()
        self.user_joined = dict()
        self.file_name = "user_chat_time"

    async def on_connected(self) -> None:
        # Load the data once connected
        self.user_data = await load_data(self.file_name)
        pass

    async def on_channel_joined(self, channel: Channel) -> None:
        # Bot joined a channel
        # Set the current date and time for the user as a join time
        now = datetime.now()
        for viewer in channel.chatters.all_viewers:
            self.user_joined[viewer] = now

    async def on_user_join(self, user: str, channel: Channel) -> None:
        # User has joined the channel
        # Don't overwrite if the user is already here, happens if they join twice
        if user not in self.user_joined.keys():
            self.user_joined[user] = datetime.now()
            print(f"{user} has joined #{channel.name}")

    async def on_user_part(self, user: str, channel: Channel) -> None:
        # User has left the channel
        print(f"{user} left #{channel.name}")
        # Don't run if it's just the bot leaving
        if user != cfg.nick:
            if user not in channel.chatters.all_viewers:
                await self.user_exit(user)

    async def on_bot_shutdown(self):
        # Bot shutting down, save all of the data
        print("Syncing UserChatTimeLogging")

        viewers = channels[cfg.channels[0]].chatters.all_viewers

        await self.user_exit(viewers)

    async def user_exit(self, users: Union[str, frozenset]):

        now = datetime.now()

        # If only a single user is passed, convert it to a frozenset as if a list of users was passed
        if isinstance(users, str):
            users = frozenset([users])

        for user in users:
            # Check to make sure the user is still in the user_joined to prevent errors
            if user in self.user_joined.keys():
                # Calculate the time in the channel for this session
                joined = self.user_joined[user]
                parted = now
                time_this_session = parted - joined

                # Read the saved value, or just use 0 seconds timedelta because the user is new
                total = self.user_data.get(user, None)
                total_time = self.datetime_parse(total) or timedelta(seconds=0)

                # Save the new data back to memory
                self.user_data[user] = str(total_time + time_this_session)

                # Remove the user from the user_joined key, since they have exited the channel
                del self.user_joined[user]

        # Save the file
        await save_data(self.file_name, self.user_data)

    def datetime_parse(self, timestr: str) -> timedelta:
        """Function to convert a string from a timedelta back into a timedelta object"""
        if timestr is None:
            return False
        elif "day" in timestr:
            m = re.match(r"(?P<days>[-\d]+) day[s]*, (?P<hours>\d+):(?P<minutes>\d+):(?P<seconds>\d[\.\d+]*)", timestr)
        else:
            m = re.match(r"(?P<hours>\d+):(?P<minutes>\d+):(?P<seconds>\d[\.\d+]*)", timestr)
        # Pack it how the timedelta function expects it
        values = {key: float(val) for key, val in m.groupdict().items()}
        # Unpack the data
        ret = timedelta(**values)
        return ret
