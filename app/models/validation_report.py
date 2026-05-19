from datetime import datetime
from app import db
from app.models.task_status import TaskStatus


class ValidationReport(db.Model):
    __tablename__ = "validation_reports"

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.String(64), nullable=False, unique=True)
    
    # List of preprocessing report IDs, one per dataset submitted for this validation
    preprocessing_report_ids = db.Column(db.JSON, nullable=False)
    
    status = db.Column(db.Enum(TaskStatus, native_enum=False), nullable=False, default=TaskStatus.QUEUED)
    rules_applied = db.Column(db.JSON)       # The rules list sent by the client
    report_result = db.Column(db.JSON)       # The full report dict from run_rules()
    passed = db.Column(db.Boolean)           # Top-level pass/fail flag
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now())
    completed_at = db.Column(db.DateTime)

    def __repr__(self):
        return f"<ValidationReport job={self.job_id} passed={self.passed}>"
    
    def get_result(self):
        return self.report_result