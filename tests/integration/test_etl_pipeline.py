import os
import pandas as pd
import pytest

from app.services.schema_validator import SchemaValidator
from app.quality.checks import QualityEngine


@pytest.fixture
def sample_data():
    return pd.DataFrame(
        {
            "user_id": [1, 2, 3, 4, 5],
            "event_type": ["login", "purchase", "logout", "login", "purchase"],
            "event_time": ["2025-06-11T10:00:00Z"] * 5,
            "amount": [None, 29.99, None, None, 49.99],
        }
    )


class TestETLPipeline:
    def test_schema_validator_with_sample_data(self, sample_data):
        validator = SchemaValidator()
        schema = {
            "fields": [
                {"name": "user_id", "type": "integer", "required": True, "nullable": False},
                {"name": "event_type", "type": "enum", "required": True, "values": ["login", "purchase", "logout"]},
                {"name": "event_time", "type": "timestamp", "required": True},
                {"name": "amount", "type": "decimal", "required": False, "nullable": True},
            ]
        }
        result = validator.validate(sample_data, schema)
        assert result["valid"] is True

    def test_quality_engine_with_sample_data(self, sample_data):
        engine = QualityEngine()
        rules = [
            {"name": "uid_nn", "type": "not_null", "field": "user_id", "severity": "critical"},
            {"name": "etype_av", "type": "allowed_values", "field": "event_type", "values": ["login", "purchase", "logout"], "severity": "error"},
        ]
        results = engine.run_checks(sample_data, rules)
        assert all(r.passed for r in results)

    def test_csv_files_exist(self):
        data_dir = "data/datasets"
        expected_files = [
            "users_events_valid.csv",
            "users_events_missing_field.csv",
            "users_events_nulls.csv",
            "users_events_invalid_enum.csv",
            "users_events_duplicates.csv",
            "users_events_stale.csv",
        ]
        for f in expected_files:
            assert os.path.exists(os.path.join(data_dir, f)), f"Missing {f}"

    def test_contract_files_exist(self):
        data_dir = "data/contracts"
        expected_files = [
            "users_events_v1.yaml",
            "users_events_v2_valid.yaml",
            "users_events_v2_breaking.yaml",
        ]
        for f in expected_files:
            assert os.path.exists(os.path.join(data_dir, f)), f"Missing {f}"
