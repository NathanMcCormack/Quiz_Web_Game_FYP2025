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

def _payload(name="Test", email="test@atu.ie", password="payload1!", age=21, user_name="TEST"):
    # Valid payload matching your schema constraints
    return {
        "name": name,
        "email": email,
        "password": password,
        "age": age,
        "user_name": user_name,
    }
 
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


def test_delete_user_success(client):
    # create
    r_create = client.post("/api/users", json=_payload(
        name="Carol", email="carol@atu.ie", user_name="CAROL01"
    ))
    assert r_create.status_code == 201
    user_id = r_create.json()["user_id"]

    # delete
    r_del = client.delete(f"/api/users/{user_id}")
    assert r_del.status_code == 204

    # confirm it's gone
    r_get = client.get(f"/api/users/{user_id}")
    assert r_get.status_code == 404

def test_update_user_success(client):
    # create
    r_create = client.post("/api/users", json=_payload(
        name="Darragh", email="darragh@atu.ie", user_name="DMAC001"
    ))
    assert r_create.status_code == 201
    user_id = r_create.json()["user_id"]

    # put (full replace)
    updated = _payload(
        name="Nathan",
        email="nathan@atu.ie",
        password="QuizGame2!",
        age=22,
        user_name="NATH001"
    )
    r_put = client.put(f"/api/users/{user_id}", json=updated)
    assert r_put.status_code == 200
    body = r_put.json()
    assert body["user_id"] == user_id
    assert body["name"] == "Nathan"
    assert body["email"] == "nathan@atu.ie"
    assert body["age"] == 22
    assert body["user_name"] == "NATH001"