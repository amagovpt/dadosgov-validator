from datetime import datetime, timezone
from app import db
from app.models.task_status import TaskStatus


class PreprocessingReport(db.Model):
    __tablename__ = "preprocessing_reports"

    id = db.Column(db.Integer, primary_key=True)
    dadosgov_dataset_id = db.Column(db.String(64), nullable=True, index=True)
    dataframe_id = db.Column(db.String(64), nullable=False, index=True)
    job_id = db.Column(db.String(64), nullable=False, unique=True)
    status = db.Column(db.Enum(TaskStatus, native_enum=False), nullable=False, default=TaskStatus.QUEUED)
    original_filename = db.Column(db.String(255))
    column_names = db.Column(db.JSON)
    presumed_column_types = db.Column(db.JSON)
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = db.Column(db.DateTime)

    def __repr__(self):
        return f"<PreprocessingReport dataframe_id={self.dataframe_id} status={self.status}>"
    
    def get_result(self):
        assert self.status == TaskStatus.SUCCESS

        report = dict()

        report["column_names"] = self.column_names
        report["presumed_column_types"] = self.presumed_column_types

        return report

        