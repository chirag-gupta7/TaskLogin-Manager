import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from database import Base, get_db

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_and_teardown_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

def get_auth_headers(username="taskuser", password="testpass123"):
    client.post("/api/v1/auth/register", json={
        "username": username,
        "email": f"{username}@example.com",
        "password": password
    })
    response = client.post("/api/v1/auth/login", json={
        "username": username,
        "password": password
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

client = TestClient(app)

def test_register_user():
    responce = client.post("/api/v1/auth/register", json={
        "username" : "testuser1",
        "email" : "testuser1@gmail.com",
        "password" : "testuserpassword"
    })

    assert responce.status_code == 200
    data = responce.json()
    assert data["username"] == "testuser1"
    assert "password" not in data

def test_register_duplicate_username():
    client.post("/api/v1/auth/register", json={
        "username": "dupeuser",
        "email": "dupe@example.com",
        "password": "testpass123"
    })
    response = client.post("/api/v1/auth/register", json={
        "username": "dupeuser",
        "email": "dupe2@example.com",
        "password": "testpass123"
    })
    assert response.status_code == 400


def test_login_success():
    client.post("/api/v1/auth/register", json={
        "username": "loginuser",
        "email": "loginuser@example.com",
        "password": "testpass123"
    })
    response = client.post("/api/v1/auth/login", json={
        "username": "loginuser",
        "password": "testpass123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password():
    client.post("/api/v1/auth/register", json={
        "username": "wrongpassuser",
        "email": "wrongpass@example.com",
        "password": "testpass123"
    })
    response = client.post("/api/v1/auth/login", json={
        "username": "wrongpassuser",
        "password": "incorrectpassword"
    })
    assert response.status_code == 401


def test_create_task_requires_auth():
    response = client.post("/api/v1/tasks", json={"title": "Test task"})
    assert response.status_code == 401

def test_create_task():
    headers = get_auth_headers()
    response = client.post("/api/v1/tasks", json={"title": "Buy groceries"}, headers=headers)
    assert response.status_code == 200
    assert response.json()["title"] == "Buy groceries"


def test_list_tasks_only_shows_own():
    headers_a = get_auth_headers(username="usera")
    headers_b = get_auth_headers(username="userb")

    client.post("/api/v1/tasks", json={"title": "User A task"}, headers=headers_a)
    client.post("/api/v1/tasks", json={"title": "User B task"}, headers=headers_b)

    response = client.get("/api/v1/tasks", headers=headers_a)
    titles = [task["title"] for task in response.json()]

    assert "User A task" in titles
    assert "User B task" not in titles


def test_cannot_update_others_task():
    headers_a = get_auth_headers(username="ownera")
    headers_b = get_auth_headers(username="ownerb")

    create_response = client.post("/api/v1/tasks", json={"title": "Owner A's task"}, headers=headers_a)
    task_id = create_response.json()["id"]

    response = client.put(f"/api/v1/tasks/{task_id}", json={"title": "Hijacked!"}, headers=headers_b)
    assert response.status_code == 403