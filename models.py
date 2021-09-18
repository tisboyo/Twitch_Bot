import random
import string
from datetime import datetime

from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_json import NestedMutableJson

Base = declarative_base()


def randomword():
    return "".join(random.choice(string.ascii_letters + string.digits) for i in range(32))


class Users(Base):
    """Storing user data"""

    __tablename__ = "users"
    user_id = Column(Integer(), primary_key=True, nullable=False, index=True)
    channel = Column(Integer(), primary_key=True, nullable=False, index=True)
    user = Column(String(64))
    time_in_channel = Column(Integer(), default=0)
    message_count = Column(Integer(), default=0)
    cheers = Column(Integer(), default=0)
    last_update = Column(DateTime(), onupdate=datetime.now)
    last_message = Column(DateTime())
    subs_gifted = Column(Integer(), default=0)


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
    category = Column(Integer(), ForeignKey("announcements_categories.id", name="announcement_id"), default=1)


class AnnouncementCategories(Base):
    """Announcement Categories"""

    __tablename__ = "announcements_categories"
    id = Column(Integer(), primary_key=True, nullable=False)
    name = Column(String(1024), nullable=False)


class Settings(Base):
    """Used for storing random bot settings"""

    __tablename__ = "settings"
    id = Column(Integer(), primary_key=True)
    key = Column(String(128), nullable=False, unique=True)
    value = Column(String(1024), nullable=False)


class Wigs(Base):
    """We have to keep our wigs somewhere..."""

    __tablename__ = "wigs"
    id = Column(Integer(), primary_key=True)
    wig_name = Column(String(128), nullable=False, unique=True)
    enabled = Column(Boolean())


class LinksToDiscordIgnoreList(Base):
    """List of twitch users to ignore for sending links to discord."""

    __tablename__ = "linkstodiscordignorelist"
    id = Column(Integer(), primary_key=True)
    username = Column(String(128), nullable=False, unique=True)


class IgnoreList(Base):
    """Table of regex patterns to ignore all commands from."""

    __tablename__ = "ignorelist"
    id = Column(Integer(), primary_key=True)
    pattern = Column(String(128), nullable=False, unique=True)
    enabled = Column(Boolean(), default=True)


class TriviaQuestions(Base):
    """Table for Trivia"""

    __tablename__ = "trivia_questions"
    id = Column(Integer(), primary_key=True)
    text = Column(String(1024), nullable=False)
    answers = Column(String(2048), nullable=False, default={})
    explain = Column(String(1024))
    last_used_date = Column(DateTime(), default=datetime.now)
    last_update_date = Column(DateTime(), default=datetime.now)
    created_date = Column(DateTime(), default=datetime.now)
    created_by = Column(String(128))
    reference = Column(String(1024))
    sound = Column(String(32), default=None)
    image = Column(String(32), default=None)
    # priority = Column(Boolean(), default=False)
    order = Column(Integer(), default=99999)
    enabled = Column(Boolean(), default=True)


class TriviaResults(Base):
    """Table for storing user data for trivia"""

    __tablename__ = "trivia_results"
    user_id = Column(Integer(), ForeignKey("users.user_id"), primary_key=True, nullable=False, index=True)
    channel = Column(Integer(), ForeignKey("users.channel"), primary_key=True, nullable=False, index=True)
    total_wins = Column(Integer(), nullable=False, default=0)
    trivia_points = Column(Integer(), nullable=False, default=0)
    questions_answered_correctly = Column(NestedMutableJson)


class WebAuth(Base):
    """Table for storing discord user ids for web authentication"""

    __tablename__ = "web_auth"
    id = Column(BigInteger(), primary_key=True, nullable=False, index=True)
    name = Column(String(128), nullable=False)
    enabled = Column(Boolean(), default=True)
    admin = Column(Boolean(), default=False)
    mod = Column(Boolean(), default=False)
    user = Column(Boolean(), default=False)
    api_key = Column(String(32), default=randomword)


class Clips(Base):
    """Table for storing twitch clips"""

    __tablename__ = "clips"
    id = Column(Integer(), primary_key=True)
    name = Column(String(32), nullable=False, unique=True)
    title = Column(String(1024))
    url = Column(String(256), nullable=False)
    enabled = Column(Boolean, default=True)
    added_by = Column(String(128), default="")
