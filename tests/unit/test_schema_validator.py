import pandas as pd
import pytest

from app.services.schema_validator import SchemaValidator


@pytest.fixture
def validator():
    return SchemaValidator()


class TestSchemaValidator:
    def test_valid_dataset(self, validator):
        df = pd.DataFrame(
            {
                "user_id": [1, 2, 3],
                "event_type": ["login", "purchase", "logout"],
                "event_time": ["2025-01-01T10:00:00Z", "2025-01-01T11:00:00Z", "2025-01-01T12:00:00Z"],
                "amount": [None, 29.99, None],
            }
        )
        schema = {
            "fields": [
                {"name": "user_id", "type": "integer", "required": True, "nullable": False},
                {"name": "event_type", "type": "enum", "required": True, "nullable": False, "values": ["login", "purchase", "logout"]},
                {"name": "event_time", "type": "timestamp", "required": True, "nullable": False},
                {"name": "amount", "type": "decimal", "required": False, "nullable": True},
            ]
        }
        result = validator.validate(df, schema)
        assert result["valid"] is True
        assert result["rows_checked"] == 3

    def test_missing_required_field(self, validator):
        df = pd.DataFrame({"event_type": ["login"], "event_time": ["2025-01-01T10:00:00Z"]})
        schema = {"fields": [{"name": "user_id", "type": "integer", "required": True, "nullable": False}]}
        result = validator.validate(df, schema)
        assert result["valid"] is False
        assert any(e["error"] == "missing_required_field" for e in result["errors"])

    def test_missing_optional_field(self, validator):
        df = pd.DataFrame({"user_id": [1]})
        schema = {"fields": [{"name": "user_id", "type": "integer", "required": True}, {"name": "extra", "type": "string", "required": False}]}
        result = validator.validate(df, schema)
        assert result["valid"] is True
        assert len(result["warnings"]) > 0

    def test_null_in_non_nullable_field(self, validator):
        df = pd.DataFrame({"user_id": [1, None, 3]})
        schema = {"fields": [{"name": "user_id", "type": "integer", "required": True, "nullable": False}]}
        result = validator.validate(df, schema)
        assert result["valid"] is False
        assert any(e["error"] == "null_value_in_non_nullable" for e in result["errors"])

    def test_invalid_enum_value(self, validator):
        df = pd.DataFrame({"event_type": ["login", "signup", "logout"]})
        schema = {"fields": [{"name": "event_type", "type": "enum", "required": True, "values": ["login", "logout"]}]}
        result = validator.validate(df, schema)
        assert result["valid"] is False
        assert any(e["error"] == "invalid_enum_value" for e in result["errors"])

    def test_extra_columns_warning(self, validator):
        df = pd.DataFrame({"user_id": [1], "unknown_col": [2]})
        schema = {"fields": [{"name": "user_id", "type": "integer", "required": True}]}
        result = validator.validate(df, schema)
        assert result["valid"] is True
        assert any(w["error"] == "unexpected_field" for w in result["warnings"])

    def test_type_mismatch(self, validator):
        df = pd.DataFrame({"user_id": ["not_a_number"]})
        schema = {"fields": [{"name": "user_id", "type": "integer", "required": True}]}
        result = validator.validate(df, schema)
        assert result["valid"] is False
        assert any(e["error"] == "type_mismatch" for e in result["errors"])
