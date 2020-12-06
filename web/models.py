from datetime import datetime

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Announcements(Base):
    """Storing data for the announcements command"""

    # Direct copy from the twitch bot, make sure to keep in sync.

    __tablename__ = "announcements"
    # __table_args__ = {"extend_existing": True}
    id = Column(Integer(), primary_key=True, nullable=False)
    text = Column(String(1024), nullable=False)
    created_date = Column(DateTime(), default=datetime.now)
    last_sent = Column(DateTime(), default=datetime.now)
    times_sent = Column(Integer(), default=0)
    enabled = Column(Boolean(), default=True)
