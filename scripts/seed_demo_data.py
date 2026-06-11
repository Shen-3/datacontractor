import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.db.models import Base
from app.db.repositories import ContractRepository, ContractVersionRepository


def seed_demo_data():
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)

    Base.metadata.create_all(engine)

    db = SessionLocal()
    try:
        contract_repo = ContractRepository(db)
        version_repo = ContractVersionRepository(db)

        contract_files = [
            ("data/contracts/users_events_v1.yaml", "1.0.0"),
        ]

        for filepath, expected_version in contract_files:
            with open(filepath) as f:
                data = yaml.safe_load(f)

            name = data["name"]
            existing = contract_repo.get_by_name(name)
            if existing:
                print(f"Contract '{name}' already exists, skipping")
                continue

            contract = contract_repo.create(
                name=name,
                description=data.get("description", ""),
                owner=data.get("owner", "unknown"),
            )

            schema_data = data.get("schema", {})
            quality_rules = data.get("quality_rules", [])
            sla_data = data.get("sla")
            compat_data = data.get("compatibility", {"mode": "backward"})

            version_repo.create(
                contract_id=contract.id,
                version=data.get("version", "1.0.0"),
                schema_json=schema_data,
                quality_rules_json=quality_rules,
                sla_json=sla_data,
                compatibility_mode=compat_data.get("mode", "backward"),
            )

            print(f"Created contract '{name}' version {data.get('version', '1.0.0')}")

        print("Seed completed successfully")
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_data()
