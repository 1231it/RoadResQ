from .user import db


class Service(db.Model):
    __tablename__ = "services"

    id = db.Column(db.Integer, primary_key=True)

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id"),
        nullable=False
    )

    name = db.Column(db.String(100), nullable=False)

    description = db.Column(db.String(255), nullable=True)

    is_active = db.Column(db.Boolean, default=True)

    category = db.relationship(
        "Category",
        backref="services"
    )

    def __repr__(self):
        return f"<Service {self.name}>"