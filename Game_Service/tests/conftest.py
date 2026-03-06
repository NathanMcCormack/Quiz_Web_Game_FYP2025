import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["DAILY_JOB_TOKEN"] = "test-token"

# Make Game_Service/ the import root so tests consistently use `app...`
BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import app.GameMain as game_main
import app.DailyMode as daily_mode
from app.GameMain import app
from app.GameModels import Base

TEST_DB_URL = "sqlite+pysqlite:///:memory:"

engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def client():
    # Force both modules to use the same test session factory
    game_main.SessionLocal = TestingSessionLocal
    daily_mode.SessionLocal = TestingSessionLocal

    # Override both dependency functions
    app.dependency_overrides[game_main.get_db] = override_get_db
    app.dependency_overrides[daily_mode.get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()