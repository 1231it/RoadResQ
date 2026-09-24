from .user import db


class Provider(db.Model):
    __tablename__ = "providers"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        unique=True
    )

    phone = db.Column(db.String(15), nullable=False)

    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)

    is_available = db.Column(db.Boolean, default=False)

    rating = db.Column(db.Float, default=0.0)

    user = db.relationship("User", backref="provider", uselist=False)

    def __repr__(self):
        return f"<Provider {self.id}>"