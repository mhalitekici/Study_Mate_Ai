import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class AsyncIterator:
    def __init__(self, items):
        self.items = iter(items)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self.items)
        except StopIteration:
            raise StopAsyncIteration


def make_mock_collection(docs=None):
    if docs is None:
        docs = []
    mock_collection = MagicMock()
    mock_collection.insert_one = AsyncMock(
        return_value=MagicMock(inserted_id="test_id")
    )
    mock_cursor = MagicMock()
    mock_cursor.sort = MagicMock(return_value=mock_cursor)
    mock_cursor.limit = MagicMock(return_value=mock_cursor)
    mock_cursor.__aiter__ = MagicMock(return_value=AsyncIterator(docs))
    mock_collection.find = MagicMock(return_value=mock_cursor)
    return mock_collection


def test_root():
    mock_col = make_mock_collection()
    with patch("app.core.database.conversations_collection", mock_col), \
         patch("app.api.memory.conversations_collection", mock_col):
        from app.main import app
        client = TestClient(app)
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["service"] == "memory-service"


def test_health():
    mock_col = make_mock_collection()
    with patch("app.core.database.conversations_collection", mock_col), \
         patch("app.api.memory.conversations_collection", mock_col):
        from app.main import app
        client = TestClient(app)
        response = client.get("/memory/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


def test_save_missing_fields():
    mock_col = make_mock_collection()
    with patch("app.core.database.conversations_collection", mock_col), \
         patch("app.api.memory.conversations_collection", mock_col):
        from app.main import app
        client = TestClient(app)
        response = client.post("/memory/save", json={})
        assert response.status_code == 422


def test_metrics():
    mock_col = make_mock_collection()
    with patch("app.core.database.conversations_collection", mock_col), \
         patch("app.api.memory.conversations_collection", mock_col):
        from app.main import app
        client = TestClient(app)
        response = client.get("/metrics")
        assert response.status_code == 200


def test_save_valid():
    mock_col = make_mock_collection()
    with patch("app.core.database.conversations_collection", mock_col), \
         patch("app.api.memory.conversations_collection", mock_col):
        from app.main import app
        client = TestClient(app)
        response = client.post("/memory/save", json={
            "user_id": 999,
            "question": "What is Python?",
            "answer": "Python is a programming language.",
            "material_ids": []
        })
        assert response.status_code == 201


def test_get_history():
    mock_col = make_mock_collection(docs=[])
    with patch("app.core.database.conversations_collection", mock_col), \
         patch("app.api.memory.conversations_collection", mock_col):
        from app.main import app
        client = TestClient(app)
        response = client.get("/memory/history/999")
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "messages" in data


def test_get_context():
    mock_col = make_mock_collection(docs=[])
    with patch("app.core.database.conversations_collection", mock_col), \
         patch("app.api.memory.conversations_collection", mock_col):
        from app.main import app
        client = TestClient(app)
        response = client.get("/memory/context/999")
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "context" in data