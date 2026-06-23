"""Pipeline-level tests for schema validation and quality engine.

These tests verify the core logic components (SchemaValidator, QualityEngine)
work correctly with sample data.  They do not require a database.
"""

import os

import pandas as pd

from app.quality.checks import QualityEngine
from app.services.schema_validator import SchemaValidator


class TestETLPipeline:
    def test_schema_validator_with_sample_data(self, sample_df: pd.DataFrame, sample_schema: dict):
        validator = SchemaValidator()
        result = validator.validate(sample_df, sample_schema)
        assert result["valid"] is True

    def test_quality_engine_with_sample_data(self, sample_df: pd.DataFrame, sample_quality_rules: list):
        engine = QualityEngine()
        results = engine.run_checks(sample_df, sample_quality_rules)
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
