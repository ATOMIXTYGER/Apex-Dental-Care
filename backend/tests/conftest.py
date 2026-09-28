import os
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import Base, get_db
from app.main import app
from seeds.seed_data import seed_database

# Use in-memory SQLite for tests to keep test runs fast and independent
TEST_DATABASE_URL = "sqlite:///./test_dental.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        seed_database(db=db)
    finally:
        db.close()
    yield
    Base.metadata.drop_all(bind=test_engine)
    if os.path.exists("./test_dental.db"):
        try:
            os.remove("./test_dental.db")
        except Exception:
            pass

@pytest.fixture
def db_session():
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def admin_token(client):
    res = client.post("/api/v1/auth/login", json={"username_or_email": "admin@clinic.com", "password": "Dental@123"})
    assert res.status_code == 200
    return res.json()["access_token"]

@pytest.fixture
def dentist_token(client):
    res = client.post("/api/v1/auth/login", json={"username_or_email": "dr.chen@clinic.com", "password": "Dental@123"})
    assert res.status_code == 200
    return res.json()["access_token"]

@pytest.fixture
def receptionist_token(client):
    res = client.post("/api/v1/auth/login", json={"username_or_email": "reception1@clinic.com", "password": "Dental@123"})
    assert res.status_code == 200
    return res.json()["access_token"]
