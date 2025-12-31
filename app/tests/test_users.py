"""
Tests for user endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.core.config import settings

# Create test database
SQLALCHEMY_DATABASE_URL = "postgresql://test:test@localhost:5432/test_db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def setup_database():
    """Setup test database."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(setup_database):
    """Create test client."""
    return TestClient(app)


def test_create_user(client):
    """Test creating a user."""
    user_data = {
        "email": "test@example.com",
        "name": "Test User"
    }
    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["name"] == user_data["name"]
    assert "id" in data


def test_get_user(client):
    """Test getting a user by ID."""
    # First create a user
    user_data = {
        "email": "gettest@example.com",
        "name": "Get Test User"
    }
    create_response = client.post("/api/v1/users/", json=user_data)
    user_id = create_response.json()["id"]
    
    # Then get the user
    response = client.get(f"/api/v1/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["email"] == user_data["email"]


def test_get_users(client):
    """Test getting all users."""
    response = client.get("/api/v1/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_update_user(client):
    """Test updating a user."""
    # First create a user
    user_data = {
        "email": "updatetest@example.com",
        "name": "Update Test User"
    }
    create_response = client.post("/api/v1/users/", json=user_data)
    user_id = create_response.json()["id"]
    
    # Then update the user
    update_data = {"name": "Updated Name"}
    response = client.put(f"/api/v1/users/{user_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]


def test_delete_user(client):
    """Test deleting a user."""
    # First create a user
    user_data = {
        "email": "deletetest@example.com",
        "name": "Delete Test User"
    }
    create_response = client.post("/api/v1/users/", json=user_data)
    user_id = create_response.json()["id"]
    
    # Then delete the user
    response = client.delete(f"/api/v1/users/{user_id}")
    assert response.status_code == 204
    
    # Verify user is deleted
    get_response = client.get(f"/api/v1/users/{user_id}")
    assert get_response.status_code == 404

