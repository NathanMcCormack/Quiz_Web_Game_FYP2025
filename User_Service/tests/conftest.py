from fastapi.testclient import TestClient 
from User_Service.app.UserMain import app 
import pytest 

@pytest.fixture 
def client(): 
    return TestClient(app) 