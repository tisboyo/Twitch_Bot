from asyncio import sleep

from sqlalchemy import create_engine
from sqlalchemy import orm
from twitchbot import Mod
from twitchbot.config import database_cfg
from twitchbot.database.session import _try_get_env
from twitchbot.util import add_task
from twitchbot.util import task_running  # Put all Table classes above here

from models import Base
from models import Settings


class Database(Mod):
    name = "database"

    def __init__(self) -> None:
        super().__init__()

        username = _try_get_env(database_cfg.username)
        passwd = _try_get_env(database_cfg.password)
        address = _try_get_env(database_cfg.address)
        port = _try_get_env(database_cfg.port)
        database = _try_get_env(database_cfg.database)
        driver = _try_get_env(database_cfg.database_format) + "+" + _try_get_env(database_cfg.driver)

        engine = create_engine(f"{driver}://{username}:{passwd}@{address}:{port}/{database}")
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
