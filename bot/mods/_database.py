from asyncio import sleep

from models import Base
from models import Settings
from sqlalchemy import create_engine
from sqlalchemy import orm
from twitchbot import Mod
from twitchbot.config import mysql_cfg
from twitchbot.util import add_task
from twitchbot.util import task_running  # Put all Table classes above here


class Database(Mod):
    name = "database"

    def __init__(self) -> None:
        super().__init__()

        engine = create_engine(
            f"mysql+mysqlconnector://{mysql_cfg.username}:{mysql_cfg.password}@{mysql_cfg.address}:{mysql_cfg.port}/{mysql_cfg.database}"  # noqa E501
        )
        Session = orm.sessionmaker(bind=engine, autoflush=True)
        self.session = orm.scoped_session(Session)
        Base.metadata.create_all(engine)


# Define the session before the keep_alive_loop so it's available to it
session = Database().session


async def keep_alive_loop():
    while True:
        session.query(Settings).filter(Settings.key == "keepalive").one_or_none()
        print("Mysql keep-alive running...")

        await sleep(3600)  # Run the keep alive once an hour


# Start the keep-alive loop if it's not running
if not task_running("mysql-keepalive"):
    add_task("mysql-keepalive", keep_alive_loop())
