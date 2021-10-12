from asyncio import sleep
from datetime import datetime
from datetime import timedelta
from json import loads
from os import environ

import aiohttp
from sqlalchemy import create_engine
from sqlalchemy import orm
from twitchbot import Mod
from twitchbot.config import database_cfg
from twitchbot.database.session import _get_database_env_value
from twitchbot.util import add_task
from twitchbot.util import task_running  # Put all Table classes above here

from models import Base
from models import Settings


class Database(Mod):
    name = "database"

    def __init__(self) -> None:
        super().__init__()

        username = _get_database_env_value(database_cfg.username)
        passwd = _get_database_env_value(database_cfg.password)
        address = _get_database_env_value(database_cfg.address)
        port = _get_database_env_value(database_cfg.port)
        database = _get_database_env_value(database_cfg.database)
        driver = _get_database_env_value(database_cfg.database_format) + "+" + _get_database_env_value(database_cfg.driver)

        engine = create_engine(f"{driver}://{username}:{passwd}@{address}:{port}/{database}")
        Session = orm.sessionmaker(bind=engine, autoflush=True)
        self.session = orm.scoped_session(Session)
        Base.metadata.create_all(engine)


# Define the session before the keep_alive_loop so it's available to it
session = Database().session


async def keep_alive_loop():
    thirty_day_warning_sent = False
    while True:
        # Replace the keep alive query with refreshing the twitch irc token in environment variable
        # so if it changes, while the connection is active, the bot will use the new key for api queries
        query = session.query(Settings.value).filter(Settings.key == "twitch_irc_token").one_or_none()
        session.commit()
        if query:
            values = loads(query[0])
            environ["oauth"] = values["access_token"]

            # Since we're querying it, might as well check how old it is and notify us
            last_update = datetime.fromisoformat(values["updated"])
            thirty_days = timedelta(days=30)
            if datetime.now() > last_update + thirty_days:
                if not thirty_day_warning_sent:
                    # send webhook message informing it has been 30 days since last auth key update
                    query = session.query(Settings).filter(Settings.key == "to_do_webhook").one_or_none()
                    webhook = query.value if query else None

                    async with aiohttp.ClientSession() as http_session:
                        await http_session.post(
                            webhook,
                            json={
                                "content": f"Twitch IRC Token last updated {values['updated']}. To update visit https://{environ['WEB_HOSTNAME']}/twitch/oauth",  # noqa E501
                                "username": "TwitchBot",
                            },
                        )

                thirty_day_warning_sent = True

            else:
                thirty_day_warning_sent = False

        else:
            print("Unable to find twitch irc token in database")

        print("Mysql keep-alive running...")

        await sleep(3600)  # Run the keep alive once an hour


# Start the keep-alive loop if it's not running
if not task_running("mysql-keepalive"):
    add_task("mysql-keepalive", keep_alive_loop())
