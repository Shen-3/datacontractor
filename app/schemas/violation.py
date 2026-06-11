from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ViolationResponse(BaseModel):
    id: UUID
    validation_run_id: UUID
    contract_name: str
    contract_version: str
    check_name: str
    check_type: str
    field_name: str | None
    severity: str
    status: str
    failed_rows_count: int
    sample_records_json: list | None
    message: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ViolationStatusUpdate(BaseModel):
    status: str
