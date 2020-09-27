from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import Interval
from sqlalchemy import String
from twitchbot import Mod
from twitchbot.database.session import Base
from twitchbot.database.session import engine


class UserChatTimeLogging(Mod):
    def __init__(self) -> None:
        super().__init__()
        print("Users Database loaded")

    async def on_connected(self) -> None:
        Base.metadata.create_all(engine)


class Users(Base):
    """Storing user data"""

    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}
    user_id = Column(Integer(), primary_key=True, nullable=False)
    channel = Column(String(64), primary_key=True, nullable=False)
    user = Column(String(64))
    time_in_channel = Column(Interval(second_precision=True, day_precision=True))
    message_count = Column(Integer(), default=0)
    cheers = Column(Integer(), default=0)
    last_update = Column(DateTime(), onupdate=datetime.now)
    last_message = Column(DateTime())


class Announcements(Base):
    """Storing data for the announcements command"""

    __tablename__ = "announcements"
    __table_args__ = {"extend_existing": True}
    id = Column(Integer(), primary_key=True, nullable=False)
    text = Column(String(1024), nullable=False)
    created_date = Column(DateTime(), default=datetime.now)
    last_sent = Column(DateTime())


class Settings(Base):
    """Used for storing random bot settings"""

    __tablename__ = "settings"
    __table_args__ = {"extend_existing": True}
    id = Column(Integer(), primary_key=True)
    key = Column(String(24), nullable=False)
    value = Column(String(256), nullable=False)
