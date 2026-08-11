"""
Shared pytest fixtures.

Uses mongomock-motor so the full test suite runs with zero external
dependencies (no real MongoDB Atlas cluster needed for CI).
"""
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from mongomock_motor import AsyncMongoMockClient

from app.core import database as db_module
from app.core.limiter import limiter
from app.main import app


@pytest_asyncio.fixture(autouse=True)
async def reset_rate_limiter():
    """
    The rate limiter's in-memory storage persists across the whole test
    session (it's a module-level singleton), not per-test. Without this,
    auth-heavy test files run later in the session fail with 429s caused
    by earlier tests' requests sharing the same 10/minute budget — not a
    real bug in the endpoints themselves.
    """
    limiter.reset()
    yield


@pytest_asyncio.fixture(autouse=True)
async def mock_mongo():
    """Replace the real Motor client with an in-memory mock for every test."""
    mock_client = AsyncMongoMockClient()
    db_module.mongodb.client = mock_client
    db_module.mongodb.db = mock_client["placer_test_db"]
    yield db_module.mongodb.db
    db_module.mongodb.client = None
    db_module.mongodb.db = None


@pytest_asyncio.fixture
async def client(mock_mongo):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
