"""Unit tests for ETLService."""

import tempfile

import pytest
import yaml
from sqlalchemy.orm import Session

from app.services.etl_service import ETLService


@pytest.fixture
def valid_yaml():
    """Create a temporary valid contract YAML file."""
    data = {
        "name": "test_from_yaml",
        "version": "1.0.0",
        "description": "Contract loaded from YAML",
        "owner": "etl-bot",
        "schema": {
            "fields": [
                {"name": "id", "type": "integer", "required": True, "nullable": False},
            ]
        },
        "quality_rules": [],
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(data, f)
        path = f.name
    yield path


class TestETLService:
    def test_load_contract_from_yaml(self, valid_yaml: str):
        db = None  # load_contract_from_yaml does not need a DB
        service = ETLService(db)
        result = service.load_contract_from_yaml(valid_yaml)
        assert result["name"] == "test_from_yaml"
        assert result["version"] == "1.0.0"
        assert "schema" in result
        assert "fields" in result["schema"]

    def test_load_contract_from_yaml_not_found(self):
        db = None
        service = ETLService(db)
        with pytest.raises(FileNotFoundError):
            service.load_contract_from_yaml("/nonexistent/path.yaml")

    def test_register_contract_from_yaml(self, test_db_session: Session, valid_yaml: str):
        service = ETLService(test_db_session)
        result = service.register_contract_from_yaml(valid_yaml)
        assert result is not None
        assert result.name == "test_from_yaml"

    def test_register_contract_from_yaml_idempotent(self, test_db_session: Session, valid_yaml: str):
        service = ETLService(test_db_session)
        first = service.register_contract_from_yaml(valid_yaml)
        second = service.register_contract_from_yaml(valid_yaml)
        # Should return the same contract (idempotent)
        assert first.id == second.id
