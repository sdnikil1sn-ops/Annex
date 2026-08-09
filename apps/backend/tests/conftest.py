"""Shared pytest fixtures."""

import os
from collections.abc import Iterator

import pytest
from dotenv import load_dotenv
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

load_dotenv()  # pick up DATABASE_URL / TEST_DATABASE_URL from .env

@pytest.fixture()
def db_session() -> Iterator[Session]:
    """Yield a database session backed by TEST_DATABASE_URL.

    Skips when the variable is unset: database tests require a running
    Postgres (e.g. ``docker compose up -d postgres``) and applied migrations
    (``uv run alembic upgrade head``).
    """
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        pytest.skip(
            "TEST_DATABASE_URL is not set. Start Postgres with "
            "'docker compose up -d postgres', run 'uv run alembic upgrade head', "
            "then set TEST_DATABASE_URL."
        )

    engine: Engine = create_engine(url)
    session_factory = sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()
