import importlib
import os
import pathlib
import sys
import types
from json import loads
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config
from sqlalchemy import pool

sys.path.append(os.getcwd())

from models import Base  # noqa E402


def import_module_from_packages(path) -> types.ModuleType:
    """Import a module from the given path."""

    module_path = pathlib.Path(path)
    module_path = get_site_packages_path().joinpath(module_path).resolve()
    module_name = module_path.stem  # 'path/x.py' -> 'x'
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def get_site_packages_path() -> pathlib.Path:
    for path in sys.path:
        if "site-packages" in path:
            return pathlib.Path(path).resolve()

    return None


# Import `my_module` without executing `/path/to/__init__.py`
twitchbot_modules = import_module_from_packages("twitchbot/database/base_models.py")

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = [Base.metadata, twitchbot_modules.Base.metadata]

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.
with open("configs/mysql.json") as f:  # TODO: Rename to file with #71
    db_cfg = loads(f.read())
    db_cfg["driver"] = "mysql+mysqlconnector"  # TODO: Remove with #71

db_url = f"{db_cfg['driver']}://{db_cfg['username']}:{db_cfg['password']}@{db_cfg['address']}:{db_cfg['port']}/{db_cfg['database']}"  # noqa E501
config.set_main_option("sqlalchemy.url", db_url)


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
