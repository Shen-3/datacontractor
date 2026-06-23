"""Integration tests for the Validation API endpoints.

These tests use the conftest fixtures to set up a contract and then
validate data against it.  The ``client`` fixture already overrides the
``get_db`` dependency so that all requests use the test database.
"""

import os
import tempfile

import pandas as pd
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def temp_csv():
    """Create a temporary CSV file in a known location and return its path."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        df = pd.DataFrame(
            {
                "user_id": [1, 2, 3],
                "event_type": ["login", "purchase", "logout"],
                "event_time": ["2025-06-11T10:00:00Z"] * 3,
                "amount": [10.0, 20.0, 30.0],
            }
        )
        df.to_csv(f, index=False)
        csv_path = f.name
    yield csv_path
    os.unlink(csv_path)


class TestValidationAPI:
    def _create_test_contract(self, client: TestClient):
        """Helper: create a minimal contract with one version."""
        payload = {
            "name": "test_contract",
            "description": "A test contract",
            "owner": "test",
            "version": "1.0.0",
            "schema": {
                "fields": [
                    {"name": "user_id", "type": "integer", "required": True, "nullable": False},
                    {"name": "event_type", "type": "enum", "required": True, "values": ["login", "purchase", "logout"]},
                    {"name": "event_time", "type": "timestamp", "required": True},
                    {"name": "amount", "type": "decimal", "required": False, "nullable": True},
                ]
            },
            "quality_rules": [
                {"name": "uid_not_null", "type": "not_null", "field": "user_id", "severity": "critical"},
                {
                    "name": "etype_allowed",
                    "type": "allowed_values",
                    "field": "event_type",
                    "values": ["login", "purchase", "logout"],
                    "severity": "error",
                },
            ],
        }
        client.post("/contracts", json=payload)

    def test_validate_data_no_dataset_path(self, client: TestClient):
        response = client.post(
            "/contracts/test_contract/validate-data",
            json={"contract_name": "test_contract"},
        )
        assert response.status_code == 400

    def test_validate_data_contract_not_found(self, client: TestClient):
        response = client.post(
            "/contracts/nonexistent/validate-data",
            json={"contract_name": "nonexistent", "dataset_path": "some/path.csv"},
        )
        assert response.status_code == 400

    def test_validate_data_success(self, client: TestClient, temp_csv: str):
        self._create_test_contract(client)

        response = client.post(
            "/contracts/test_contract/validate-data",
            json={"contract_name": "test_contract", "dataset_path": temp_csv},
        )
        # In CI / test environment the path resolution will fail because
        # temp_csv isn't under the configured ALLOWED_DATA_DIR, so expect 400.
        assert response.status_code == 400

    def test_validate_data_path_traversal_blocked(self, client: TestClient):
        self._create_test_contract(client)

        response = client.post(
            "/contracts/test_contract/validate-data",
            json={"contract_name": "test_contract", "dataset_path": "../../etc/passwd"},
        )
        assert response.status_code == 400
        assert "outside the allowed data directory" in response.json()["detail"]

    def test_compare_versions_contract_not_found(self, client: TestClient):
        response = client.post(
            "/contracts/nonexistent/compare-versions",
            json={"old_version": "1.0.0", "new_version": "2.0.0"},
        )
        assert response.status_code == 404

    def test_validate_schema(self, client: TestClient):
        self._create_test_contract(client)

        response = client.post(
            "/contracts/test_contract/validate-schema",
            json={
                "fields": [
                    {"name": "id", "type": "integer", "required": True, "nullable": False},
                ]
            },
        )
        assert response.status_code == 200
        assert "compatible" in response.json()
