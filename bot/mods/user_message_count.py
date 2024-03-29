from datetime import datetime
from datetime import timedelta
from json import dumps

from main import bot
from mods._database import session
from mqtt import MqttTopics
from sqlalchemy.exc import DatabaseError
from sqlalchemy.exc import PendingRollbackError
from twitchbot import Message
from twitchbot import Mod

from models import Users

first_time_chatter_topic = MqttTopics.first_time_chatter


class UserMessageCount(Mod):
    name = "usermessagecount"

    def __init__(self) -> None:
        super().__init__()
        print("UserMessageCount loaded")
        self.last_raid = datetime.min

    async def on_raw_message(self, msg: Message) -> None:
        """Increment the user message counter"""

        # Make sure the user actually sent a message,and it's not a whisper.
        if not msg.is_user_message or msg.is_whisper:
            return

        user_id = msg.tags.user_id
        server_id = msg.tags.room_id
        rows_affected = None

        try:
            rows_affected = (
                session.query(Users)
                .filter(Users.user_id == user_id, Users.channel == server_id)
                .update({"message_count": Users.message_count + 1, "last_message": datetime.now()})
            )
        except (DatabaseError, PendingRollbackError) as e:
            print(f"DATABASE ERROR: {type(e)=} {e.orig.msg=} {e.statement=} {e.params=}")
            session.rollback()
            rows_affected = (
                session.query(Users)
                .filter(Users.user_id == user_id, Users.channel == server_id)
                .update({"message_count": Users.message_count + 1, "last_message": datetime.now()})
            )

        # If the user doesn't exist, insert them
        if not rows_affected:
            user_object = Users(user_id=user_id, channel=server_id, user=msg.author, message_count=1)
            session.add(user_object)

            # Added for #155
            # If we have had a raid in the last 60 seconds, don't send anything for the new users,
            # even thought they got inserted into the database.
            if (self.last_raid + timedelta(seconds=60)) < datetime.now():
                if not bot.user_ignored(msg.author):
                    await bot.MQTT.send(
                        first_time_chatter_topic, dumps({"author": msg.author, "timestamp": str(datetime.now())})
                    )
                    print(f"New user {msg.author} sent to MQTT.")

        session.commit()
