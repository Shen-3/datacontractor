from uuid import UUID

from sqlalchemy.orm import Session

from app.core.errors import BreakingChangesError
from app.db.repositories import ContractRepository, ContractVersionRepository
from app.schemas.contract import ContractCreate, VersionCreate


class ContractService:
    def __init__(self, db: Session):
        self.db = db
        self.contract_repo = ContractRepository(db)
        self.version_repo = ContractVersionRepository(db)

    def create_contract(self, data: ContractCreate):
        existing = self.contract_repo.get_by_name(data.name)
        if existing:
            raise ValueError(f"Contract '{data.name}' already exists")

        contract = self.contract_repo.create(
            name=data.name,
            description=data.description,
            owner=data.owner,
        )

        schema_data = data.schema.model_dump()
        quality_rules_data = [r.model_dump() for r in data.quality_rules]
        sla_data = data.sla.model_dump() if data.sla else None
        compat_data = data.compatibility.model_dump() if data.compatibility else {"mode": "backward"}

        self.version_repo.create(
            contract_id=contract.id,
            version=data.version,
            schema_json=schema_data,
            quality_rules_json=quality_rules_data,
            sla_json=sla_data,
            compatibility_mode=compat_data.get("mode", "backward"),
        )

        return contract

    def get_contract(self, name: str):
        return self.contract_repo.get_by_name(name)

    def list_contracts(self):
        return self.contract_repo.list_all()

    def list_versions(self, contract_id: UUID):
        return self.version_repo.list_by_contract(contract_id)

    def get_version(self, contract_id: UUID, version: str):
        return self.version_repo.get_by_version(contract_id, version)

    def get_active_version(self, contract_id: UUID):
        return self.version_repo.get_active_version(contract_id)

    def add_version(self, contract_name: str, data: VersionCreate):
        contract = self.contract_repo.get_by_name(contract_name)
        if not contract:
            raise ValueError(f"Contract '{contract_name}' not found")

        active_version = self.version_repo.get_active_version(contract.id)
        if active_version and not data.allow_breaking:
            from app.services.compatibility_checker import CompatibilityChecker

            checker = CompatibilityChecker()
            old_schema = active_version.schema_json or {"fields": []}
            new_schema = data.schema.model_dump()
            result = checker.check(old_schema, new_schema)
            if not result["compatible"]:
                raise BreakingChangesError(
                    {
                        "error": "breaking_changes_detected",
                        "compatible": result["compatible"],
                        "breaking_changes": result["breaking_changes"],
                        "warnings": result.get("warnings", []),
                    }
                )

        if active_version:
            active_version.is_active = False
            self.db.commit()

        schema_data = data.schema.model_dump()
        quality_rules_data = [r.model_dump() for r in data.quality_rules]
        sla_data = data.sla.model_dump() if data.sla else None
        compat_data = data.compatibility.model_dump() if data.compatibility else {"mode": "backward"}

        version = self.version_repo.create(
            contract_id=contract.id,
            version=data.version,
            schema_json=schema_data,
            quality_rules_json=quality_rules_data,
            sla_json=sla_data,
            compatibility_mode=compat_data.get("mode", "backward"),
        )

        return version
