from .user import db
from datetime import datetime


class Rating(db.Model):
    __tablename__ = "ratings"

    id = db.Column(db.Integer, primary_key=True)

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    provider_id = db.Column(
        db.Integer,
        db.ForeignKey("providers.id"),
        nullable=False
    )

    request_id = db.Column(
        db.Integer,
        db.ForeignKey("assistance_requests.id"),
        nullable=False
    )

    rating = db.Column(
        db.Integer,
        nullable=False
    )

    review = db.Column(
        db.String(500),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    customer = db.relationship("User", backref="ratings")

    provider = db.relationship("Provider", backref="ratings")

    request = db.relationship(
        "AssistanceRequest",
        backref="rating"
    )