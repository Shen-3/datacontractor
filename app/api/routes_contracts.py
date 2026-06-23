from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.errors import BreakingChangesError
from app.db.base import get_db
from app.schemas.contract import (
    ContractCreate,
    ContractDetailResponse,
    ContractResponse,
    ContractVersionResponse,
    VersionCreate,
)
from app.services.contract_service import ContractService

router = APIRouter(prefix="/contracts", tags=["contracts"])


@router.post("", response_model=ContractResponse, status_code=201)
def create_contract(data: ContractCreate, db: Session = Depends(get_db)):
    service = ContractService(db)
    try:
        contract = service.create_contract(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return contract


@router.get("", response_model=list[ContractResponse])
def list_contracts(db: Session = Depends(get_db)):
    service = ContractService(db)
    return service.list_contracts()


@router.get("/{contract_name}", response_model=ContractDetailResponse)
def get_contract(contract_name: str, db: Session = Depends(get_db)):
    service = ContractService(db)
    contract = service.get_contract(contract_name)
    if not contract:
        raise HTTPException(status_code=404, detail=f"Contract '{contract_name}' not found")
    versions = service.list_versions(contract.id)
    return ContractDetailResponse(
        id=contract.id,
        name=contract.name,
        description=contract.description,
        owner=contract.owner,
        status=contract.status,
        created_at=contract.created_at,
        updated_at=contract.updated_at,
        versions=versions,
    )


@router.get("/{contract_name}/versions", response_model=list[ContractVersionResponse])
def list_versions(contract_name: str, db: Session = Depends(get_db)):
    service = ContractService(db)
    contract = service.get_contract(contract_name)
    if not contract:
        raise HTTPException(status_code=404, detail=f"Contract '{contract_name}' not found")
    return service.list_versions(contract.id)


@router.get("/{contract_name}/versions/{version}", response_model=ContractVersionResponse)
def get_version(contract_name: str, version: str, db: Session = Depends(get_db)):
    service = ContractService(db)
    contract = service.get_contract(contract_name)
    if not contract:
        raise HTTPException(status_code=404, detail=f"Contract '{contract_name}' not found")
    cv = service.get_version(contract.id, version)
    if not cv:
        raise HTTPException(status_code=404, detail=f"Version '{version}' not found")
    return cv


@router.post("/{contract_name}/versions", response_model=ContractVersionResponse, status_code=201)
def add_version(contract_name: str, data: VersionCreate, db: Session = Depends(get_db)):
    service = ContractService(db)
    try:
        version = service.add_version(contract_name, data)
    except BreakingChangesError as e:
        raise HTTPException(status_code=409, detail=e.detail)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return version
