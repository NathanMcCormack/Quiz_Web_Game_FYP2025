import pytest 
from fastapi.testclient import TestClient 
from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker 
 
from app.main import app, get_db 
from app.models import Base 
 
TEST_DB_URL = "sqlite:///./app.db" 
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False}) 
TestingSessionLocal = sessionmaker(bind=engine, expire_on_commit=False) 
Base.metadata.create_all(bind=engine) 
 
@pytest.fixture 
def client(): 
    def override_get_db(): 
        db = TestingSessionLocal() 
        try: 
            yield db 
        finally: 
            db.close() 
    app.dependency_overrides[get_db] = override_get_db 
    with TestClient(app) as c: 
        # hand the client to the test 
        yield c 
        # --- teardown happens when the 'with' block exits --- 
 
def test_create_user(client): 
    r = client.post("/api/users", json={"name":"Darragh","email":"Darragh@atu.ie","age":21,"student_id":"G00123456"}) 
    assert r.status_code == 201 