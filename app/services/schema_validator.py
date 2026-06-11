from datetime import datetime

import pandas as pd


class SchemaValidator:
    TYPE_CHECKERS = {
        "string": lambda v: isinstance(v, str),
        "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
        "float": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
        "decimal": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
        "boolean": lambda v: isinstance(v, bool),
        "date": lambda v: _is_date(v),
        "timestamp": lambda v: _is_timestamp(v),
        "enum": lambda v: True,
    }

    def validate(self, df: pd.DataFrame, schema: dict) -> dict:
        fields = schema.get("fields", [])
        field_map = {f["name"]: f for f in fields}

        errors = []
        warnings = []

        schema_columns = set(field_map.keys())
        df_columns = set(df.columns)

        missing = schema_columns - df_columns
        for col in missing:
            field = field_map[col]
            if field.get("required", True):
                errors.append(
                    {
                        "field": col,
                        "error": "missing_required_field",
                        "severity": "critical",
                        "message": f"Required field '{col}' is missing from dataset",
                    }
                )
            else:
                warnings.append(
                    {
                        "field": col,
                        "error": "missing_optional_field",
                        "severity": "info",
                        "message": f"Optional field '{col}' is missing from dataset",
                    }
                )

        extra = df_columns - schema_columns
        for col in extra:
            warnings.append(
                {
                    "field": col,
                    "error": "unexpected_field",
                    "severity": "info",
                    "message": f"Unexpected field '{col}' in dataset",
                }
            )

        for col_name, field_def in field_map.items():
            if col_name not in df.columns:
                continue

            col = df[col_name]

            if not field_def.get("nullable", False):
                null_count = col.isna().sum()
                if null_count > 0:
                    errors.append(
                        {
                            "field": col_name,
                            "error": "null_value_in_non_nullable",
                            "severity": "error",
                            "failed_rows": int(null_count),
                            "message": f"Field '{col_name}' has {null_count} null values but is non-nullable",
                        }
                    )

            expected_type = field_def.get("type", "string")
            if expected_type == "enum":
                allowed = set(field_def.get("values") or [])
                non_null = col.dropna()
                if len(non_null) > 0 and allowed:
                    invalid = non_null[~non_null.isin(allowed)]
                    if len(invalid) > 0:
                        errors.append(
                            {
                                "field": col_name,
                                "error": "invalid_enum_value",
                                "severity": "error",
                                "failed_rows": int(len(invalid)),
                                "message": f"Field '{col_name}' contains values not in allowed set",
                                "sample_values": invalid.head(5).tolist(),
                            }
                        )
            else:
                checker = self.TYPE_CHECKERS.get(expected_type)
                if checker:
                    non_null = col.dropna()
                    type_errors = non_null[~non_null.apply(checker)]
                    if len(type_errors) > 0:
                        errors.append(
                            {
                                "field": col_name,
                                "error": "type_mismatch",
                                "severity": "error",
                                "failed_rows": int(len(type_errors)),
                                "message": (
                                    f"Field '{col_name}' has {len(type_errors)} values "
                                    f"that don't match type '{expected_type}'"
                                ),
                            }
                        )

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "rows_checked": len(df),
        }


def _is_date(v) -> bool:
    if isinstance(v, (datetime,)):
        return True
    if isinstance(v, str):
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
            return True
        except (ValueError, TypeError):
            return False
    return False


def _is_timestamp(v) -> bool:
    return _is_date(v)
