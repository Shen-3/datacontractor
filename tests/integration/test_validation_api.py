import pytest
import os
import pandas as pd
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.main import app
from fastapi.testclient import TestClient


TEST_DB_URL = "sqlite:///test_validation.db"


@pytest.fixture(scope="module")
def test_db():
    engine = create_engine(TEST_DB_URL)
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)
    yield TestSession
    Base.metadata.drop_all(engine)
    if os.path.exists("test_validation.db"):
        os.remove("test_validation.db")


@pytest.fixture
def client():
    return TestClient(app)


class TestValidationAPI:
    def test_validate_data_no_dataset_path(self, client):
        response = client.post(
            "/contracts/nonexistent/validate-data",
            json={"contract_name": "nonexistent"},
        )
        assert response.status_code == 400

    def test_validate_data_contract_not_found(self, client):
        response = client.post(
            "/contracts/nonexistent/validate-data",
            json={"contract_name": "nonexistent", "dataset_path": "some/path.csv"},
        )
        assert response.status_code == 400

    def test_compare_versions_contract_not_found(self, client):
        response = client.post(
            "/contracts/nonexistent/compare-versions",
            json={"old_version": "1.0.0", "new_version": "2.0.0"},
        )
        assert response.status_code == 404
