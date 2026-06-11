from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.db.repositories import ValidationRunRepository
from app.schemas.etl import ETLRunResponse

router = APIRouter(prefix="/etl", tags=["etl"])


@router.get("/runs", response_model=list[ETLRunResponse])
def list_runs(db: Session = Depends(get_db)):
    repo = ValidationRunRepository(db)
    return repo.list_all()


@router.get("/runs/{run_id}", response_model=ETLRunResponse)
def get_run(run_id: str, db: Session = Depends(get_db)):
    repo = ValidationRunRepository(db)
    run = repo.get_by_id(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")
    return run
