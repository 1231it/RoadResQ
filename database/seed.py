import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app
from models import db, Category, Service


data = {
    "Vehicle Assistance": [
        "Mechanic",
        "Tyre Assistance",
        "Fuel Delivery",
        "Towing"
    ],
    "Food Assistance": [
        "Food Delivery",
        "Emergency Food"
    ],
    "Medical Assistance": [
        "Pharmacy",
        "Medicine Delivery"
    ],
    "Home Services": [
        "Electrician",
        "Plumber",
        "General Repair"
    ],
    "Local Delivery": [
        "Urgent Pickup",
        "Small Package Delivery"
    ],
    "Other Help": [
        "General Local Assistance"
    ]
}


with app.app_context():

    for category_name, services in data.items():

        category = Category.query.filter_by(
            name=category_name
        ).first()

        if not category:
            category = Category(
                name=category_name,
                description=f"{category_name} services"
            )

            db.session.add(category)
            db.session.commit()

        for service_name in services:

            existing_service = Service.query.filter_by(
                name=service_name,
                category_id=category.id
            ).first()

            if not existing_service:
                service = Service(
                    name=service_name,
                    category_id=category.id
                )

                db.session.add(service)

    db.session.commit()

    print("Categories and services added successfully!")