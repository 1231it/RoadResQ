import sys
import os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from app import app
from models import Category, Service


with app.app_context():

    categories = Category.query.all()

    for category in categories:
        print(f"\n{category.name}")

        services = Service.query.filter_by(
            category_id=category.id
        ).all()

        for service in services:
            print(f"  - {service.name}")