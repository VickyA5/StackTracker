import os
import pathlib
import shutil
import pytest
from fastapi.testclient import TestClient

# Ensure a clean SQLite file-based DB per test session
TEST_DB_PATH = pathlib.Path(__file__).parent / "test.db"

@pytest.fixture(scope="session", autouse=True)
def configure_test_database():
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
    os.environ["DATABASE_URL"] = f"sqlite+pysqlite:///{TEST_DB_PATH}"
    yield
    # Cleanup after tests
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()

@pytest.fixture()
def client():
    # Import here so DATABASE_URL is already set
    from back.src.main import app
    # Use context manager to ensure startup/shutdown (lifespan) runs
    with TestClient(app) as c:
        yield c
