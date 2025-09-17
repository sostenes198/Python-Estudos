from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

import os

config = context.config

# --- Integração com Flask ---
from app_factory import create_app
from extensions import db

app = create_app()
with app.app_context():
    # Usa a URI da app (config.py). Se quiser, DATABASE_URL pode sobrescrever.
    db_url = "sqlite:///./instance/recipes.db"  # fallback seguro
    config.set_main_option("sqlalchemy.url", db_url)

    # IMPORTANTE: importe todos os modelos aqui para povoar o metadata
    from models import *  # noqa: F401

target_metadata = db.metadata


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
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
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
