from .user import db


class ProviderService(db.Model):
    __tablename__ = "provider_services"

    id = db.Column(db.Integer, primary_key=True)

    provider_id = db.Column(
        db.Integer,
        db.ForeignKey("providers.id"),
        nullable=False
    )

    service_id = db.Column(
        db.Integer,
        db.ForeignKey("services.id"),
        nullable=False
    )

    provider = db.relationship(
        "Provider",
        backref="services"
    )

    service = db.relationship(
        "Service",
        backref="providers"
    )