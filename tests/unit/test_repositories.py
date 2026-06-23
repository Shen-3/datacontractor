"""Unit tests for all repository classes.

Uses an in-memory SQLite database via the conftest ``test_db_session``
fixture for real database interactions.
"""

from sqlalchemy.orm import Session

from app.db.repositories import (
    ContractRepository,
    ContractVersionRepository,
    ValidationRunRepository,
    ViolationRepository,
)


class TestContractRepository:
    def test_create_and_get_by_name(self, test_db_session: Session):
        repo = ContractRepository(test_db_session)
        c = repo.create(name="test_contract", description="desc", owner="team-a")
        assert c.name == "test_contract"

        fetched = repo.get_by_name("test_contract")
        assert fetched is not None
        assert fetched.id == c.id

    def test_get_by_name_not_found(self, test_db_session: Session):
        repo = ContractRepository(test_db_session)
        assert repo.get_by_name("nonexistent") is None

    def test_list_all(self, test_db_session: Session):
        repo = ContractRepository(test_db_session)
        repo.create(name="c1", description="d1", owner="o1")
        repo.create(name="c2", description="d2", owner="o2")
        contracts = repo.list_all()
        assert len(contracts) >= 2
        names = [c.name for c in contracts]
        assert "c1" in names
        assert "c2" in names


class TestContractVersionRepository:
    def test_create_and_get_active(self, test_db_session: Session):
        contract_repo = ContractRepository(test_db_session)
        c = contract_repo.create(name="ver_test", description="", owner="team")

        version_repo = ContractVersionRepository(test_db_session)
        cv = version_repo.create(
            contract_id=c.id,
            version="1.0.0",
            schema_json={"fields": []},
            quality_rules_json=[],
            sla_json=None,
        )
        assert cv.version == "1.0.0"

        active = version_repo.get_active_version(c.id)
        assert active is not None
        assert active.id == cv.id

    def test_list_by_contract(self, test_db_session: Session):
        contract_repo = ContractRepository(test_db_session)
        c = contract_repo.create(name="list_ver", description="", owner="team")

        version_repo = ContractVersionRepository(test_db_session)
        version_repo.create(contract_id=c.id, version="1.0.0", schema_json={}, quality_rules_json=[], sla_json=None)
        version_repo.create(contract_id=c.id, version="2.0.0", schema_json={}, quality_rules_json=[], sla_json=None)

        versions = version_repo.list_by_contract(c.id)
        assert len(versions) == 2

    def test_get_by_version(self, test_db_session: Session):
        contract_repo = ContractRepository(test_db_session)
        c = contract_repo.create(name="get_by_ver", description="", owner="team")

        version_repo = ContractVersionRepository(test_db_session)
        version_repo.create(contract_id=c.id, version="1.0.0", schema_json={}, quality_rules_json=[], sla_json=None)

        fetched = version_repo.get_by_version(c.id, "1.0.0")
        assert fetched is not None
        assert fetched.version == "1.0.0"


class TestValidationRunRepository:
    def test_create_and_get(self, test_db_session: Session):
        contract_repo = ContractRepository(test_db_session)
        c = contract_repo.create(name="run_test", description="", owner="team")

        version_repo = ContractVersionRepository(test_db_session)
        cv = version_repo.create(
            contract_id=c.id, version="1.0.0", schema_json={}, quality_rules_json=[], sla_json=None
        )

        run_repo = ValidationRunRepository(test_db_session)
        run = run_repo.create(
            contract_id=c.id,
            contract_version_id=cv.id,
            dataset_name="test.csv",
            status="running",
        )
        assert run.status == "running"

        fetched = run_repo.get_by_id(run.id)
        assert fetched is not None
        assert str(fetched.id) == str(run.id)

    def test_update_result_sets_finished_at(self, test_db_session: Session):
        contract_repo = ContractRepository(test_db_session)
        c = contract_repo.create(name="finish_test", description="", owner="team")

        version_repo = ContractVersionRepository(test_db_session)
        cv = version_repo.create(
            contract_id=c.id, version="1.0.0", schema_json={}, quality_rules_json=[], sla_json=None
        )

        run_repo = ValidationRunRepository(test_db_session)
        run = run_repo.create(contract_id=c.id, contract_version_id=cv.id, dataset_name="t.csv", status="running")

        run_repo.update_result(run.id, status="passed", rows_checked=100, violations_count=0)

        fetched = run_repo.get_by_id(run.id)
        assert fetched.status == "passed"
        assert fetched.rows_checked == 100
        assert fetched.finished_at is not None

    def test_list_all(self, test_db_session: Session):
        contract_repo = ContractRepository(test_db_session)
        c = contract_repo.create(name="list_runs", description="", owner="team")
        version_repo = ContractVersionRepository(test_db_session)
        cv = version_repo.create(
            contract_id=c.id, version="1.0.0", schema_json={}, quality_rules_json=[], sla_json=None
        )

        run_repo = ValidationRunRepository(test_db_session)
        run_repo.create(contract_id=c.id, contract_version_id=cv.id, dataset_name="a.csv", status="running")
        run_repo.create(contract_id=c.id, contract_version_id=cv.id, dataset_name="b.csv", status="passed")

        runs = run_repo.list_all()
        assert len(runs) >= 2


class TestViolationRepository:
    def test_create_and_get(self, test_db_session: Session):
        contract_repo = ContractRepository(test_db_session)
        c = contract_repo.create(name="viol_test", description="", owner="team")
        version_repo = ContractVersionRepository(test_db_session)
        cv = version_repo.create(
            contract_id=c.id, version="1.0.0", schema_json={}, quality_rules_json=[], sla_json=None
        )
        run_repo = ValidationRunRepository(test_db_session)
        run = run_repo.create(contract_id=c.id, contract_version_id=cv.id, dataset_name="t.csv", status="running")

        viol_repo = ViolationRepository(test_db_session)
        v = viol_repo.create(
            validation_run_id=run.id,
            contract_name="viol_test",
            contract_version="1.0.0",
            check_name="not_null",
            check_type="not_null",
            field_name="user_id",
            severity="critical",
            failed_rows_count=5,
            sample_records_json=None,
            message="5 null values",
        )
        assert v.check_name == "not_null"
        assert v.severity == "critical"

        fetched = viol_repo.get_by_id(v.id)
        assert fetched is not None

    def test_update_status(self, test_db_session: Session):
        contract_repo = ContractRepository(test_db_session)
        c = contract_repo.create(name="viol_status", description="", owner="team")
        version_repo = ContractVersionRepository(test_db_session)
        cv = version_repo.create(
            contract_id=c.id, version="1.0.0", schema_json={}, quality_rules_json=[], sla_json=None
        )
        run_repo = ValidationRunRepository(test_db_session)
        run = run_repo.create(contract_id=c.id, contract_version_id=cv.id, dataset_name="t.csv", status="running")
        viol_repo = ViolationRepository(test_db_session)

        v = viol_repo.create(
            validation_run_id=run.id,
            contract_name="vc",
            contract_version="1.0.0",
            check_name="nn",
            check_type="not_null",
            field_name="x",
            severity="error",
            failed_rows_count=1,
            sample_records_json=None,
            message="err",
        )
        viol_repo.update_status(v.id, "resolved")

        fetched = viol_repo.get_by_id(v.id)
        assert fetched.status == "resolved"

    def test_bulk_create(self, test_db_session: Session):
        contract_repo = ContractRepository(test_db_session)
        c = contract_repo.create(name="bulk_test", description="", owner="team")
        version_repo = ContractVersionRepository(test_db_session)
        cv = version_repo.create(
            contract_id=c.id, version="1.0.0", schema_json={}, quality_rules_json=[], sla_json=None
        )
        run_repo = ValidationRunRepository(test_db_session)
        run = run_repo.create(contract_id=c.id, contract_version_id=cv.id, dataset_name="t.csv", status="running")

        viol_repo = ViolationRepository(test_db_session)
        records = [
            dict(
                validation_run_id=run.id,
                contract_name="bulk_test",
                contract_version="1.0.0",
                check_name=f"check_{i}",
                check_type="not_null",
                field_name="x",
                severity="error",
                failed_rows_count=1,
                sample_records_json=None,
                message=f"err_{i}",
            )
            for i in range(10)
        ]
        violations = viol_repo.bulk_create(records)
        assert len(violations) == 10
        assert all(v.check_name.startswith("check_") for v in violations)
