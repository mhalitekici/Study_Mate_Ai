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
    assert response.json()["service"] == "memory-service"

def test_health():
    response = client.get("/memory/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_save_missing_fields():
    response = client.post("/memory/save", json={})
    assert response.status_code == 422

def test_save_valid():
    response = client.post("/memory/save", json={
        "user_id": 999,
        "question": "What is Python?",
        "answer": "Python is a programming language.",
        "material_ids": []
    })
    assert response.status_code == 201

def test_get_history():
    response = client.get("/memory/history/999")
    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data
    assert "messages" in data

def test_get_context():
    response = client.get("/memory/context/999")
    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data
    assert "context" in data

def test_metrics():
    response = client.get("/metrics")
    assert response.status_code == 200