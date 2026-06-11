import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app


client = TestClient(app)


class TestHealthAPI:
    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_root(self):
        response = client.get("/")
        assert response.status_code == 200
        assert "DataContractor" in response.json()["message"]
