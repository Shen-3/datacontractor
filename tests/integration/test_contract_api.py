"""Integration tests for the Contract API endpoints.

All tests run against a real (in-memory SQLite or PostgreSQL via
DATABASE_URL_TEST) database through the FastAPI TestClient.
"""

from fastapi.testclient import TestClient


class TestContractAPI:
    """Contract CRUD + version management API tests."""

    def test_health_check(self, client: TestClient):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "database" in data

    def test_root(self, client: TestClient):
        response = client.get("/")
        assert response.status_code == 200
        assert "DataContractor" in response.json()["message"]

    def test_create_contract(self, client: TestClient):
        payload = {
            "name": "users_events",
            "description": "User events tracking contract",
            "owner": "team-a",
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
            ],
        }
        response = client.post("/contracts", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "users_events"
        assert data["owner"] == "team-a"

    def test_create_duplicate_contract(self, client: TestClient):
        payload = {
            "name": "dup_test",
            "owner": "team-b",
            "version": "1.0.0",
            "schema": {"fields": [{"name": "id", "type": "integer", "required": True}]},
            "quality_rules": [],
        }
        # First creation
        client.post("/contracts", json=payload)
        # Duplicate
        response = client.post("/contracts", json=payload)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_list_contracts(self, client: TestClient):
        # Create a contract first
        client.post(
            "/contracts",
            json={
                "name": "list_test",
                "owner": "team-c",
                "version": "1.0.0",
                "schema": {"fields": []},
                "quality_rules": [],
            },
        )
        response = client.get("/contracts")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        names = [c["name"] for c in data]
        assert "list_test" in names

    def test_get_contract(self, client: TestClient):
        client.post(
            "/contracts",
            json={
                "name": "get_test",
                "owner": "team-d",
                "version": "1.0.0",
                "schema": {"fields": []},
                "quality_rules": [],
            },
        )
        response = client.get("/contracts/get_test")
        assert response.status_code == 200
        assert response.json()["name"] == "get_test"

    def test_get_nonexistent_contract(self, client: TestClient):
        response = client.get("/contracts/nonexistent")
        assert response.status_code == 404

    def test_add_version(self, client: TestClient):
        client.post(
            "/contracts",
            json={
                "name": "version_test",
                "owner": "team-e",
                "version": "1.0.0",
                "schema": {"fields": [{"name": "id", "type": "integer", "required": True}]},
                "quality_rules": [],
            },
        )
        response = client.post(
            "/contracts/version_test/versions",
            json={
                "version": "1.1.0",
                "schema": {
                    "fields": [
                        {"name": "id", "type": "integer", "required": True},
                        {"name": "name", "type": "string", "required": False},
                    ]
                },
                "quality_rules": [],
                "allow_breaking": False,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["version"] == "1.1.0"

    def test_add_version_breaking_change_blocked(self, client: TestClient):
        client.post(
            "/contracts",
            json={
                "name": "breaking_test",
                "owner": "team-f",
                "version": "1.0.0",
                "schema": {"fields": [{"name": "id", "type": "integer", "required": True}]},
                "quality_rules": [],
            },
        )
        response = client.post(
            "/contracts/breaking_test/versions",
            json={
                "version": "2.0.0",
                "schema": {"fields": [{"name": "id", "type": "string", "required": True}]},
                "quality_rules": [],
                "allow_breaking": False,
            },
        )
        # Type change is a breaking change
        assert response.status_code == 409

    def test_add_version_breaking_change_allowed(self, client: TestClient):
        client.post(
            "/contracts",
            json={
                "name": "breaking_allowed_test",
                "owner": "team-g",
                "version": "1.0.0",
                "schema": {"fields": [{"name": "id", "type": "integer", "required": True}]},
                "quality_rules": [],
            },
        )
        response = client.post(
            "/contracts/breaking_allowed_test/versions",
            json={
                "version": "2.0.0",
                "schema": {"fields": [{"name": "id", "type": "string", "required": True}]},
                "quality_rules": [],
                "allow_breaking": True,
            },
        )
        assert response.status_code == 201
        assert response.json()["version"] == "2.0.0"

    def test_list_versions(self, client: TestClient):
        client.post(
            "/contracts",
            json={
                "name": "list_ver_test",
                "owner": "team-h",
                "version": "1.0.0",
                "schema": {"fields": []},
                "quality_rules": [],
            },
        )
        response = client.get("/contracts/list_ver_test/versions")
        assert response.status_code == 200
        versions = response.json()
        assert isinstance(versions, list)
        assert any(v["version"] == "1.0.0" for v in versions)

    def test_compare_versions(self, client: TestClient):
        client.post(
            "/contracts",
            json={
                "name": "compare_test",
                "owner": "team-i",
                "version": "1.0.0",
                "schema": {"fields": [{"name": "id", "type": "integer", "required": True}]},
                "quality_rules": [],
            },
        )
        client.post(
            "/contracts/compare_test/versions",
            json={
                "version": "2.0.0",
                "schema": {
                    "fields": [
                        {"name": "id", "type": "integer", "required": True},
                        {"name": "name", "type": "string", "required": False},
                    ]
                },
                "quality_rules": [],
                "allow_breaking": True,
            },
        )
        response = client.post(
            "/contracts/compare_test/compare-versions",
            json={
                "old_version": "1.0.0",
                "new_version": "2.0.0",
            },
        )
        assert response.status_code == 200
        report = response.json()
        assert "compatible" in report
