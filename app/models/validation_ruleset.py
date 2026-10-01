from datetime import datetime, timezone
from app import db


class ValidationRuleset(db.Model):
    __tablename__ = "validation_rulesets"

    id = db.Column(db.Integer, primary_key=True)
    dadosgov_organization_id = db.Column(db.String(64), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    dadosgov_dataset_id = db.Column(db.String(64), nullable=True, index=True)
    dadosgov_resource_id_list = db.Column(db.JSON, nullable=False)
    rules = db.Column(db.JSON, nullable=False)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<ValidationRuleset organization_id={self.dadosgov_organization_id} title={self.title} description={self.description} dataset_id={self.dadosgov_dataset_id}>"
