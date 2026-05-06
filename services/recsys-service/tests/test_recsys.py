import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

def test_root():
    with patch("motor.motor_asyncio.AsyncIOMotorClient"):
        from app.main import app
        client = TestClient(app)
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["service"] == "recsys-service"

def test_health():
    with patch("motor.motor_asyncio.AsyncIOMotorClient"):
        from app.main import app
        client = TestClient(app)
        response = client.get("/recsys/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

def test_metrics():
    with patch("motor.motor_asyncio.AsyncIOMotorClient"):
        from app.main import app
        client = TestClient(app)
        response = client.get("/metrics")
        assert response.status_code == 200

def test_recommend_returns_200():
    with patch("motor.motor_asyncio.AsyncIOMotorClient"), \
         patch("app.core.collaborative.interactions_collection"), \
         patch("app.core.heuristic.interactions_collection"):
        from app.main import app
        client = TestClient(app)
        response = client.post("/recsys/recommend", json={
            "user_id": 999,
            "current_question": "What is machine learning?",
            "top_k": 3
        })
        assert response.status_code == 200

def test_recommend_has_required_fields():
    with patch("motor.motor_asyncio.AsyncIOMotorClient"), \
         patch("app.core.collaborative.interactions_collection"), \
         patch("app.core.heuristic.interactions_collection"):
        from app.main import app
        client = TestClient(app)
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
    with patch("motor.motor_asyncio.AsyncIOMotorClient"), \
         patch("app.core.collaborative.interactions_collection"), \
         patch("app.core.heuristic.interactions_collection"):
        from app.main import app
        client = TestClient(app)
        response = client.post("/recsys/recommend", json={
            "user_id": 99999,
            "top_k": 5
        })
        assert response.status_code == 200

def test_popular_topics():
    with patch("motor.motor_asyncio.AsyncIOMotorClient"), \
         patch("app.core.heuristic.interactions_collection"):
        from app.main import app
        client = TestClient(app)
        response = client.get("/recsys/popular")
        assert response.status_code == 200

def test_log_interaction():
    mock_collection = MagicMock()
    mock_collection.insert_one = AsyncMock(return_value=MagicMock(inserted_id="test_id"))

    with patch("motor.motor_asyncio.AsyncIOMotorClient"), \
         patch("app.core.collaborative.interactions_collection", mock_collection):
        from app.main import app
        client = TestClient(app)
        response = client.post("/recsys/log", json={
            "user_id": 999,
            "question": "What is Docker?"
        })
        assert response.status_code == 201