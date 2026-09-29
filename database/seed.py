from werkzeug.security import generate_password_hash

from app import app
from models import (
    db,
    User,
    Provider,
    Service,
    ProviderService
)


DEMO_PROVIDERS = [
    {
        "name": "Ravi Auto Care",
        "email": "ravi@roadresq.com",
        "password": "Ravi123",
        "phone": "9000000001",
        "services": [
            "Mechanic",
            "Tyre Assistance",
            "Towing"
        ],
        "latitude": 16.5449,
        "longitude": 81.5212
    },
    {
        "name": "Kumar Motors",
        "email": "kumar@roadresq.com",
        "password": "Kumar123",
        "phone": "9000000002",
        "services": [
            "Mechanic",
            "Fuel Delivery",
            "Towing"
        ],
        "latitude": 16.5500,
        "longitude": 81.5250
    },
    {
        "name": "FastFix Vehicle Services",
        "email": "fastfix@roadresq.com",
        "password": "FastFix123",
        "phone": "9000000003",
        "services": [
            "Mechanic",
            "Tyre Assistance",
            "Fuel Delivery"
        ],
        "latitude": 16.5380,
        "longitude": 81.5150
    },
    {
        "name": "FreshBite Delivery",
        "email": "freshbite@roadresq.com",
        "password": "Fresh123",
        "phone": "9000000004",
        "services": [
            "Food Delivery",
            "Emergency Food"
        ],
        "latitude": 16.5480,
        "longitude": 81.5190
    },
    {
        "name": "QuickFood Services",
        "email": "quickfood@roadresq.com",
        "password": "Quick123",
        "phone": "9000000005",
        "services": [
            "Food Delivery",
            "Emergency Food"
        ],
        "latitude": 16.5420,
        "longitude": 81.5280
    },
    {
        "name": "Sri Sai Pharmacy",
        "email": "srisai@roadresq.com",
        "password": "Sai123",
        "phone": "9000000006",
        "services": [
            "Pharmacy",
            "Medicine Delivery"
        ],
        "latitude": 16.5520,
        "longitude": 81.5180
    },
    {
        "name": "MedCare Services",
        "email": "medcare@roadresq.com",
        "password": "Med123",
        "phone": "9000000007",
        "services": [
            "Pharmacy",
            "Medicine Delivery"
        ],
        "latitude": 16.5350,
        "longitude": 81.5220
    },
    {
        "name": "HomeFix Experts",
        "email": "homefix@roadresq.com",
        "password": "Home123",
        "phone": "9000000008",
        "services": [
            "Electrician",
            "Plumber",
            "General Repair"
        ],
        "latitude": 16.5460,
        "longitude": 81.5300
    },
    {
        "name": "QuickMove Delivery",
        "email": "quickmove@roadresq.com",
        "password": "Move123",
        "phone": "9000000009",
        "services": [
            "Urgent Pickup",
            "Small Package Delivery"
        ],
        "latitude": 16.5400,
        "longitude": 81.5160
    },
    {
        "name": "Local Help Services",
        "email": "localhelp@roadresq.com",
        "password": "Local123",
        "phone": "9000000010",
        "services": [
            "General Local Assistance",
            "Urgent Pickup",
            "Small Package Delivery"
        ],
        "latitude": 16.5500,
        "longitude": 81.5150
    }
]


with app.app_context():

    for data in DEMO_PROVIDERS:

        # Find existing user
        user = User.query.filter_by(
            email=data["email"]
        ).first()

        # Create user if it doesn't exist
        if not user:

            user = User(
                name=data["name"],
                email=data["email"],
                password=generate_password_hash(
                    data["password"]
                ),
                role="provider"
            )

            db.session.add(user)
            db.session.flush()

        else:

            # Make sure this is a provider account
            user.name = data["name"]
            user.role = "provider"

            # Reset to known demo password
            user.password = generate_password_hash(
                data["password"]
            )

        # Find/create provider profile
        provider = Provider.query.filter_by(
            user_id=user.id
        ).first()

        if not provider:

            provider = Provider(
                user_id=user.id,
                phone=data["phone"],
                latitude=data["latitude"],
                longitude=data["longitude"],
                is_available=True,
                rating=4.5
            )

            db.session.add(provider)
            db.session.flush()

        else:

            provider.phone = data["phone"]
            provider.latitude = data["latitude"]
            provider.longitude = data["longitude"]
            provider.is_available = True
            provider.rating = 4.5

        # Get service IDs
        for service_name in data["services"]:

            service = Service.query.filter_by(
                name=service_name
            ).first()

            if not service:
                print(
                    f"Service not found: {service_name}"
                )
                continue

            existing_link = ProviderService.query.filter_by(
                provider_id=provider.id,
                service_id=service.id
            ).first()

            if not existing_link:

                db.session.add(
                    ProviderService(
                        provider_id=provider.id,
                        service_id=service.id
                    )
                )

    db.session.commit()

    print("\n========================================")
    print("DEMO PROVIDER ACCOUNTS READY")
    print("========================================\n")

    for data in DEMO_PROVIDERS:
        print(
            f"{data['name']} | "
            f"{data['email']} | "
            f"{data['password']}"
        )

    print("\nAll demo providers are AVAILABLE.")