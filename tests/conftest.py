import os
import shutil
import tempfile
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.config as config
import app.database as database
from app.database import Base, get_db
from app.main import app

# Create in-memory SQLite engine for tests with StaticPool so all connections share the same memory DB
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Patch SessionLocal globally for the test process
database.SessionLocal = TestingSessionLocal
database.engine = test_engine


@pytest.fixture(scope="session", autouse=True)
def setup_test_storage():
    """Points STORAGE_DIR to a temporary directory during testing."""
    temp_dir = Path(tempfile.mkdtemp(prefix="cert_test_storage_"))
    config.STORAGE_DIR = temp_dir
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(autouse=True)
def setup_test_database():
    """Initializes a fresh schema before each test and tears it down afterwards."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session():
    """Provides a fresh transactional test database session."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session):
    """FastAPI TestClient with overridden get_db dependency."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
