from datetime import datetime
from .user import db


class AssistanceRequest(db.Model):
    __tablename__ = "assistance_requests"

    id = db.Column(db.Integer, primary_key=True)

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    provider_id = db.Column(
        db.Integer,
        db.ForeignKey("providers.id"),
        nullable=True
    )

    service_id = db.Column(
        db.Integer,
        db.ForeignKey("services.id"),
        nullable=False
    )

    description = db.Column(
        db.String(500),
        nullable=False
    )

    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)

    status = db.Column(
        db.String(30),
        nullable=False,
        default="PENDING"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    customer = db.relationship(
        "User",
        foreign_keys=[customer_id],
        backref="requests"
    )

    provider = db.relationship(
        "Provider",
        foreign_keys=[provider_id],
        backref="requests"
    )

    service = db.relationship(
        "Service",
        backref="requests"
    )

    def __repr__(self):
        return f"<AssistanceRequest {self.id}>"