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
    assert response.json()["service"] == "recsys-service"

def test_health():
    response = client.get("/recsys/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_recommend_returns_200():
    response = client.post("/recsys/recommend", json={
        "user_id": 999,
        "current_question": "What is machine learning?",
        "top_k": 3
    })
    assert response.status_code == 200

def test_recommend_has_required_fields():
    response = client.post("/recsys/recommend", json={
        "user_id": 999,
        "top_k": 3
    })
    data = response.json()
    assert "user_id" in data
    assert "content_based" in data
    assert "collaborative" in data
    assert "heuristic" in data
    assert "cold_start" in data

def test_recommend_cold_start_for_new_user():
    response = client.post("/recsys/recommend", json={
        "user_id": 99999,
        "top_k": 5
    })
    data = response.json()
    assert response.status_code == 200
    assert isinstance(data["cold_start"], list)

def test_log_interaction():
    response = client.post("/recsys/log", json={
        "user_id": 999,
        "question": "What is Docker?"
    })
    assert response.status_code == 201

def test_popular_topics():
    response = client.get("/recsys/popular")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_metrics():
    response = client.get("/metrics")
    assert response.status_code == 200