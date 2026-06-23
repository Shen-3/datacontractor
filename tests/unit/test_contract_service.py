"""Unit tests for ContractService."""

from unittest.mock import MagicMock, patch

import pytest

from app.core.errors import BreakingChangesError
from app.schemas.contract import ContractCreate, SchemaDefinition, SchemaField, VersionCreate
from app.services.contract_service import ContractService


class TestContractService:
    def test_create_contract(self):
        db = MagicMock()
        service = ContractService(db)

        db.query.return_value.filter.return_value.first.return_value = None
        db.refresh = lambda x: x

        data = ContractCreate(
            name="test_contract",
            description="Test",
            owner="team-a",
            schema=SchemaDefinition(fields=[SchemaField(name="id", type="integer")]),
        )

        result = service.create_contract(data)
        assert result is not None

    def test_create_duplicate_contract_raises(self):
        db = MagicMock()
        service = ContractService(db)
        db.query.return_value.filter.return_value.first.return_value = MagicMock()

        data = ContractCreate(
            name="existing",
            owner="team",
            schema=SchemaDefinition(fields=[]),
        )
        with pytest.raises(ValueError, match="already exists"):
            service.create_contract(data)

    def test_list_contracts(self):
        db = MagicMock()
        service = ContractService(db)
        db.query.return_value.all.return_value = []
        result = service.list_contracts()
        assert result == []

    def test_add_version_nonexistent_contract(self):
        db = MagicMock()
        service = ContractService(db)
        db.query.return_value.filter.return_value.first.return_value = None

        data = VersionCreate(
            version="1.1.0",
            schema=SchemaDefinition(fields=[]),
            quality_rules=[],
        )
        with pytest.raises(ValueError, match="not found"):
            service.add_version("nonexistent", data)

    def test_add_version_success(self):
        db = MagicMock()
        service = ContractService(db)

        mock_contract = MagicMock()
        mock_contract.id = "contract-uuid"

        mock_active_version = MagicMock()
        mock_active_version.schema_json = {"fields": [{"name": "id", "type": "integer", "required": True}]}
        mock_active_version.is_active = True

        # Repository mocks
        service.contract_repo = MagicMock()
        service.contract_repo.get_by_name.return_value = mock_contract

        service.version_repo = MagicMock()
        service.version_repo.get_active_version.return_value = mock_active_version
        service.version_repo.create.return_value = MagicMock(version="1.1.0")

        data = VersionCreate(
            version="1.1.0",
            schema=SchemaDefinition(
                fields=[
                    SchemaField(name="id", type="integer", required=True),
                    SchemaField(name="name", type="string", required=False),
                ]
            ),
            quality_rules=[],
        )

        result = service.add_version("test_contract", data)
        assert result.version == "1.1.0"
        # The old active version should be deactivated
        assert mock_active_version.is_active is False

    @patch("app.services.compatibility_checker.CompatibilityChecker")
    def test_add_version_breaking_change_blocked(self, mock_checker):
        db = MagicMock()
        service = ContractService(db)

        mock_contract = MagicMock()
        mock_contract.id = "contract-uuid"

        mock_active = MagicMock()
        mock_active.schema_json = {"fields": [{"name": "id", "type": "integer", "required": True}]}

        service.contract_repo = MagicMock()
        service.contract_repo.get_by_name.return_value = mock_contract
        service.version_repo = MagicMock()
        service.version_repo.get_active_version.return_value = mock_active

        checker_instance = mock_checker.return_value
        checker_instance.check.return_value = {
            "compatible": False,
            "breaking_changes": [{"change": "type_changed", "field": "id"}],
            "warnings": [],
        }

        data = VersionCreate(
            version="2.0.0",
            schema=SchemaDefinition(fields=[SchemaField(name="id", type="string", required=True)]),
            quality_rules=[],
        )

        with pytest.raises(BreakingChangesError):
            service.add_version("test_contract", data)

    @patch("app.services.compatibility_checker.CompatibilityChecker")
    def test_add_version_breaking_change_allowed(self, mock_checker):
        db = MagicMock()
        service = ContractService(db)

        mock_contract = MagicMock()
        mock_contract.id = "contract-uuid"

        mock_active = MagicMock()
        mock_active.schema_json = {"fields": [{"name": "id", "type": "integer", "required": True}]}
        mock_active.is_active = True

        service.contract_repo = MagicMock()
        service.contract_repo.get_by_name.return_value = mock_contract
        service.version_repo = MagicMock()
        service.version_repo.get_active_version.return_value = mock_active
        service.version_repo.create.return_value = MagicMock(version="2.0.0")

        checker_instance = mock_checker.return_value
        checker_instance.check.return_value = {
            "compatible": False,
            "breaking_changes": [{"change": "type_changed", "field": "id"}],
            "warnings": [],
        }

        data = VersionCreate(
            version="2.0.0",
            schema=SchemaDefinition(fields=[SchemaField(name="id", type="string", required=True)]),
            quality_rules=[],
            allow_breaking=True,
        )

        result = service.add_version("test_contract", data)
        assert result.version == "2.0.0"
