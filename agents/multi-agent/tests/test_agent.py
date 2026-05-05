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
    assert response.json()["service"] == "multi-agent-system"

def test_health():
    response = client.get("/agent/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_metrics():
    response = client.get("/metrics")
    assert response.status_code == 200

def test_ask_missing_fields():
    response = client.post("/agent/ask", json={})
    assert response.status_code == 422

def test_ask_invalid_user_id():
    response = client.post("/agent/ask", json={
        "question": "What is AI?",
        "user_id": "not-a-number"
    })
    assert response.status_code == 422