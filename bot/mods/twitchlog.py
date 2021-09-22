from datetime import date
from datetime import datetime

from aiofile import AIOFile
from data import load_data
from data import save_data
from mods._database import session
from twitchbot import cfg
from twitchbot import Message
from twitchbot import Mod
from twitchbot import ModCommand
from twitchbot import PubSubData

from models import RaidLog
from models import Subscriptions
from models import Users


class TwitchLog(Mod):
    name = "twitchlog"

    def __init__(self):
        super().__init__()
        print("TwitchLog loaded")
        self.user_data = dict()

    async def on_raw_message(self, msg: Message):
        """Log raw the actual chat to {date}-{channel_name}.log"""
        if True:
            async with AIOFile(f"irc_logs/{date.today().isoformat()}-{cfg.channels[0]}.log", "a") as afp:
                await afp.write(f"{datetime.now().isoformat()}:{msg} \n")
                await afp.fsync()

        # If the message is a system message, we're done here
        if not msg.author:
            return

    # TODO REMOVE THIS COMMAND
    @ModCommand(name, "convert_raid_log", permission="admin")
    async def convert_raid_log(self, msg: Message):
        raid_data = await load_data("raided")
        for each in raid_data:
            date = datetime.fromisoformat(each)
            raider = raid_data[each][0]
            viewers = raid_data[each][1]

            insert = RaidLog(raider=raider, viewers=viewers, timestamp=date)
            session.add(insert)
            session.commit()

        await save_data("raided", {})

        await msg.reply("Please, don't do that again. (It may duplicate the data) @tisboyo, remove this command")

    async def on_channel_points_redemption(self, msg: Message, reward: str):
        """Log channel points redemptions"""
        channel_point_data = await load_data("channel_points")
        channel_point_data[datetime.now().isoformat()] = (msg.author, msg.msg_id, msg.raw_msg, msg.normalized_content)
        await save_data("channel_points", channel_point_data)

    async def on_pubsub_received(self, raw: PubSubData):
        # Dump to a log file
        async with AIOFile(f"pubsub_logs/{date.today().isoformat()}-{cfg.channels[0]}.log", "a") as afp:
            data = f"{datetime.now().isoformat()}:{raw.raw_data}"
            await afp.write(data + "\n")
            await afp.fsync()

        if len(raw.message_data) == 0:
            # Happens at startup, and possibly other times.
            pass

        elif raw.is_channel_points_redeemed:
            # Channel points received
            pass
        elif raw.is_bits:  # Bits receieved
            # Bits received, nothing to do here
            pass
        elif raw.is_moderation_action and raw.moderation_action == "raid":
            # Raided another channel
            pass
        elif raw.is_moderation_action and raw.moderation_action == "ban":
            # User banned
            print(f"{raw.args[0]} banned by {raw.created_by}.")
        elif raw.is_moderation_action and raw.moderation_action == "unban":
            print(f"{raw.args[0]} unbanned by {raw.created_by}.")
        elif raw.is_moderation_action and raw.moderation_action == "clear":
            # Chat as cleared by a moderator
            async with AIOFile(f"irc_logs/{date.today().isoformat()}-{cfg.channels[0]}.log", "a") as afp:
                data = f"{datetime.now().isoformat()}:{raw.raw_data}"
                await afp.write("CHAT CLEARED!".center(80, "*") + "\n")
                await afp.fsync()
            print("Chat was cleared by a moderator.")

        else:
            # Unknown pubsub received, print out the data
            print(f"Unknown pubsub received: {raw.message_data}")

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
        username = raw.message_dict["data"]["user_name"]
        server_id = raw.message_dict["data"]["channel_id"]
        bits_used = raw.message_dict["data"]["bits_used"]
        if raw.message_dict["data"]["is_anonymous"]:
            user_id = "407665396"  # AnAnonymousCheerer
            username = "AnAnonymousCheerer"

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
                user=username,
                message_count=1,
                cheers=bits_used,
            )
            session.add(user_object)

        session.commit()

    async def on_pubsub_subscription(self, raw: PubSubData, data):
        """Twitch subscription event"""

        """
        print(raw.message_dict)
        {'benefit_end_month': 0, 'user_name': 'tisboyo', 'display_name': 'tisboyo', 'channel_name': 'baldengineer',
        'user_id': '461713054', 'channel_id': '125957551', 'time': '2020-09-27T20:01:35.385520498Z',
        'sub_message': {'message': '', 'emotes': None}, 'sub_plan': 'Prime', 'sub_plan_name': '104 Capacitor Level Sub',
        'months': 0, 'cumulative_months': 4, 'streak_months': 4, 'context': 'resub', 'is_gift': False,
        'multi_month_duration': 0}

        print(raw.raw_data)
        {'type': 'MESSAGE', 'data': {'topic': 'channel-subscribe-events-v1.125957551',
        'message': '{"benefit_end_month":0,"user_name":"tisboyo","display_name":"tisboyo","channel_name":"baldengineer",
        "user_id":"461713054","channel_id":"125957551","time":"2020-09-27T20:01:35.385520498Z",
        "sub_message":{"message":"","emotes":null},"sub_plan":"Prime","sub_plan_name":"104 Capacitor Level Sub",
        "months":0,"cumulative_months":4,"streak_months":4,"context":"resub","is_gift":false,"multi_month_duration":0}'}}
        """

        if raw.message_dict["is_gift"]:  # A gift subscription
            user_id = raw.message_dict["recipient_id"]
            # Add count to the user for gifting a sub
            gifter_id = int(raw.message_dict["user_id"])
            channel_id = int(raw.message_dict["channel_id"])
            user_name = raw.message_dict["recipient_user_name"]
            session.query(Users).filter(Users.user_id == gifter_id, Users.channel == channel_id).update(
                {Users.subs_gifted: Users.subs_gifted + 1}
            )
            session.commit()  # Fix for #222, changes weren't being commited to the database in time.

        else:  # A regular subscription
            user_id = raw.message_dict["user_id"]
            user_name = raw.message_dict["user_name"]

        cumulative_months = raw.message_dict["cumulative_months"] if "cumulative_months" in raw.message_dict else 0
        streak_months = raw.message_dict["streak_months"] if "streak_months" in raw.message_dict else 0

        # In both gift and regular sub
        server_id = raw.message_dict["channel_id"]
        sub_level = raw.message_dict["sub_plan"]

        rows_affected = (
            session.query(Subscriptions)
            .filter(Subscriptions.user_id == user_id, Subscriptions.channel == server_id)
            .update(
                {"subscription_level": sub_level, "cumulative_months": cumulative_months, "streak_months": streak_months}
            )
        )

        # Add row if one wasn't updated.
        if not rows_affected:
            if not session.query(Users).filter(Users.user_id == user_id, Users.channel == server_id).one_or_none():
                # Make sure the user that is getting the sub is in the Users table. Fix for #241
                user_object = Users(user_id=user_id, channel=server_id, user=user_name)
                session.add(user_object)
                session.commit()

            sub_object = Subscriptions(
                user_id=user_id,
                channel=server_id,
                subscription_level=sub_level,
                cumulative_months=cumulative_months,
                streak_months=streak_months,
            )
            session.add(sub_object)

        # Up one level of indentation so it can commit the above update if it succeeded
        session.commit()
