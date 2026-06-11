from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ValidateDataRequest(BaseModel):
    dataset_path: str | None = None
    contract_name: str
    dataset_name: str | None = None


class ValidationViolationSummary(BaseModel):
    check_name: str
    severity: str
    failed_rows_count: int
    message: str


class ValidationSummary(BaseModel):
    contract: str
    version: str
    dataset: str
    status: str
    rows_checked: int
    violations_count: int
    violations: list[ValidationViolationSummary]


class CompareVersionsRequest(BaseModel):
    old_version: str
    new_version: str


class CompatibilityReport(BaseModel):
    compatible: bool
    breaking_changes: list[dict]
    warnings: list[dict]
