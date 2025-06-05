from fastapi.testclient import TestClient
from fastapi import FastAPI
import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from main import app, get_session
import database

DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture(scope="function", autouse=True)
async def override_db():
    test_engine = create_async_engine(DATABASE_URL, future=True)
    test_session_maker = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    # monkeypatch глобальные переменные
    database.engine = test_engine
    database.async_session_maker = test_session_maker
    async def override_get_session():
        async with test_session_maker() as session:
            yield session
    app.dependency_overrides[get_session] = override_get_session
    yield
    await test_engine.dispose()

@pytest_asyncio.fixture(scope="function")
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_register_and_login(async_client):
    resp = await async_client.post("/register/", json={"username": "user1", "password": "pass"})
    assert resp.status_code == 200
    resp = await async_client.post("/login/", data={"username": "user1", "password": "pass"})
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    assert token

@pytest.mark.asyncio
async def test_protected_me(async_client):
    await async_client.post("/register/", json={"username": "user2", "password": "pass"})
    resp = await async_client.post("/login/", data={"username": "user2", "password": "pass"})
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    resp = await async_client.get("/users/me/", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["username"] == "user2"

@pytest.mark.asyncio
async def test_notes_crud(async_client):
    await async_client.post("/register/", json={"username": "user3", "password": "pass"})
    resp = await async_client.post("/login/", data={"username": "user3", "password": "pass"})
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    resp = await async_client.post("/notes/", json={"title": "n1", "content": "c1"}, headers=headers)
    assert resp.status_code == 200
    note_id = resp.json()["id"]
    resp = await async_client.get(f"/notes/{note_id}", headers=headers)
    assert resp.status_code == 200
    resp = await async_client.get("/notes/", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    resp = await async_client.delete(f"/notes/{note_id}", headers=headers)
    assert resp.status_code == 204
    resp = await async_client.get(f"/notes/{note_id}", headers=headers)
    assert resp.status_code == 404