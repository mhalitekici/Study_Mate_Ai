import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "auth-service"

def test_health():
    response = client.get("/auth/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_register_success():
    response = client.post("/auth/register", json={
        "email": "pytest_test@studymate.com",
        "password": "test123",
        "full_name": "Pytest User"
    })
    assert response.status_code in [201, 400]

def test_register_invalid_email():
    response = client.post("/auth/register", json={
        "email": "not-an-email",
        "password": "test123"
    })
    assert response.status_code == 422

def test_login_wrong_password():
    response = client.post("/auth/login", json={
        "email": "wrong@test.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401

def test_validate_invalid_token():
    response = client.get("/auth/validate", params={"token": "invalid_token"})
    assert response.status_code == 401

def test_metrics():
    response = client.get("/metrics")
    assert response.status_code == 200