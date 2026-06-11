from sqlalchemy.orm import Session

from app.db.repositories import ViolationRepository


class ViolationService:
    def __init__(self, db: Session):
        self.db = db
        self.violation_repo = ViolationRepository(db)

    def list_violations(self):
        return self.violation_repo.list_all()

    def get_violation(self, violation_id):
        return self.violation_repo.get_by_id(violation_id)

    def update_status(self, violation_id, status: str):
        valid_statuses = {"open", "acknowledged", "resolved", "ignored"}
        if status not in valid_statuses:
            raise ValueError(f"Invalid status: {status}. Must be one of {valid_statuses}")
        self.violation_repo.update_status(violation_id, status)
        return self.violation_repo.get_by_id(violation_id)
