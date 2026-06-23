"""Unit tests for ViolationService."""

from unittest.mock import MagicMock

import pytest

from app.services.violation_service import ViolationService


class TestViolationService:
    def test_list_violations(self):
        db = MagicMock()
        service = ViolationService(db)
        service.violation_repo = MagicMock()
        service.violation_repo.list_all.return_value = ["v1", "v2"]

        result = service.list_violations()
        assert result == ["v1", "v2"]

    def test_get_violation(self):
        db = MagicMock()
        service = ViolationService(db)
        service.violation_repo = MagicMock()
        service.violation_repo.get_by_id.return_value = MagicMock(id="violation-uuid")

        result = service.get_violation("violation-uuid")
        assert result is not None
        assert str(result.id) == "violation-uuid"

    def test_get_violation_not_found(self):
        db = MagicMock()
        service = ViolationService(db)
        service.violation_repo = MagicMock()
        service.violation_repo.get_by_id.return_value = None

        result = service.get_violation("nonexistent")
        assert result is None

    def test_update_status(self):
        db = MagicMock()
        service = ViolationService(db)
        service.violation_repo = MagicMock()
        service.violation_repo.get_by_id.return_value = MagicMock(id="v-uuid", status="resolved")

        result = service.update_status("v-uuid", "resolved")
        assert result.status == "resolved"

    def test_update_status_invalid(self):
        db = MagicMock()
        service = ViolationService(db)
        service.violation_repo = MagicMock()

        with pytest.raises(ValueError, match="Invalid status"):
            service.update_status("v-uuid", "invalid_status")
