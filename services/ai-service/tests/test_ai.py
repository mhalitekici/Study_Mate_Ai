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
    assert response.json()["service"] == "ai-service"

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_generate_missing_fields():
    response = client.post("/generate", json={})
    assert response.status_code == 422

def test_generate_invalid_user_id():
    response = client.post("/generate", json={
        "question": "What is AI?",
        "user_id": "not-a-number"
    })
    assert response.status_code == 422

def test_index_missing_fields():
    response = client.post("/index", json={})
    assert response.status_code == 422

def test_metrics():
    response = client.get("/metrics")
    assert response.status_code == 200