from os import getenv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

mysql_database = getenv("MYSQL_DATABASE")
mysql_user = getenv("MYSQL_USER")
mysql_pass = getenv("MYSQL_PASSWORD")

engine = create_engine(f"mysql+mysqlconnector://{mysql_user}:{mysql_pass}@mysql:3306/{mysql_database}")

session = scoped_session(sessionmaker(bind=engine))
