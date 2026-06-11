from datetime import datetime, timezone


class CheckResult:
    def __init__(
        self,
        name: str,
        check_type: str,
        field: str | None,
        passed: bool,
        severity: str,
        failed_rows_count: int = 0,
        sample_records: list | None = None,
        message: str = "",
    ):
        self.name = name
        self.check_type = check_type
        self.field = field
        self.passed = passed
        self.severity = severity
        self.failed_rows_count = failed_rows_count
        self.sample_records = sample_records or []
        self.message = message
        self.timestamp = datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "check_type": self.check_type,
            "field": self.field,
            "passed": self.passed,
            "severity": self.severity,
            "failed_rows_count": self.failed_rows_count,
            "sample_records": self.sample_records[:10],
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
        }
