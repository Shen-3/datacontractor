import yaml
from sqlalchemy.orm import Session

from app.db.repositories import ContractRepository, ContractVersionRepository
from app.services.compatibility_checker import CompatibilityChecker


class ETLService:
    def __init__(self, db: Session):
        self.db = db
        self.contract_repo = ContractRepository(db)
        self.version_repo = ContractVersionRepository(db)
        self.checker = CompatibilityChecker()

    def load_contract_from_yaml(self, filepath: str) -> dict:
        with open(filepath) as f:
            return yaml.safe_load(f)

    def register_contract_from_yaml(self, filepath: str):
        data = self.load_contract_from_yaml(filepath)
        name = data["name"]

        existing = self.contract_repo.get_by_name(name)
        if existing:
            return existing

        contract = self.contract_repo.create(
            name=name,
            description=data.get("description", ""),
            owner=data.get("owner", "unknown"),
        )

        schema_data = data.get("schema", {})
        quality_rules = data.get("quality_rules", [])
        sla_data = data.get("sla")
        compat_data = data.get("compatibility", {"mode": "backward"})

        self.version_repo.create(
            contract_id=contract.id,
            version=data.get("version", "1.0.0"),
            schema_json=schema_data,
            quality_rules_json=quality_rules,
            sla_json=sla_data,
            compatibility_mode=compat_data.get("mode", "backward"),
        )

        return contract

    def compare_contract_versions(self, contract_name: str, old_version: str, new_version: str) -> dict:
        contract = self.contract_repo.get_by_name(contract_name)
        if not contract:
            raise ValueError(f"Contract '{contract_name}' not found")

        old = self.version_repo.get_by_version(contract.id, old_version)
        new = self.version_repo.get_by_version(contract.id, new_version)

        if not old:
            raise ValueError(f"Version '{old_version}' not found")
        if not new:
            raise ValueError(f"Version '{new_version}' not found")

        old_schema = old.schema_json or {"fields": []}
        new_schema = new.schema_json or {"fields": []}

        return self.checker.check(old_schema, new_schema)
