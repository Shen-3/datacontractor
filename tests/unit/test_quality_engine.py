import pandas as pd
import pytest

from app.quality.checks import QualityEngine


@pytest.fixture
def engine():
    return QualityEngine()


class TestQualityEngine:
    def test_not_null_pass(self, engine):
        df = pd.DataFrame({"user_id": [1, 2, 3]})
        rules = [{"name": "uid_nn", "type": "not_null", "field": "user_id", "severity": "critical"}]
        results = engine.run_checks(df, rules)
        assert len(results) == 1
        assert results[0].passed is True

    def test_not_null_fail(self, engine):
        df = pd.DataFrame({"user_id": [1, None, 3]})
        rules = [{"name": "uid_nn", "type": "not_null", "field": "user_id", "severity": "critical"}]
        results = engine.run_checks(df, rules)
        assert results[0].passed is False
        assert results[0].failed_rows_count == 1

    def test_unique_pass(self, engine):
        df = pd.DataFrame({"user_id": [1, 2, 3]})
        rules = [{"name": "uid_uniq", "type": "unique", "field": "user_id", "severity": "error"}]
        results = engine.run_checks(df, rules)
        assert results[0].passed is True

    def test_unique_fail(self, engine):
        df = pd.DataFrame({"user_id": [1, 1, 3]})
        rules = [{"name": "uid_uniq", "type": "unique", "field": "user_id", "severity": "error"}]
        results = engine.run_checks(df, rules)
        assert results[0].passed is False
        assert results[0].failed_rows_count == 1

    def test_allowed_values_pass(self, engine):
        df = pd.DataFrame({"status": ["active", "inactive", "active"]})
        rules = [
            {
                "name": "status_av",
                "type": "allowed_values",
                "field": "status",
                "values": ["active", "inactive"],
                "severity": "error",
            }
        ]
        results = engine.run_checks(df, rules)
        assert results[0].passed is True

    def test_allowed_values_fail(self, engine):
        df = pd.DataFrame({"status": ["active", "unknown", "active"]})
        rules = [
            {
                "name": "status_av",
                "type": "allowed_values",
                "field": "status",
                "values": ["active", "inactive"],
                "severity": "error",
            }
        ]
        results = engine.run_checks(df, rules)
        assert results[0].passed is False
        assert results[0].failed_rows_count == 1

    def test_min_value_pass(self, engine):
        df = pd.DataFrame({"amount": [10, 20, 30]})
        rules = [{"name": "amt_min", "type": "min_value", "field": "amount", "min_value": 5, "severity": "error"}]
        results = engine.run_checks(df, rules)
        assert results[0].passed is True

    def test_min_value_fail(self, engine):
        df = pd.DataFrame({"amount": [1, 20, 30]})
        rules = [{"name": "amt_min", "type": "min_value", "field": "amount", "min_value": 5, "severity": "error"}]
        results = engine.run_checks(df, rules)
        assert results[0].passed is False

    def test_max_value_pass(self, engine):
        df = pd.DataFrame({"amount": [10, 20, 30]})
        rules = [{"name": "amt_max", "type": "max_value", "field": "amount", "max_value": 100, "severity": "error"}]
        results = engine.run_checks(df, rules)
        assert results[0].passed is True

    def test_max_value_fail(self, engine):
        df = pd.DataFrame({"amount": [10, 200, 30]})
        rules = [{"name": "amt_max", "type": "max_value", "field": "amount", "max_value": 100, "severity": "error"}]
        results = engine.run_checks(df, rules)
        assert results[0].passed is False

    def test_row_count_min_pass(self, engine):
        df = pd.DataFrame({"a": range(10)})
        rules = [{"name": "rc_min", "type": "row_count_min", "min_rows": 5, "severity": "error"}]
        results = engine.run_checks(df, rules)
        assert results[0].passed is True

    def test_row_count_min_fail(self, engine):
        df = pd.DataFrame({"a": range(2)})
        rules = [{"name": "rc_min", "type": "row_count_min", "min_rows": 5, "severity": "error"}]
        results = engine.run_checks(df, rules)
        assert results[0].passed is False

    def test_row_count_max_pass(self, engine):
        df = pd.DataFrame({"a": range(3)})
        rules = [{"name": "rc_max", "type": "row_count_max", "max_rows": 10, "severity": "error"}]
        results = engine.run_checks(df, rules)
        assert results[0].passed is True

    def test_row_count_max_fail(self, engine):
        df = pd.DataFrame({"a": range(15)})
        rules = [{"name": "rc_max", "type": "row_count_max", "max_rows": 10, "severity": "error"}]
        results = engine.run_checks(df, rules)
        assert results[0].passed is False

    def test_regex_pass(self, engine):
        df = pd.DataFrame({"email": ["a@b.com", "c@d.com"]})
        rules = [{"name": "email_re", "type": "regex", "field": "email", "pattern": r".+@.+\..+", "severity": "error"}]
        results = engine.run_checks(df, rules)
        assert results[0].passed is True

    def test_regex_fail(self, engine):
        df = pd.DataFrame({"email": ["a@b.com", "invalid"]})
        rules = [{"name": "email_re", "type": "regex", "field": "email", "pattern": r".+@.+\..+", "severity": "error"}]
        results = engine.run_checks(df, rules)
        assert results[0].passed is False

    def test_null_rate_pass(self, engine):
        df = pd.DataFrame({"x": [1, 2, None]})
        rules = [{"name": "x_nr", "type": "null_rate", "field": "x", "threshold": 0.5, "severity": "warning"}]
        results = engine.run_checks(df, rules)
        assert results[0].passed is True

    def test_null_rate_fail(self, engine):
        df = pd.DataFrame({"x": [1, None, None, None]})
        rules = [{"name": "x_nr", "type": "null_rate", "field": "x", "threshold": 0.1, "severity": "warning"}]
        results = engine.run_checks(df, rules)
        assert results[0].passed is False

    def test_duplicate_rate_pass(self, engine):
        df = pd.DataFrame({"x": [1, 2, 3, 4, 5]})
        rules = [{"name": "x_dr", "type": "duplicate_rate", "field": "x", "threshold": 0.5, "severity": "warning"}]
        results = engine.run_checks(df, rules)
        assert results[0].passed is True

    def test_duplicate_rate_fail(self, engine):
        df = pd.DataFrame({"x": [1, 1, 1, 1, 2]})
        rules = [{"name": "x_dr", "type": "duplicate_rate", "field": "x", "threshold": 0.1, "severity": "warning"}]
        results = engine.run_checks(df, rules)
        assert results[0].passed is False

    def test_missing_field_returns_error(self, engine):
        df = pd.DataFrame({"other": [1]})
        rules = [{"name": "x_nn", "type": "not_null", "field": "nonexistent", "severity": "critical"}]
        results = engine.run_checks(df, rules)
        assert results[0].passed is False

    def test_type_check_string_pass(self, engine):
        df = pd.DataFrame({"name": ["alice", "bob", "charlie"]})
        rules = [
            {"name": "name_tc", "type": "type_check", "field": "name", "expected_type": "string", "severity": "error"}
        ]
        results = engine.run_checks(df, rules)
        assert results[0].passed is True

    def test_type_check_integer_pass(self, engine):
        df = pd.DataFrame({"user_id": [1, 2, 3]})
        rules = [
            {
                "name": "uid_tc",
                "type": "type_check",
                "field": "user_id",
                "expected_type": "integer",
                "severity": "error",
            }
        ]
        results = engine.run_checks(df, rules)
        assert results[0].passed is True

    def test_type_check_integer_fail(self, engine):
        df = pd.DataFrame({"user_id": [1, "not_a_number", 3]})
        rules = [
            {
                "name": "uid_tc",
                "type": "type_check",
                "field": "user_id",
                "expected_type": "integer",
                "severity": "error",
            }
        ]
        results = engine.run_checks(df, rules)
        assert results[0].passed is False

    def test_freshness_pass(self, engine):
        df = pd.DataFrame({"event_time": ["2026-06-23T10:00:00Z", "2026-06-23T10:05:00Z"]})
        rules = [
            {
                "name": "time_fr",
                "type": "freshness",
                "field": "event_time",
                "max_delay_minutes": 1440,
                "severity": "warning",
            }
        ]
        results = engine.run_checks(df, rules)
        # Within 24 hours, should pass
        assert results[0].passed is True

    def test_freshness_fail(self, engine):
        df = pd.DataFrame({"event_time": ["2020-01-01T00:00:00Z"]})
        rules = [
            {
                "name": "time_fr",
                "type": "freshness",
                "field": "event_time",
                "max_delay_minutes": 60,
                "severity": "warning",
            }
        ]
        results = engine.run_checks(df, rules)
        # Data from 2020 is definitely more than 60 minutes old
        assert results[0].passed is False

    def test_schema_match_pass(self, engine):
        df = pd.DataFrame({"id": [1, 2], "name": ["a", "b"]})
        rules = [{"name": "sm", "type": "schema_match", "fields": ["id", "name"], "severity": "warning"}]
        results = engine.run_checks(df, rules)
        assert results[0].passed is True

    def test_schema_match_fail(self, engine):
        df = pd.DataFrame({"id": [1, 2]})
        rules = [{"name": "sm", "type": "schema_match", "fields": ["id", "name", "email"], "severity": "warning"}]
        results = engine.run_checks(df, rules)
        assert results[0].passed is False

    def test_multiple_rules_in_one_call(self, engine):
        df = pd.DataFrame({"user_id": [1, 2, 3], "status": ["active", "inactive", "active"]})
        rules = [
            {"name": "uid_nn", "type": "not_null", "field": "user_id", "severity": "critical"},
            {"name": "uid_uniq", "type": "unique", "field": "user_id", "severity": "error"},
            {
                "name": "status_av",
                "type": "allowed_values",
                "field": "status",
                "values": ["active", "inactive"],
                "severity": "error",
            },
        ]
        results = engine.run_checks(df, rules)
        assert len(results) == 3
        assert all(r.passed for r in results)

    def test_unknown_check_type_skipped(self, engine):
        df = pd.DataFrame({"x": [1]})
        rules = [{"name": "unknown", "type": "nonexistent_check_type", "field": "x", "severity": "error"}]
        results = engine.run_checks(df, rules)
        # Unknown check types are silently skipped
        assert len(results) == 0

    def test_check_result_to_dict_includes_timestamp(self, engine):
        df = pd.DataFrame({"user_id": [1, None, 3]})
        rules = [{"name": "uid_nn", "type": "not_null", "field": "user_id", "severity": "critical"}]
        results = engine.run_checks(df, rules)
        d = results[0].to_dict()
        assert "timestamp" in d
        assert d["name"] == "uid_nn"
        assert d["passed"] is False
        assert d["failed_rows_count"] == 1
