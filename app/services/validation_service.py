import json

import pandas as pd
from sqlalchemy.orm import Session

from app.core.security import safe_resolve_path
from app.db.repositories import (
    ContractRepository,
    ContractVersionRepository,
    ValidationRunRepository,
    ViolationRepository,
)
from app.quality.checks import QualityEngine
from app.services.schema_validator import SchemaValidator


class ValidationService:
    def __init__(self, db: Session):
        self.db = db
        self.contract_repo = ContractRepository(db)
        self.version_repo = ContractVersionRepository(db)
        self.run_repo = ValidationRunRepository(db)
        self.violation_repo = ViolationRepository(db)
        self.schema_validator = SchemaValidator()
        self.quality_engine = QualityEngine()

    def validate_data(self, contract_name: str, dataset_path: str, dataset_name: str | None = None):
        contract = self.contract_repo.get_by_name(contract_name)
        if not contract:
            raise ValueError(f"Contract '{contract_name}' not found")

        active_version = self.version_repo.get_active_version(contract.id)
        if not active_version:
            raise ValueError(f"No active version for contract '{contract_name}'")

        # Resolve dataset path safely, preventing path traversal
        safe_path = safe_resolve_path(dataset_path)

        dataset_name = dataset_name or safe_path.name

        run = self.run_repo.create(
            contract_id=contract.id,
            contract_version_id=active_version.id,
            dataset_name=dataset_name,
            status="running",
        )

        try:
            df = pd.read_csv(str(safe_path))
        except Exception as e:
            self.run_repo.update_result(run.id, "error", 0, 0)
            raise ValueError(f"Failed to load dataset: {e}")

        schema = active_version.schema_json or {"fields": []}
        quality_rules = active_version.quality_rules_json or []

        schema_result = self.schema_validator.validate(df, schema)
        quality_results = self.quality_engine.run_checks(df, quality_rules)

        all_violations = []

        # Collect all violation records for bulk insert
        violation_records = []

        for err in schema_result.get("errors", []):
            violation_records.append(
                {
                    "validation_run_id": run.id,
                    "contract_name": contract_name,
                    "contract_version": active_version.version,
                    "check_name": f"schema_{err['error']}",
                    "check_type": "schema_validation",
                    "field_name": err.get("field"),
                    "severity": err.get("severity", "error"),
                    "failed_rows_count": err.get("failed_rows", 0),
                    "sample_records_json": None,
                    "message": err.get("message", ""),
                }
            )

        for qr in quality_results:
            if not qr.passed:
                sample_records = qr.sample_records[:10] if qr.sample_records else None
                violation_records.append(
                    {
                        "validation_run_id": run.id,
                        "contract_name": contract_name,
                        "contract_version": active_version.version,
                        "check_name": qr.name,
                        "check_type": qr.check_type,
                        "field_name": qr.field,
                        "severity": qr.severity,
                        "failed_rows_count": qr.failed_rows_count,
                        "sample_records_json": json.dumps(sample_records) if sample_records else None,
                        "message": qr.message,
                    }
                )

        # Bulk insert all violations in a single operation
        if violation_records:
            all_violations = self.violation_repo.bulk_create(violation_records)
        else:
            all_violations = []

        has_critical = any(v.severity == "critical" for v in all_violations)
        status = "failed" if all_violations else "passed"
        if has_critical:
            status = "blocked"

        self.run_repo.update_result(
            run.id,
            status=status,
            rows_checked=len(df),
            violations_count=len(all_violations),
        )

        return {
            "contract": contract_name,
            "version": active_version.version,
            "dataset": dataset_name,
            "status": status,
            "rows_checked": len(df),
            "violations_count": len(all_violations),
            "violations": [
                {
                    "check_name": v.check_name,
                    "severity": v.severity,
                    "failed_rows_count": v.failed_rows_count,
                    "message": v.message or "",
                }
                for v in all_violations
            ],
            "run_id": str(run.id),
        }
