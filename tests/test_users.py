import pytest 
from fastapi.testclient import TestClient 
from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker 
from sqlalchemy.pool import StaticPool
 
from app.main import app, get_db 
from app.models import Base 
 
TEST_DB_URL = "sqlite+pysqlite:///:memory:" 
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool) 
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
    r = client.post("/api/users", json={"name":"Darragh","email":"Darragh@atu.ie","password":"QuizGame1!","age":21,"user_name":"DMAC"}) 
    assert r.status_code == 201 

def test_get_user_not_found(client):
    r = client.get("/api/users/999999")
    assert r.status_code == 404

def test_duplicate_user_id_conflict(client): 
    client.post("/api/users", json={"name":"Michael","email":"Michael@atu.ie","password":"QuizGame32","age":41,"user_name":"MIKE"}) 
    r = client.post("/api/users", json={"name":"Michael","email":"Michael@atu.ie","password":"QuizGame32","age":41,"user_name":"MIKE"}) 
    assert r.status_code == 409  # duplicate 
 
def test_bad_name(client): 
    r = client.post("/api/users", json={"name":"Name12@!","email":"Nathan@atu.ie","password":"QuizGame2!","age":21,"user_name":"NMC"}) 
    assert r.status_code == 422  # pydantic validation error 

def test_bad_password(client): 
    r = client.post("/api/users", json={"name":"Nathan","email":"Nathan@atu.ie","password":"a","age":21,"user_name":"NMC"}) 
    assert r.status_code == 422  # pydantic validation error 

def test_bad_age(client): 
    r = client.post("/api/users", json={"name":"Nathan","email":"Nathan@atu.ie","password":"Correct123","age":1,"user_name":"NMC"}) 
    assert r.status_code == 422  # pydantic validation error 

def test_bad_username(client): 
    r = client.post("/api/users", json={"name":"Nathan","email":"Nathan@atu.ie","password":"Correct123","age":21,"user_name":"a"}) 
    assert r.status_code == 422  # pydantic validation error 