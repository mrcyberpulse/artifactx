import os
import uuid

# Settings must be valid before anything under app/ is imported, since app.main reads them
# at import time. The DATABASE_URL here is never actually connected to: get_db is overridden
# below so every request uses the SQLite test engine instead.
os.environ.setdefault("ARTIFACTX_ENVIRONMENT", "testing")
os.environ.setdefault("ARTIFACTX_DATABASE_URL", "postgresql+psycopg://unused:unused@localhost/unused")
os.environ.setdefault("ARTIFACTX_REDIS_URL", "redis://localhost:6379/15")
os.environ.setdefault("ARTIFACTX_SECRET_KEY", "test-secret-key-please-change-0123456789abcdef")
os.environ.setdefault("ARTIFACTX_COOKIE_SECURE", "false")
os.environ.setdefault("ARTIFACTX_RATE_LIMIT_ENABLED", "true")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app

# In-memory SQLite shared across connections in the pool, so all sessions in a test see the
# same schema. The real deployment target is PostgreSQL (see docker-compose.yml); this keeps
# the test suite fast and dependency-free. CI also validates migrations against real Postgres.
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@pytest.fixture(scope="session", autouse=True)
def _create_schema():
    # Import every model module so Base.metadata is fully populated, matching alembic/env.py.
    from app.modules.auth import models as _auth  # noqa: F401
    from app.modules.audit import models as _audit  # noqa: F401
    from app.modules.projects import models as _projects  # noqa: F401
    from app.modules.users import models as _users  # noqa: F401
    from app.modules.workspaces import models as _workspaces  # noqa: F401

    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session():
    """Each test runs inside an outer transaction + SAVEPOINT, so endpoint-level db.commit()
    calls only release the savepoint. Everything is rolled back when the test ends."""
    connection = engine.connect()
    outer_transaction = connection.begin()
    session = TestSessionLocal(bind=connection)
    nested = connection.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def _restart_savepoint(sess, trans):
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()

    try:
        yield session
    finally:
        session.close()
        outer_transaction.rollback()
        connection.close()


@pytest.fixture()
def client(db_session):
    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.pop(get_db, None)


def unique_email() -> str:
    return f"user-{uuid.uuid4().hex[:12]}@example.com"


def register_user(client: TestClient, *, email: str | None = None, password: str = "Str0ngPassw0rd!") -> dict:
    response = client.post(
        "/api/auth/register",
        json={"email": email or unique_email(), "full_name": "Test User", "password": password},
    )
    assert response.status_code == 201, response.text
    return response.json()


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def create_workspace(client: TestClient, token: str, name: str = "Acme Security") -> dict:
    response = client.post("/api/workspaces", json={"name": name}, headers=auth_headers(token))
    assert response.status_code == 201, response.text
    return response.json()
