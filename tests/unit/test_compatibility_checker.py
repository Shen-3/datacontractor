import pytest

from app.services.compatibility_checker import CompatibilityChecker


@pytest.fixture
def checker():
    return CompatibilityChecker()


class TestCompatibilityChecker:
    def test_compatible_add_optional_field(self, checker):
        old = {"fields": [{"name": "id", "type": "integer", "required": True, "nullable": False}]}
        new = {
            "fields": [
                {"name": "id", "type": "integer", "required": True, "nullable": False},
                {"name": "name", "type": "string", "required": False, "nullable": True},
            ]
        }
        result = checker.check(old, new)
        assert result["compatible"] is True
        assert len(result["breaking_changes"]) == 0

    def test_breaking_remove_required_field(self, checker):
        old = {
            "fields": [
                {"name": "id", "type": "integer", "required": True, "nullable": False},
                {"name": "name", "type": "string", "required": True, "nullable": False},
            ]
        }
        new = {"fields": [{"name": "id", "type": "integer", "required": True, "nullable": False}]}
        result = checker.check(old, new)
        assert result["compatible"] is False
        assert any(bc["change"] == "field_removed" for bc in result["breaking_changes"])

    def test_breaking_type_change(self, checker):
        old = {"fields": [{"name": "amount", "type": "string", "required": True}]}
        new = {"fields": [{"name": "amount", "type": "integer", "required": True}]}
        result = checker.check(old, new)
        assert result["compatible"] is False
        assert any(bc["change"] == "type_changed" for bc in result["breaking_changes"])

    def test_breaking_nullable_true_to_false(self, checker):
        old = {"fields": [{"name": "email", "type": "string", "required": True, "nullable": True}]}
        new = {"fields": [{"name": "email", "type": "string", "required": True, "nullable": False}]}
        result = checker.check(old, new)
        assert result["compatible"] is False
        assert any(bc["change"] == "nullable_changed_true_to_false" for bc in result["breaking_changes"])

    def test_warning_nullable_false_to_true(self, checker):
        old = {"fields": [{"name": "email", "type": "string", "required": True, "nullable": False}]}
        new = {"fields": [{"name": "email", "type": "string", "required": True, "nullable": True}]}
        result = checker.check(old, new)
        assert result["compatible"] is True
        assert len(result["breaking_changes"]) == 0
        assert len(result["warnings"]) > 0

    def test_breaking_enum_value_removed(self, checker):
        old = {"fields": [{"name": "status", "type": "enum", "values": ["active", "inactive", "pending"]}]}
        new = {"fields": [{"name": "status", "type": "enum", "values": ["active", "inactive"]}]}
        result = checker.check(old, new)
        assert result["compatible"] is False
        assert any(bc["change"] == "enum_value_removed" for bc in result["breaking_changes"])

    def test_warning_enum_value_added(self, checker):
        old = {"fields": [{"name": "status", "type": "enum", "values": ["active", "inactive"]}]}
        new = {"fields": [{"name": "status", "type": "enum", "values": ["active", "inactive", "pending"]}]}
        result = checker.check(old, new)
        assert result["compatible"] is True
        assert len(result["warnings"]) > 0

    def test_identical_schemas(self, checker):
        schema = {"fields": [{"name": "id", "type": "integer", "required": True}]}
        result = checker.check(schema, schema)
        assert result["compatible"] is True
        assert len(result["breaking_changes"]) == 0

    def test_new_field_added(self, checker):
        old = {"fields": [{"name": "id", "type": "integer"}]}
        new = {"fields": [{"name": "id", "type": "integer"}, {"name": "email", "type": "string"}]}
        result = checker.check(old, new)
        assert result["compatible"] is True
        assert len(result["warnings"]) > 0
