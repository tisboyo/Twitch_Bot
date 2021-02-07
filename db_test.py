from os import getenv

from sqlalchemy import create_engine
from sqlalchemy import orm

from models import Base

driver = "mysql+mysqlconnector"
username = getenv("MYSQL_USER")
passwd = getenv("MYSQL_PASSWORD")
address = getenv("MYSQL_SERVER") or "mysql"
port = getenv("MYSQL_PORT") or 3306
database = getenv("MYSQL_DATABASE")

engine = create_engine(f"{driver}://{username}:{passwd}@{address}:{port}/{database}")
Session = orm.sessionmaker(bind=engine, autoflush=True)
session = orm.scoped_session(Session)
Base.metadata.create_all(engine)
