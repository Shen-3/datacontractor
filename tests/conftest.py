"""Shared pytest fixtures for DataContractor tests.

Usage:
    - Override DATABASE_URL_TEST env var to use PostgreSQL instead of SQLite
    - Use client fixture for API integration tests
    - Use test_db_session for repository/service unit tests
"""

import os
from collections.abc import Generator
from typing import Any

import pandas as pd
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base, get_db
from app.main import app


@pytest.fixture(scope="session")
def test_engine():
    """Create a test database engine.

    Uses DATABASE_URL_TEST env var if set, otherwise falls back to
    SQLite in-memory database.
    """
    url = os.environ.get("DATABASE_URL_TEST", "sqlite:///:memory:")
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    engine = create_engine(
        url,
        connect_args=connect_args,
        echo=False,
        pool_pre_ping=True,
    )
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def test_db_session(test_engine) -> Generator[Session, Any, None]:
    """Provide an isolated database session for each test.

    Uses transaction rollback to ensure test isolation without
    dropping and recreating tables between tests.
    """
    connection = test_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(test_db_session: Session) -> Generator[TestClient, Any, None]:
    """Provide a TestClient with the database dependency overridden.

    All API requests during the test use the isolated test database session.
    """
    app.dependency_overrides[get_db] = lambda: test_db_session
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """A standard 5-row sample DataFrame for quality/schema tests."""
    return pd.DataFrame(
        {
            "user_id": [1, 2, 3, 4, 5],
            "event_type": ["login", "purchase", "logout", "login", "purchase"],
            "event_time": ["2025-06-11T10:00:00Z"] * 5,
            "amount": [None, 29.99, None, None, 49.99],
        }
    )


@pytest.fixture
def sample_schema() -> dict[str, Any]:
    """A standard schema definition matching sample_df."""
    return {
        "fields": [
            {"name": "user_id", "type": "integer", "required": True, "nullable": False},
            {"name": "event_type", "type": "enum", "required": True, "values": ["login", "purchase", "logout"]},
            {"name": "event_time", "type": "timestamp", "required": True},
            {"name": "amount", "type": "decimal", "required": False, "nullable": True},
        ]
    }


@pytest.fixture
def sample_quality_rules() -> list[dict[str, Any]]:
    """Standard quality rules that pass against sample_df."""
    return [
        {"name": "uid_not_null", "type": "not_null", "field": "user_id", "severity": "critical"},
        {
            "name": "etype_allowed",
            "type": "allowed_values",
            "field": "event_type",
            "values": ["login", "purchase", "logout"],
            "severity": "error",
        },
    ]
