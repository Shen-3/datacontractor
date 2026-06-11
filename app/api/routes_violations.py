from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.db.repositories import ValidationRunRepository
from app.schemas.violation import ViolationResponse, ViolationStatusUpdate
from app.services.violation_service import ViolationService

router = APIRouter(tags=["violations"])


@router.get("/violations", response_model=list[ViolationResponse])
def list_violations(db: Session = Depends(get_db)):
    service = ViolationService(db)
    return service.list_violations()


@router.get("/violations/{violation_id}", response_model=ViolationResponse)
def get_violation(violation_id: str, db: Session = Depends(get_db)):
    service = ViolationService(db)
    v = service.get_violation(violation_id)
    if not v:
        raise HTTPException(status_code=404, detail=f"Violation '{violation_id}' not found")
    return v


@router.patch("/violations/{violation_id}/status", response_model=ViolationResponse)
def update_violation_status(
    violation_id: str,
    data: ViolationStatusUpdate,
    db: Session = Depends(get_db),
):
    service = ViolationService(db)
    try:
        v = service.update_status(violation_id, data.status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not v:
        raise HTTPException(status_code=404, detail=f"Violation '{violation_id}' not found")
    return v
