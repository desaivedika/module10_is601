"""Fixtures for integration tests that need a real PostgreSQL database.

The database comes from the DATABASE_URL environment variable. In GitHub Actions
that is a Postgres service container; locally it is the `db` service from
docker-compose.yml.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.database import Base, SessionLocal, engine
from main import app


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    """Create all tables once for the test session, then drop them."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def clean_tables():
    """Start every test with an empty users table."""
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE"))
    yield


@pytest.fixture
def db():
    """A database session for direct model-level tests."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client():
    """HTTP client for API-level tests."""
    with TestClient(app) as test_client:
        yield test_client