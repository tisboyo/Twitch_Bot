from datetime import date
from datetime import datetime

from aiofile import AIOFile
from twitchbot import Channel
from twitchbot import Message
from twitchbot import Mod
from twitchbot import PubSubData
from twitchbot.database.session import session

from data import load_data
from data import save_data
from mods.database_models import Users


class TwitchLog(Mod):
    name = "twitchlog"

    def __init__(self):
        super().__init__()
        print("TwitchLog loaded")
        self.user_data = dict()

    async def on_raw_message(self, msg: Message):
        """Log raw the actual chat to {date}-{channel_name}.log"""
        if True:
            async with AIOFile(f"irc_logs/{date.today().isoformat()}-{msg.channel_name}.log", "a") as afp:
                await afp.write(f"{datetime.now().isoformat()}:{msg} \n")
                await afp.fsync()

        # If the message is a system message, we're done here
        if not msg.author:
            return

    # async def on_connected(self):
    #     """Load user data from file when connected"""
    #     print("Loading user data from json file...", end="")
    #     self.user_data = await load_data("user")
    #     print("done")

    async def on_channel_raided(self, channel: Channel, raider: str, viewer_count: int) -> None:
        """Log channel raid"""

        raid_data = await load_data("raided")

        raid_data[datetime.now().isoformat()] = (raider, viewer_count)

        await save_data("raided", raid_data)

    async def on_channel_points_redemption(self, msg: Message, reward: str):
        """Log channel points redemptions"""
        channel_point_data = await load_data("channel_points")
        channel_point_data[datetime.now().isoformat()] = (msg.author, msg.msg_id, msg.raw_msg, msg.normalized_content)
        await save_data("channel_points", channel_point_data)

    async def on_pubsub_received(self, raw: PubSubData):
        # Dump to a log file
        async with AIOFile("pubsub.log", "a") as afp:
            data = f"{datetime.now().isoformat()}:{raw.raw_data}"
            await afp.write(data + "\n")
            await afp.fsync()

    async def on_pubsub_bits(self, raw: PubSubData, data) -> None:
        """Send MQTT push when a us4er redeems bits"""
        """
        print(raw.message_dict)
        {'data':
            {'user_name': 'tisboyo', 'channel_name': 'baldengineer',
            'user_id': '461713054', 'channel_id': '125957551', 'time': '2020-09-20T02:48:34.819702158Z',
            'chat_message': 'cheer1', 'bits_used': 1, 'total_bits_used': 2,
            'is_anonymous': False, 'context': 'cheer', 'badge_entitlement': None},
        'version': '1.0',
        'message_type': 'bits_event',
        'message_id': '5a2da2f4-a6b5-5d23-b7cc-839a3ea5140c'
        }
        """
        # bits = await load_data("bits")
        # bits[datetime.now().isoformat()] = raw.message_dict
        # await save_data("bits", bits)

        user_id = raw.message_dict["data"]["user_id"]
        server_id = raw.message_dict["data"]["channel_id"]
        bits_used = raw.message_dict["data"]["bits_used"]

        rows_affected = (
            session.query(Users)
            .filter(Users.user_id == user_id, Users.channel == server_id)
            .update({"cheers": Users.cheers + bits_used, "last_message": datetime.now()})
        )

        # If the user doesn't exist, insert them
        if not rows_affected:
            user_object = Users(
                user_id=user_id,
                channel=server_id,
                user=raw.message_dict["data"]["user_name"],
                message_count=1,
                cheers=bits_used,
            )
            session.add(user_object)

        session.commit()
