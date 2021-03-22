from alembic import config as alembic_config

# Update database models
alembicArgs = ["--raiseerr", "upgrade", "head"]
alembic_config.main(argv=alembicArgs)
