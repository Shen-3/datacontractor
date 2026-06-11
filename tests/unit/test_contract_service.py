import pytest
from unittest.mock import MagicMock, patch
from app.services.contract_service import ContractService
from app.schemas.contract import ContractCreate, SchemaDefinition, SchemaField


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
