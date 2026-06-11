from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class SchemaField(BaseModel):
    name: str
    type: str = Field(..., pattern=r"^(string|integer|float|decimal|boolean|date|timestamp|enum)$")
    required: bool = True
    nullable: bool = False
    description: str | None = None
    values: list[str] | None = None


class SchemaDefinition(BaseModel):
    fields: list[SchemaField]


class QualityRule(BaseModel):
    name: str
    type: str
    field: str | None = None
    severity: str = Field(default="warning", pattern=r"^(info|warning|error|critical)$")
    values: list[str] | None = None
    max_delay_minutes: int | None = None
    min_value: float | None = None
    max_value: float | None = None
    pattern: str | None = None
    threshold: float | None = None


class SLADefinition(BaseModel):
    update_frequency: str | None = None
    max_delay_minutes: int | None = None


class CompatibilityDefinition(BaseModel):
    mode: str = "backward"


class ContractCreate(BaseModel):
    name: str
    description: str | None = None
    owner: str
    version: str = "1.0.0"
    schema: SchemaDefinition
    quality_rules: list[QualityRule] = []
    sla: SLADefinition | None = None
    compatibility: CompatibilityDefinition | None = None


class ContractResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    owner: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ContractVersionResponse(BaseModel):
    id: UUID
    contract_id: UUID
    version: str
    schema_json: dict | None
    quality_rules_json: list | None
    sla_json: dict | None
    compatibility_mode: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ContractDetailResponse(ContractResponse):
    versions: list[ContractVersionResponse] = []


class VersionCreate(BaseModel):
    version: str
    schema: SchemaDefinition
    quality_rules: list[QualityRule] = []
    sla: SLADefinition | None = None
    compatibility: CompatibilityDefinition | None = None
    allow_breaking: bool = False
