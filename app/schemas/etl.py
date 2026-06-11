from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ETLRunResponse(BaseModel):
    id: UUID
    contract_id: UUID
    contract_version_id: UUID
    dataset_name: str
    status: str
    started_at: datetime
    finished_at: datetime | None
    rows_checked: int
    violations_count: int

    model_config = {"from_attributes": True}
