"""Test health check endpoint."""

from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"

