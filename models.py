from datetime import datetime

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Users(Base):
    """Storing user data"""

    __tablename__ = "users"
    user_id = Column(Integer(), primary_key=True, nullable=False, index=True)
    channel = Column(Integer(), primary_key=True, nullable=False, index=True)
    user = Column(String(64), unique=True)
    time_in_channel = Column(Integer(), default=0)
    message_count = Column(Integer(), default=0)
    cheers = Column(Integer(), default=0)
    last_update = Column(DateTime(), onupdate=datetime.now)
    last_message = Column(DateTime())


class Subscriptions(Base):
    """Store subscription info"""

    __tablename__ = "subscriptions"
    user_id = Column(Integer(), ForeignKey("users.user_id"), primary_key=True, nullable=False, index=True)
    channel = Column(Integer(), ForeignKey("users.channel"), primary_key=True, nullable=False, index=True)
    subscription_level = Column(String(64))
    cumulative_months = Column(Integer(), default=0)
    streak_months = Column(Integer(), default=0)


class Announcements(Base):
    """Storing data for the announcements command"""

    __tablename__ = "announcements"
    id = Column(Integer(), primary_key=True, nullable=False)
    text = Column(String(1024), nullable=False)
    created_date = Column(DateTime(), default=datetime.now)
    last_sent = Column(DateTime(), default=datetime.now)
    times_sent = Column(Integer(), default=0)
    enabled = Column(Boolean(), default=True)
    groups = Column(String(1024), nullable=True)


class Settings(Base):
    """Used for storing random bot settings"""

    __tablename__ = "settings"
    id = Column(Integer(), primary_key=True)
    key = Column(String(128), nullable=False, unique=True)
    value = Column(String(1024), nullable=False)
