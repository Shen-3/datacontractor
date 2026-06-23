from datetime import datetime, timezone

import pandas as pd


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


class QualityEngine:
    def run_checks(self, df: pd.DataFrame, rules: list[dict]) -> list[CheckResult]:
        results = []
        for rule in rules:
            check_type = rule.get("type", "")
            handler = getattr(self, f"_check_{check_type}", None)
            if handler:
                result = handler(df, rule)
                if result:
                    results.append(result)
        return results

    def _check_not_null(self, df: pd.DataFrame, rule: dict) -> CheckResult:
        field = rule["field"]
        if field not in df.columns:
            return CheckResult(
                name=rule["name"],
                check_type="not_null",
                field=field,
                passed=False,
                severity=rule.get("severity", "error"),
                failed_rows_count=len(df),
                message=f"Field '{field}' not found in dataset",
            )
        col = df[field]
        null_mask = col.isna()
        failed_count = int(null_mask.sum())
        samples = []
        if failed_count > 0:
            samples = df[null_mask].head(5).to_dict("records")
        return CheckResult(
            name=rule["name"],
            check_type="not_null",
            field=field,
            passed=failed_count == 0,
            severity=rule.get("severity", "error"),
            failed_rows_count=failed_count,
            sample_records=samples,
            message=f"Field '{field}' has {failed_count} null values" if failed_count > 0 else "",
        )

    def _check_unique(self, df: pd.DataFrame, rule: dict) -> CheckResult:
        field = rule["field"]
        if field not in df.columns:
            return CheckResult(
                name=rule["name"],
                check_type="unique",
                field=field,
                passed=False,
                severity=rule.get("severity", "error"),
                failed_rows_count=len(df),
                message=f"Field '{field}' not found in dataset",
            )
        col = df[field]
        dup_mask = col.duplicated(keep="first")
        failed_count = int(dup_mask.sum())
        samples = []
        if failed_count > 0:
            samples = df[dup_mask].head(5).to_dict("records")
        return CheckResult(
            name=rule["name"],
            check_type="unique",
            field=field,
            passed=failed_count == 0,
            severity=rule.get("severity", "error"),
            failed_rows_count=failed_count,
            sample_records=samples,
            message=f"Field '{field}' has {failed_count} duplicate values" if failed_count > 0 else "",
        )

    def _check_allowed_values(self, df: pd.DataFrame, rule: dict) -> CheckResult:
        field = rule["field"]
        allowed = set(rule.get("values", []))
        if field not in df.columns:
            return CheckResult(
                name=rule["name"],
                check_type="allowed_values",
                field=field,
                passed=False,
                severity=rule.get("severity", "error"),
                failed_rows_count=len(df),
                message=f"Field '{field}' not found in dataset",
            )
        col = df[field].dropna()
        if len(col) == 0:
            return CheckResult(
                name=rule["name"],
                check_type="allowed_values",
                field=field,
                passed=True,
                severity=rule.get("severity", "error"),
            )
        invalid = col[~col.isin(allowed)]
        failed_count = int(len(invalid))
        samples = []
        if failed_count > 0:
            samples = df.loc[invalid.index].head(5).to_dict("records")
        return CheckResult(
            name=rule["name"],
            check_type="allowed_values",
            field=field,
            passed=failed_count == 0,
            severity=rule.get("severity", "error"),
            failed_rows_count=failed_count,
            sample_records=samples,
            message=f"Field '{field}' contains {failed_count} values outside allowed set" if failed_count > 0 else "",
        )

    def _check_regex(self, df: pd.DataFrame, rule: dict) -> CheckResult:

        field = rule["field"]
        pattern = rule.get("pattern", "")
        if field not in df.columns:
            return CheckResult(
                name=rule["name"],
                check_type="regex",
                field=field,
                passed=False,
                severity=rule.get("severity", "error"),
                failed_rows_count=len(df),
                message=f"Field '{field}' not found in dataset",
            )
        col = df[field].dropna().astype(str)
        if len(col) == 0:
            return CheckResult(
                name=rule["name"],
                check_type="regex",
                field=field,
                passed=True,
                severity=rule.get("severity", "error"),
            )
        match = col.str.match(pattern)
        failed_count = int((~match).sum())
        samples = []
        if failed_count > 0:
            samples = df.loc[col[~match].index].head(5).to_dict("records")
        return CheckResult(
            name=rule["name"],
            check_type="regex",
            field=field,
            passed=failed_count == 0,
            severity=rule.get("severity", "error"),
            failed_rows_count=failed_count,
            sample_records=samples,
            message=f"Field '{field}' has {failed_count} values not matching pattern" if failed_count > 0 else "",
        )

    def _check_min_value(self, df: pd.DataFrame, rule: dict) -> CheckResult:
        field = rule["field"]
        min_val = rule.get("min_value", 0)
        if field not in df.columns:
            return CheckResult(
                name=rule["name"],
                check_type="min_value",
                field=field,
                passed=False,
                severity=rule.get("severity", "error"),
                failed_rows_count=len(df),
                message=f"Field '{field}' not found in dataset",
            )
        col = pd.to_numeric(df[field], errors="coerce")
        invalid = col[col < min_val]
        failed_count = int(len(invalid.dropna()))
        samples = []
        if failed_count > 0:
            samples = df.loc[invalid.dropna().index].head(5).to_dict("records")
        return CheckResult(
            name=rule["name"],
            check_type="min_value",
            field=field,
            passed=failed_count == 0,
            severity=rule.get("severity", "error"),
            failed_rows_count=failed_count,
            sample_records=samples,
            message=f"Field '{field}' has {failed_count} values below {min_val}" if failed_count > 0 else "",
        )

    def _check_max_value(self, df: pd.DataFrame, rule: dict) -> CheckResult:
        field = rule["field"]
        max_val = rule.get("max_value", 0)
        if field not in df.columns:
            return CheckResult(
                name=rule["name"],
                check_type="max_value",
                field=field,
                passed=False,
                severity=rule.get("severity", "error"),
                failed_rows_count=len(df),
                message=f"Field '{field}' not found in dataset",
            )
        col = pd.to_numeric(df[field], errors="coerce")
        invalid = col[col > max_val]
        failed_count = int(len(invalid.dropna()))
        samples = []
        if failed_count > 0:
            samples = df.loc[invalid.dropna().index].head(5).to_dict("records")
        return CheckResult(
            name=rule["name"],
            check_type="max_value",
            field=field,
            passed=failed_count == 0,
            severity=rule.get("severity", "error"),
            failed_rows_count=failed_count,
            sample_records=samples,
            message=f"Field '{field}' has {failed_count} values above {max_val}" if failed_count > 0 else "",
        )

    def _check_type_check(self, df: pd.DataFrame, rule: dict) -> CheckResult:
        field = rule["field"]
        expected_type = rule.get("expected_type", "string")
        if field not in df.columns:
            return CheckResult(
                name=rule["name"],
                check_type="type_check",
                field=field,
                passed=False,
                severity=rule.get("severity", "error"),
                failed_rows_count=len(df),
                message=f"Field '{field}' not found in dataset",
            )
        col = df[field].dropna()
        type_map = {
            "string": lambda v: isinstance(v, str),
            "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
            "float": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
            "decimal": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
            "boolean": lambda v: isinstance(v, bool),
        }
        checker = type_map.get(expected_type, lambda v: True)
        invalid = col[~col.apply(checker)]
        failed_count = int(len(invalid))
        return CheckResult(
            name=rule["name"],
            check_type="type_check",
            field=field,
            passed=failed_count == 0,
            severity=rule.get("severity", "error"),
            failed_rows_count=failed_count,
            message=f"Field '{field}' has {failed_count} values not matching type '{expected_type}'"
            if failed_count > 0
            else "",
        )

    def _check_row_count_min(self, df: pd.DataFrame, rule: dict) -> CheckResult:
        min_rows = rule.get("min_rows", 0)
        count = len(df)
        passed = count >= min_rows
        return CheckResult(
            name=rule["name"],
            check_type="row_count_min",
            field=None,
            passed=passed,
            severity=rule.get("severity", "error"),
            failed_rows_count=0 if passed else min_rows - count,
            message=f"Row count {count} is below minimum {min_rows}" if not passed else "",
        )

    def _check_row_count_max(self, df: pd.DataFrame, rule: dict) -> CheckResult:
        max_rows = rule.get("max_rows", float("inf"))
        count = len(df)
        passed = count <= max_rows
        return CheckResult(
            name=rule["name"],
            check_type="row_count_max",
            field=None,
            passed=passed,
            severity=rule.get("severity", "error"),
            failed_rows_count=0 if passed else count - max_rows,
            message=f"Row count {count} exceeds maximum {max_rows}" if not passed else "",
        )

    def _check_freshness(self, df: pd.DataFrame, rule: dict) -> CheckResult:
        field = rule["field"]
        max_delay = rule.get("max_delay_minutes", 1440)
        if field not in df.columns:
            return CheckResult(
                name=rule["name"],
                check_type="freshness",
                field=field,
                passed=False,
                severity=rule.get("severity", "warning"),
                message=f"Field '{field}' not found in dataset",
            )
        col = df[field].dropna()
        if len(col) == 0:
            return CheckResult(
                name=rule["name"],
                check_type="freshness",
                field=field,
                passed=False,
                severity=rule.get("severity", "warning"),
                message=f"Field '{field}' has no values to check freshness",
            )
        try:
            timestamps = pd.to_datetime(col)
            max_ts = timestamps.max()
            now = pd.Timestamp.now(tz=timezone.utc)
            if max_ts.tzinfo is None:
                max_ts = max_ts.replace(tzinfo=timezone.utc)
            delay = (now - max_ts).total_seconds() / 60
            passed = delay <= max_delay
            return CheckResult(
                name=rule["name"],
                check_type="freshness",
                field=field,
                passed=passed,
                severity=rule.get("severity", "warning"),
                message=f"Data is {delay:.0f} minutes old (max allowed: {max_delay})" if not passed else "",
            )
        except Exception:
            return CheckResult(
                name=rule["name"],
                check_type="freshness",
                field=field,
                passed=False,
                severity=rule.get("severity", "warning"),
                message=f"Could not parse timestamps in field '{field}'",
            )

    def _check_duplicate_rate(self, df: pd.DataFrame, rule: dict) -> CheckResult:
        field = rule["field"]
        threshold = rule.get("threshold", 0.01)
        if field not in df.columns:
            return CheckResult(
                name=rule["name"],
                check_type="duplicate_rate",
                field=field,
                passed=True,
                severity=rule.get("severity", "warning"),
            )
        col = df[field]
        total = len(col)
        if total == 0:
            return CheckResult(
                name=rule["name"],
                check_type="duplicate_rate",
                field=field,
                passed=True,
                severity=rule.get("severity", "warning"),
            )
        dup_count = int(col.duplicated().sum())
        rate = dup_count / total
        passed = rate <= threshold
        return CheckResult(
            name=rule["name"],
            check_type="duplicate_rate",
            field=field,
            passed=passed,
            severity=rule.get("severity", "warning"),
            failed_rows_count=dup_count,
            message=f"Duplicate rate for '{field}' is {rate:.2%} (threshold: {threshold:.2%})" if not passed else "",
        )

    def _check_null_rate(self, df: pd.DataFrame, rule: dict) -> CheckResult:
        field = rule["field"]
        threshold = rule.get("threshold", 0.05)
        if field not in df.columns:
            return CheckResult(
                name=rule["name"],
                check_type="null_rate",
                field=field,
                passed=False,
                severity=rule.get("severity", "warning"),
                failed_rows_count=len(df),
                message=f"Field '{field}' not found in dataset",
            )
        col = df[field]
        total = len(col)
        if total == 0:
            return CheckResult(
                name=rule["name"],
                check_type="null_rate",
                field=field,
                passed=True,
                severity=rule.get("severity", "warning"),
            )
        null_count = int(col.isna().sum())
        rate = null_count / total
        passed = rate <= threshold
        return CheckResult(
            name=rule["name"],
            check_type="null_rate",
            field=field,
            passed=passed,
            severity=rule.get("severity", "warning"),
            failed_rows_count=null_count,
            message=f"Null rate for '{field}' is {rate:.2%} (threshold: {threshold:.2%})" if not passed else "",
        )

    def _check_schema_match(self, df: pd.DataFrame, rule: dict) -> CheckResult:
        expected_fields = rule.get("fields", [])
        if not expected_fields:
            return CheckResult(
                name=rule["name"],
                check_type="schema_match",
                field=None,
                passed=True,
                severity=rule.get("severity", "warning"),
            )
        df_cols = set(df.columns)
        missing = [f for f in expected_fields if f not in df_cols]
        passed = len(missing) == 0
        return CheckResult(
            name=rule["name"],
            check_type="schema_match",
            field=None,
            passed=passed,
            severity=rule.get("severity", "warning"),
            failed_rows_count=len(missing),
            message=f"Missing fields: {missing}" if not passed else "",
        )
