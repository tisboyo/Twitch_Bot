from datetime import datetime
from typing import Union

from mods._database import session
from twitchbot import cfg
from twitchbot import Channel
from twitchbot import channels
from twitchbot import get_user_id
from twitchbot import Message
from twitchbot import Mod

from models import Users


class UserChatTimeLogging(Mod):
    name = "userchattimelogging"

    def __init__(self) -> None:
        super().__init__()
        print("UserChatTimeLogging loaded")
        self.user_data = dict()
        self.user_joined = dict()
        self.channel_ids = dict()
        self.user_ids = dict()

    async def on_raw_message(self, msg: Message):
        """Add the user to the dictionary if they send a message before the join event"""
        # Not counting whispers as being active
        if msg.is_whisper:
            return

        # If it is a system message from the user,
        # the tags aren't there so we have to query the user_id
        if not msg.is_user_message:
            user_id = await get_user_id(msg.author)
        else:
            user_id = msg.tags.user_id

        # Add the user to the user_joined dictionary if they aren't already in it
        if msg.author not in self.user_joined.keys():
            self.user_joined[(msg.author, user_id)] = datetime.now()

    async def on_channel_joined(self, channel: Channel) -> None:
        """Bot joined a channel"""
        # Call user joind for all users currently in th channel
        for user_name in channel.chatters.all_viewers:
            await self.on_user_join(user_name, channel, commit=False)

        # Waited to commit so only one database commit was done on the server join
        session.commit()

    async def on_user_join(self, user_name: str, channel: Channel, commit: bool = True) -> None:
        """User has joined the channel"""

        # get_user_info is cached by the bot, so only one actual request per user is sent to the api
        user_id = await get_user_id(user_name)
        channel_id = await get_user_id(channel.name)

        # Don't overwrite if the user is already here, happens if they join twice
        if (user_name, user_id) not in self.user_joined.keys():
            in_database = session.query(Users).filter(Users.user_id == user_id, Users.channel == channel_id).one_or_none()

            # If the user isn't in the database insert them so we can find them later
            if not in_database:
                user_object = Users(user_id=user_id, channel=channel_id, user=user_name)
                session.add(user_object)
                if commit:
                    session.commit()

            self.user_joined[(user_name, user_id)] = datetime.now()
            print(f"{datetime.now().isoformat()}: {user_name} has joined #{channel.name}, in database: {bool(in_database)}")

    async def on_user_part(self, user: str, channel: Channel) -> None:
        """User has left the channel"""
        print(f"{datetime.now().isoformat()}: {user} left #{channel.name}")

        # Don't run if it's just the bot leaving
        if user != cfg.nick:
            # Make sure they are actually gone, and not a second instance
            if user not in channel.chatters.all_viewers:
                await self.user_exit(user, channel)

    async def on_bot_shutdown(self):
        """Bot shutting down, save all of the data"""
        print("Syncing UserChatTimeLogging")

        for chan in channels:
            users = channels[chan].chatters.all_viewers
            await self.user_exit(users, channels[chan])

    async def user_exit(self, users: Union[str, frozenset], channel: Channel):

        now = datetime.now()

        # If only a single user is passed, convert it to a frozenset as if a list of users was passed
        if isinstance(users, str):
            users = frozenset([users])

        for user_name in users:
            # Build a tuple to compare
            user = (user_name, await get_user_id(user_name))

            # Check to make sure the user is still in the user_joined to prevent errors
            if user in self.user_joined.keys():
                # Calculate the time in the channel for this session
                joined: datetime = self.user_joined[user]
                parted = now
                time_this_session = parted - joined

                _, user_id = user
                channel_id = int(await get_user_id(channel.name))

                # Update the database
                # Adding time objects is not possible with sqlite, so using an integer to track seconds
                rows_affected = (
                    session.query(Users)
                    .filter(Users.user_id == user_id, Users.channel == channel_id)
                    .update({"time_in_channel": Users.time_in_channel + time_this_session.seconds})
                )

                if not rows_affected:
                    user_object = Users(
                        user_id=user_id, channel=channel_id, user=user_name, time_in_channel=time_this_session.seconds
                    )
                    session.add(user_object)

                # Remove the user from the user_joined key, since they have exited the channel
                del self.user_joined[user]

        # Commit the changes
        session.commit()
