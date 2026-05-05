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
    assert response.json()["service"] == "material-service"

def test_health():
    response = client.get("/materials/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_upload_without_auth():
    response = client.post("/materials/upload")
    assert response.status_code == 422

def test_list_without_auth():
    response = client.get("/materials/")
    assert response.status_code == 422

def test_delete_without_auth():
    response = client.delete("/materials/1")
    assert response.status_code == 422

def test_metrics():
    response = client.get("/metrics")
    assert response.status_code == 200