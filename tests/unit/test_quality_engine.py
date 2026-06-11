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
        rules = [{"name": "status_av", "type": "allowed_values", "field": "status", "values": ["active", "inactive"], "severity": "error"}]
        results = engine.run_checks(df, rules)
        assert results[0].passed is True

    def test_allowed_values_fail(self, engine):
        df = pd.DataFrame({"status": ["active", "unknown", "active"]})
        rules = [{"name": "status_av", "type": "allowed_values", "field": "status", "values": ["active", "inactive"], "severity": "error"}]
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
