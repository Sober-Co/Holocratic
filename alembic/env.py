"""Alembic environment configuration for the Holocratic project."""

from __future__ import annotations

import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel

# Ensure models are imported so metadata is populated
from holocratic.domain.org_structure import models as org_models  # noqa: F401
from holocratic.domain.governance import models as governance_models  # noqa: F401
from holocratic.domain.meetings import models as meeting_models  # noqa: F401
from holocratic.domain.work import models as work_models  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

section = config.get_section(config.config_ini_section)
if section is None:
    raise RuntimeError("Alembic configuration section missing")

database_url = os.getenv("HOLOCRATIC_DATABASE_URL")
if database_url:
    section["sqlalchemy.url"] = database_url

target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""

    url = section.get("sqlalchemy.url")
    if not url:
        raise RuntimeError("sqlalchemy.url must be configured for offline migrations")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    connectable = engine_from_config(
        section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
