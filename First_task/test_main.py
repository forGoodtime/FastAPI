import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from main import app, get_session

# Настройка тестовой БД (SQLite in-memory)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Фикстура для тестовой сессии
@pytest.fixture(scope="function")
def db_session():
    SQLModel.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    SQLModel.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_session():
        yield db_session
    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as c:
        yield c

def test_register_and_login(client):
    resp = client.post("/register/", json={"username": "user1", "password": "pass"})
    assert resp.status_code == 200
    resp = client.post("/login/", data={"username": "user1", "password": "pass"})
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    assert token

def test_protected_me(client):
    client.post("/register/", json={"username": "user2", "password": "pass"})
    resp = client.post("/login/", data={"username": "user2", "password": "pass"})
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.get("/users/me/", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["username"] == "user2"

def test_notes_crud(client):
    client.post("/register/", json={"username": "user3", "password": "pass"})
    resp = client.post("/login/", data={"username": "user3", "password": "pass"})
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.post("/notes/", json={"title": "n1", "content": "c1"}, headers=headers)
    assert resp.status_code == 200
    note_id = resp.json()["id"]
    resp = client.get(f"/notes/{note_id}", headers=headers)
    assert resp.status_code == 200
    resp = client.get("/notes/", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    resp = client.delete(f"/notes/{note_id}", headers=headers)
    assert resp.status_code == 204
    resp = client.get(f"/notes/{note_id}", headers=headers)
    assert resp.status_code == 404