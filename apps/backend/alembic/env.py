# ruff: noqa: I001, F401
from logging.config import fileConfig
import app.models # Almbericでモデルを読み込ために必要

from sqlalchemy import create_engine, pool
from sqlalchemy.engine import Engine

from alembic import context
from app.common.database import Base  # Baseをインポート

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_sync_engine() -> Engine:
    """Create a synchronous engine for Alembic to run migrations.

    This function ensures that Alembic uses a synchronous engine
    even if the main application uses an asynchronous engine.

    Returns:
        Engine: A synchronous SQLAlchemy Engine.

    """
    # Use the synchronous version of the DATABASE_URL
    url = config.get_main_option("sqlalchemy.url")
    if url is None:
        raise ValueError("sqlalchemy.url is not set in the configuration.")
    url = url.replace("asyncpg", "psycopg2")
    return create_engine(url, poolclass=pool.NullPool)


def run_migrations_offline() -> None:
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


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Use the synchronous engine specifically for Alembic migrations
    connectable = get_sync_engine()

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
