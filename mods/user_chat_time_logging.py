import re
from datetime import datetime
from datetime import timedelta
from typing import Union

from twitchbot import cfg
from twitchbot import Channel
from twitchbot import channels
from twitchbot import Mod
from twitchbot.database.session import session

from mods.database_models import Users


class UserChatTimeLogging(Mod):
    name = "userchattimelogging"

    def __init__(self) -> None:
        super().__init__()
        print("UserChatTimeLogging loaded")
        self.user_data = dict()
        self.user_joined = dict()
        # TODO add user to joined if they send a message and aren't in the dict yet

    # async def on_connected(self) -> None:
    #     # Load the data once connected
    #     self.user_data = await load_data(self.file_name)

    async def on_channel_joined(self, channel: Channel) -> None:
        """Bot joined a channel"""
        # Set the current date and time for the user as a join time
        now = datetime.now()
        for viewer in channel.chatters.all_viewers:
            self.user_joined[viewer] = now

    async def on_user_join(self, user: str, channel: Channel) -> None:
        """User has joined the channel"""
        # Don't overwrite if the user is already here, happens if they join twice
        if user not in self.user_joined.keys():
            self.user_joined[user] = datetime.now()
            print(f"{user} has joined #{channel.name}")

    async def on_user_part(self, user: str, channel: Channel) -> None:
        """User has left the channel"""
        print(f"{user} left #{channel.name}")
        # Don't run if it's just the bot leaving
        if user != cfg.nick:
            # Make sure they are actually gone, and not a second instance
            if user not in channel.chatters.all_viewers:
                await self.user_exit(user)

    async def on_bot_shutdown(self):
        """Bot shutting down, save all of the data"""
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
                joined: datetime = self.user_joined[user]
                parted = now
                time_this_session = parted - joined

                # Update the database
                # TODO Research if adding time is possible with sqlite on update

                # Read the saved value, or just use 0 seconds timedelta because the user is new
                # total = self.user_data.get(user, None)
                # total_time = self.datetime_parse(total) or timedelta(seconds=0)

                # Save the new data back to memory
                # self.user_data[user] = str(total_time + time_this_session)
                # Save the new data to the database

                # Remove the user from the user_joined key, since they have exited the channel
                del self.user_joined[user]

        # Save the file
        # await save_data(self.file_name, self.user_data)

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
