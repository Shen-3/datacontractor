from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.schemas.contract import SchemaDefinition
from app.schemas.validation import (
    CompareVersionsRequest,
    CompatibilityReport,
    ValidateDataRequest,
    ValidationSummary,
)
from app.services.compatibility_checker import CompatibilityChecker
from app.services.contract_service import ContractService
from app.services.validation_service import ValidationService

router = APIRouter(prefix="/contracts", tags=["validation"])


@router.post("/{contract_name}/validate-schema")
def validate_schema(
    contract_name: str,
    schema: SchemaDefinition,
    db: Session = Depends(get_db),
):
    service = ContractService(db)
    contract = service.get_contract(contract_name)
    if not contract:
        raise HTTPException(status_code=404, detail=f"Contract '{contract_name}' not found")

    active_version = service.get_active_version(contract.id)
    if not active_version:
        raise HTTPException(status_code=404, detail=f"No active version for '{contract_name}'")

    old_schema = active_version.schema_json or {"fields": []}
    new_schema = {"fields": [f.model_dump() for f in schema.fields]}

    checker = CompatibilityChecker()
    result = checker.check(old_schema, new_schema)
    return result


@router.post("/{contract_name}/validate-data", response_model=ValidationSummary)
def validate_data(
    contract_name: str,
    data: ValidateDataRequest,
    db: Session = Depends(get_db),
):
    service = ValidationService(db)
    if not data.dataset_path:
        raise HTTPException(status_code=400, detail="dataset_path is required")

    try:
        result = service.validate_data(
            contract_name=contract_name,
            dataset_path=data.dataset_path,
            dataset_name=data.dataset_name,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return ValidationSummary(**result)


@router.post("/{contract_name}/compare-versions", response_model=CompatibilityReport)
def compare_versions(
    contract_name: str,
    data: CompareVersionsRequest,
    db: Session = Depends(get_db),
):
    service = ContractService(db)
    contract = service.get_contract(contract_name)
    if not contract:
        raise HTTPException(status_code=404, detail=f"Contract '{contract_name}' not found")

    old_ver = service.get_version(contract.id, data.old_version)
    new_ver = service.get_version(contract.id, data.new_version)

    if not old_ver:
        raise HTTPException(status_code=404, detail=f"Version '{data.old_version}' not found")
    if not new_ver:
        raise HTTPException(status_code=404, detail=f"Version '{data.new_version}' not found")

    old_schema = old_ver.schema_json or {"fields": []}
    new_schema = new_ver.schema_json or {"fields": []}

    checker = CompatibilityChecker()
    result = checker.check(old_schema, new_schema)
    return CompatibilityReport(**result)
