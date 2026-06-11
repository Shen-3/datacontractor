from sqlalchemy.orm import Session

from app.db.models import Contract, ContractVersion, ValidationRun, Violation


class ContractRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str, description: str | None, owner: str) -> Contract:
        contract = Contract(name=name, description=description, owner=owner)
        self.db.add(contract)
        self.db.commit()
        self.db.refresh(contract)
        return contract

    def get_by_name(self, name: str) -> Contract | None:
        return self.db.query(Contract).filter(Contract.name == name).first()

    def list_all(self) -> list[Contract]:
        return self.db.query(Contract).all()


class ContractVersionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        contract_id,
        version: str,
        schema_json: dict | None,
        quality_rules_json: list | None,
        sla_json: dict | None,
        compatibility_mode: str = "backward",
    ) -> ContractVersion:
        cv = ContractVersion(
            contract_id=contract_id,
            version=version,
            schema_json=schema_json,
            quality_rules_json=quality_rules_json,
            sla_json=sla_json,
            compatibility_mode=compatibility_mode,
        )
        self.db.add(cv)
        self.db.commit()
        self.db.refresh(cv)
        return cv

    def get_active_version(self, contract_id) -> ContractVersion | None:
        return (
            self.db.query(ContractVersion)
            .filter(ContractVersion.contract_id == contract_id, ContractVersion.is_active == True)
            .first()
        )

    def list_by_contract(self, contract_id) -> list[ContractVersion]:
        return (
            self.db.query(ContractVersion)
            .filter(ContractVersion.contract_id == contract_id)
            .order_by(ContractVersion.created_at.desc())
            .all()
        )

    def get_by_version(self, contract_id, version: str) -> ContractVersion | None:
        return (
            self.db.query(ContractVersion)
            .filter(ContractVersion.contract_id == contract_id, ContractVersion.version == version)
            .first()
        )


class ValidationRunRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        contract_id,
        contract_version_id,
        dataset_name: str,
        status: str,
    ) -> ValidationRun:
        vr = ValidationRun(
            contract_id=contract_id,
            contract_version_id=contract_version_id,
            dataset_name=dataset_name,
            status=status,
        )
        self.db.add(vr)
        self.db.commit()
        self.db.refresh(vr)
        return vr

    def update_result(self, run_id, status: str, rows_checked: int, violations_count: int):
        vr = self.db.query(ValidationRun).filter(ValidationRun.id == run_id).first()
        if vr:
            vr.status = status
            vr.rows_checked = rows_checked
            vr.violations_count = violations_count
            self.db.commit()

    def get_by_id(self, run_id) -> ValidationRun | None:
        return self.db.query(ValidationRun).filter(ValidationRun.id == run_id).first()

    def list_all(self) -> list[ValidationRun]:
        return self.db.query(ValidationRun).order_by(ValidationRun.started_at.desc()).all()


class ViolationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        validation_run_id,
        contract_name: str,
        contract_version: str,
        check_name: str,
        check_type: str,
        field_name: str | None,
        severity: str,
        failed_rows_count: int,
        sample_records_json: list | None,
        message: str | None,
    ) -> Violation:
        v = Violation(
            validation_run_id=validation_run_id,
            contract_name=contract_name,
            contract_version=contract_version,
            check_name=check_name,
            check_type=check_type,
            field_name=field_name,
            severity=severity,
            failed_rows_count=failed_rows_count,
            sample_records_json=sample_records_json,
            message=message,
        )
        self.db.add(v)
        self.db.commit()
        self.db.refresh(v)
        return v

    def get_by_id(self, violation_id) -> Violation | None:
        return self.db.query(Violation).filter(Violation.id == violation_id).first()

    def list_all(self) -> list[Violation]:
        return self.db.query(Violation).order_by(Violation.created_at.desc()).all()

    def update_status(self, violation_id, status: str):
        v = self.db.query(Violation).filter(Violation.id == violation_id).first()
        if v:
            v.status = status
            self.db.commit()
