class CompatibilityChecker:
    BREAKING_TYPE_MAP = {
        "field_removed": "critical",
        "type_changed": "critical",
        "nullable_changed_true_to_false": "error",
        "enum_value_removed": "error",
        "field_renamed_without_alias": "critical",
    }

    NON_BREAKING_TYPES = {
        "field_added_optional",
        "field_added_nullable",
        "enum_value_added",
        "description_added",
    }

    def check(self, old_schema: dict, new_schema: dict) -> dict:
        old_fields = {f["name"]: f for f in old_schema.get("fields", [])}
        new_fields = {f["name"]: f for f in new_schema.get("fields", [])}

        breaking_changes = []
        warnings = []

        for field_name, old_field in old_fields.items():
            if field_name not in new_fields:
                breaking_changes.append(
                    {
                        "field": field_name,
                        "change": "field_removed",
                        "severity": "critical",
                        "message": f"Required field '{field_name}' was removed",
                    }
                )
                continue

            new_field = new_fields[field_name]

            if old_field.get("type") != new_field.get("type"):
                breaking_changes.append(
                    {
                        "field": field_name,
                        "change": "type_changed",
                        "severity": "critical",
                        "message": (
                            f"Field '{field_name}' type changed from "
                            f"'{old_field.get('type')}' to '{new_field.get('type')}'"
                        ),
                    }
                )

            if old_field.get("nullable") is False and new_field.get("nullable") is True:
                warnings.append(
                    {
                        "field": field_name,
                        "change": "nullable_changed_false_to_true",
                        "severity": "info",
                        "message": f"Field '{field_name}' became nullable",
                    }
                )

            if old_field.get("nullable") is True and new_field.get("nullable") is False:
                breaking_changes.append(
                    {
                        "field": field_name,
                        "change": "nullable_changed_true_to_false",
                        "severity": "error",
                        "message": f"Field '{field_name}' changed from nullable to non-nullable",
                    }
                )

            old_values = set(old_field.get("values") or [])
            new_values = set(new_field.get("values") or [])
            if old_values and new_values:
                removed = old_values - new_values
                added = new_values - old_values
                if removed:
                    breaking_changes.append(
                        {
                            "field": field_name,
                            "change": "enum_value_removed",
                            "severity": "error",
                            "message": f"Enum values removed from '{field_name}': {sorted(removed)}",
                        }
                    )
                if added:
                    warnings.append(
                        {
                            "field": field_name,
                            "change": "enum_value_added",
                            "severity": "info",
                            "message": f"Enum values added to '{field_name}': {sorted(added)}",
                        }
                    )

        for field_name in new_fields:
            if field_name not in old_fields:
                f = new_fields[field_name]
                change_type = "field_added_nullable" if f.get("nullable") else "field_added_optional"
                severity = "info"
                warnings.append(
                    {
                        "field": field_name,
                        "change": change_type,
                        "severity": severity,
                        "message": f"New field '{field_name}' added",
                    }
                )

        return {
            "compatible": len(breaking_changes) == 0,
            "breaking_changes": breaking_changes,
            "warnings": warnings,
        }
