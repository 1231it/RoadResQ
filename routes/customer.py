from math import radians, sin, cos, sqrt, atan2

from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user

from routes.role_required import role_required

from models import (
    db,
    Category,
    Service,
    Provider,
    ProviderService,
    AssistanceRequest,
    Rating
)


customer = Blueprint("customer", __name__)


# ============================================================
# DISTANCE CALCULATION
# ============================================================

def calculate_distance_km(lat1, lon1, lat2, lon2):
    earth_radius_km = 6371.0

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    a = (
        sin(delta_lat / 2) ** 2
        + cos(lat1)
        * cos(lat2)
        * sin(delta_lon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return earth_radius_km * c


# ============================================================
# SERVICE PRICING
# ============================================================

def get_service_pricing(service_name):

    pricing = {
        "Mechanic": (150, 20),
        "Tyre Assistance": (100, 15),
        "Fuel Delivery": (80, 10),
        "Towing": (500, 30),

        "Food Delivery": (50, 10),
        "Emergency Food": (80, 10),

        "Pharmacy": (40, 8),
        "Medicine Delivery": (40, 8),

        "Electrician": (150, 15),
        "Plumber": (150, 15),
        "General Repair": (150, 15),

        "Urgent Pickup": (100, 15),
        "Small Package Delivery": (80, 12),

        "General Local Assistance": (100, 15)
    }

    return pricing.get(service_name, (100, 15))


# ============================================================
# ETA CALCULATION
# ============================================================

def calculate_eta_minutes(distance_km):

    average_speed_kmh = 25

    eta_minutes = (
        distance_km / average_speed_kmh
    ) * 60

    return max(5, round(eta_minutes))


# ============================================================
# CUSTOMER DASHBOARD
# ============================================================

@customer.route("/dashboard", methods=["GET"])
@role_required("customer")
def dashboard():

    categories = Category.query.filter_by(
        is_active=True
    ).all()

    return render_template(
        "customer_dashboard.html",
        categories=categories
    )


# ============================================================
# REQUEST HELP PAGE
# ============================================================

@customer.route("/request-help", methods=["GET"])
@role_required("customer")
def request_help():

    categories = Category.query.filter_by(
        is_active=True
    ).all()

    selected_category_id = request.args.get(
        "category_id",
        type=int
    )

    return render_template(
        "request_help.html",
        categories=categories,
        selected_category_id=selected_category_id
    )


# ============================================================
# FIND NEARBY PROVIDERS
# ============================================================

@customer.route("/nearby-providers", methods=["GET"])
@role_required("customer")
def nearby_providers():

    service_id = request.args.get(
        "service_id",
        type=int
    )

    latitude = request.args.get(
        "latitude",
        type=float
    )

    longitude = request.args.get(
        "longitude",
        type=float
    )

    if not service_id:
        return jsonify({
            "message": "Service is required"
        }), 400

    if latitude is None or longitude is None:
        return jsonify({
            "message": "Customer location is required"
        }), 400

    service = Service.query.filter_by(
        id=service_id,
        is_active=True
    ).first()

    if not service:
        return jsonify({
            "message": "Invalid service"
        }), 404

    provider_service_rows = ProviderService.query.filter_by(
        service_id=service.id
    ).all()

    nearby = []

    base_price, price_per_km = get_service_pricing(
        service.name
    )

    for row in provider_service_rows:

        provider = db.session.get(
            Provider,
            row.provider_id
        )

        if not provider:
            continue

        if not provider.is_available:
            continue

        if (
            provider.latitude is None
            or provider.longitude is None
        ):
            continue

        distance = calculate_distance_km(
            latitude,
            longitude,
            provider.latitude,
            provider.longitude
        )

        # Only providers within 25 km
        if distance > 25:
            continue

        eta = calculate_eta_minutes(distance)

        estimated_price = (
            base_price
            + (distance * price_per_km)
        )

        price_min = round(
            estimated_price * 0.95
        )

        price_max = round(
            estimated_price * 1.05
        )

        provider_name = "Service Provider"

        if provider.user:
            provider_name = provider.user.name

        nearby.append({

            "id": provider.id,

            "provider_id": provider.id,

            "name": provider_name,

            "phone": provider.phone,

            "rating": round(
                provider.rating,
                1
            ),

            "distance_km": round(
                distance,
                2
            ),

            "eta_minutes": eta,

            "estimated_price": round(
                estimated_price
            ),

            "estimated_price_min": price_min,

            "estimated_price_max": price_max,

            "latitude": provider.latitude,

            "longitude": provider.longitude
        })

    nearby.sort(
        key=lambda provider:
        provider["distance_km"]
    )

    return jsonify({

        "service": {
            "id": service.id,
            "name": service.name
        },

        "providers": nearby

    }), 200


# ============================================================
# CREATE ASSISTANCE REQUEST
# ============================================================

@customer.route("/create-request", methods=["POST"])
@role_required("customer")
def create_request():

    data = request.get_json() or {}

    service_id = data.get(
        "service_id"
    )

    description = data.get(
        "description",
        ""
    ).strip()

    latitude = data.get(
        "latitude"
    )

    longitude = data.get(
        "longitude"
    )

    provider_id = data.get(
        "provider_id"
    )

    if not service_id or not description:

        return jsonify({
            "message":
                "Service and description are required"
        }), 400

    if latitude is None or longitude is None:

        return jsonify({
            "message":
                "Current location is required"
        }), 400

    try:

        latitude = float(latitude)

        longitude = float(longitude)

    except (TypeError, ValueError):

        return jsonify({
            "message":
                "Invalid location coordinates"
        }), 400

    # Validate service

    service = Service.query.filter_by(
        id=int(service_id),
        is_active=True
    ).first()

    if not service:

        return jsonify({
            "message":
                "Invalid service selected"
        }), 404

    selected_provider = None

    # ========================================================
    # VALIDATE SELECTED PROVIDER
    # ========================================================

    if provider_id:

        try:

            provider_id = int(
                provider_id
            )

        except (TypeError, ValueError):

            return jsonify({
                "message":
                    "Invalid provider"
            }), 400

        selected_provider = db.session.get(
            Provider,
            provider_id
        )

        if not selected_provider:

            return jsonify({
                "message":
                    "Selected provider not found"
            }), 404

        if not selected_provider.is_available:

            return jsonify({
                "message":
                    "Selected provider is no longer available"
            }), 409

        provider_service = ProviderService.query.filter_by(
            provider_id=selected_provider.id,
            service_id=service.id
        ).first()

        if not provider_service:

            return jsonify({
                "message":
                    "Provider does not offer this service"
            }), 400

    # ========================================================
    # CREATE REQUEST
    # ========================================================

    assistance_request = AssistanceRequest(

        customer_id=current_user.id,

        provider_id=(
            selected_provider.id
            if selected_provider
            else None
        ),

        service_id=service.id,

        description=description,

        latitude=latitude,

        longitude=longitude,

        status="PENDING"
    )

    try:

        db.session.add(
            assistance_request
        )

        db.session.commit()

    except Exception as error:

        db.session.rollback()

        print(
            "Create request error:",
            error
        )

        return jsonify({
            "message":
                "Failed to create assistance request. "
                "Please try again."
        }), 500

    return jsonify({

        "message":
            "Assistance request created successfully",

        "request_id":
            assistance_request.id,

        "status":
            assistance_request.status,

        "provider_id":
            (
                selected_provider.id
                if selected_provider
                else None
            )

    }), 201


# ============================================================
# REQUEST TRACKING
# ============================================================

@customer.route(
    "/request/<int:request_id>/tracking",
    methods=["GET"]
)
@role_required("customer")
def request_tracking(request_id):

    assistance_request = db.session.get(
        AssistanceRequest,
        request_id
    )

    if not assistance_request:

        return jsonify({
            "message":
                "Request not found"
        }), 404

    if assistance_request.customer_id != current_user.id:

        return jsonify({
            "message":
                "You do not have access to this request"
        }), 403

    service = db.session.get(
        Service,
        assistance_request.service_id
    )

    service_name = (
        service.name
        if service
        else "Unknown"
    )

    response = {

        "request_id":
            assistance_request.id,

        "status":
            assistance_request.status,

        "service": {

            "id":
                service.id
                if service
                else None,

            "name":
                service_name
        },

        "description":
            assistance_request.description,

        "latitude":
            assistance_request.latitude,

        "longitude":
            assistance_request.longitude,

        "customer_location": {

            "latitude":
                assistance_request.latitude,

            "longitude":
                assistance_request.longitude
        },

        "provider":
            None,

        "rating": {

            "submitted":
                False
        }
    }

    # No provider yet

    if not assistance_request.provider_id:

        return jsonify(
            response
        ), 200

    provider = db.session.get(
        Provider,
        assistance_request.provider_id
    )

    if not provider:

        return jsonify(
            response
        ), 200

    provider_name = "Service Provider"

    if provider.user:

        provider_name = provider.user.name

    provider_data = {

        "id":
            provider.id,

        "name":
            provider_name,

        "phone":
            provider.phone,

        "rating":
            round(
                provider.rating,
                1
            ),

        "latitude":
            provider.latitude,

        "longitude":
            provider.longitude
    }

    # Calculate distance and ETA

    if (
        provider.latitude is not None
        and provider.longitude is not None
    ):

        distance = calculate_distance_km(

            assistance_request.latitude,

            assistance_request.longitude,

            provider.latitude,

            provider.longitude
        )

        eta = calculate_eta_minutes(
            distance
        )

        base_price, price_per_km = (
            get_service_pricing(
                service_name
            )
        )

        estimated_price = (
            base_price
            + (distance * price_per_km)
        )

        provider_data["distance_km"] = round(
            distance,
            2
        )

        provider_data["eta_minutes"] = eta

        provider_data["estimated_price"] = round(
            estimated_price
        )

        provider_data["estimated_price_min"] = round(
            estimated_price * 0.95
        )

        provider_data["estimated_price_max"] = round(
            estimated_price * 1.05
        )

    response["provider"] = provider_data

    # ========================================================
    # CHECK RATING
    # ========================================================

    existing_rating = Rating.query.filter_by(

        request_id=assistance_request.id,

        customer_id=current_user.id

    ).first()

    if existing_rating:

        response["rating"] = {

            "submitted":
                True,

            "rating":
                existing_rating.rating,

            "review":
                existing_rating.review
        }

    else:

        response["rating"] = {

            "submitted":
                False
        }

    return jsonify(
        response
    ), 200


# ============================================================
# SUBMIT RATING
# ============================================================

@customer.route(
    "/request/<int:request_id>/rating",
    methods=["POST"]
)
@role_required("customer")
def submit_rating(request_id):

    assistance_request = db.session.get(
        AssistanceRequest,
        request_id
    )

    if not assistance_request:

        return jsonify({
            "message":
                "Request not found"
        }), 404

    if assistance_request.customer_id != current_user.id:

        return jsonify({
            "message":
                "You do not have access to this request"
        }), 403

    if assistance_request.status != "COMPLETED":

        return jsonify({
            "message":
                "You can rate the provider only after "
                "the request is completed"
        }), 400

    if not assistance_request.provider_id:

        return jsonify({
            "message":
                "No provider is assigned to this request"
        }), 400

    data = request.get_json() or {}

    rating_value = data.get(
        "rating"
    )

    review = data.get(
        "review",
        ""
    ).strip()

    if rating_value is None:

        return jsonify({
            "message":
                "Rating is required"
        }), 400

    try:

        rating_value = int(
            rating_value
        )

    except (TypeError, ValueError):

        return jsonify({
            "message":
                "Rating must be a number between 1 and 5"
        }), 400

    if rating_value < 1 or rating_value > 5:

        return jsonify({
            "message":
                "Rating must be between 1 and 5"
        }), 400

    existing_rating = Rating.query.filter_by(

        request_id=
            assistance_request.id

    ).first()

    if existing_rating:

        return jsonify({
            "message":
                "You have already rated this request"
        }), 409

    provider = db.session.get(
        Provider,
        assistance_request.provider_id
    )

    if not provider:

        return jsonify({
            "message":
                "Provider not found"
        }), 404

    try:

        new_rating = Rating(

            customer_id=
                current_user.id,

            provider_id=
                provider.id,

            request_id=
                assistance_request.id,

            rating=
                rating_value,

            review=
                review
                if review
                else None
        )

        db.session.add(
            new_rating
        )

        # Existing ratings

        provider_ratings = Rating.query.filter_by(
            provider_id=provider.id
        ).all()

        total_ratings = (
            len(provider_ratings) + 1
        )

        total_score = (

            sum(
                item.rating
                for item in provider_ratings
            )

            + rating_value
        )

        provider.rating = round(

            total_score
            / total_ratings,

            1
        )

        db.session.commit()

        return jsonify({

            "message":
                "Rating submitted successfully",

            "rating":
                rating_value,

            "provider_rating":
                provider.rating

        }), 201

    except Exception as error:

        db.session.rollback()

        print(
            "Rating submission error:",
            error
        )

        return jsonify({

            "message":
                "Failed to submit rating. "
                "Please try again."

        }), 500


# ============================================================
# CUSTOMER REQUEST HISTORY
# ============================================================

@customer.route(
    "/history",
    methods=["GET"]
)
@role_required("customer")
def request_history():

    requests = AssistanceRequest.query.filter_by(

        customer_id=
            current_user.id

    ).order_by(

        AssistanceRequest.created_at.desc()

    ).all()

    history = []

    for item in requests:

        # Service

        service = db.session.get(
            Service,
            item.service_id
        )

        # Provider details

        provider_name = None
        provider_phone = None

        if item.provider:

            provider_phone = (
                item.provider.phone
            )

            if item.provider.user:

                provider_name = (
                    item.provider.user.name
                )

        # Rating

        rating = Rating.query.filter_by(

            request_id=item.id,

            customer_id=current_user.id

        ).first()

        history.append({

            "request_id":
                item.id,

            "service":
                service.name
                if service
                else "Unknown",

            "description":
                item.description,

            "provider":
                provider_name,

            "phone":
                provider_phone,

            "status":
                item.status,

            "latitude":
                item.latitude,

            "longitude":
                item.longitude,

            "created_at": (

                item.created_at.strftime(
                    "%d %b %Y, %I:%M %p"
                )

                if item.created_at

                else None
            ),

            "rating":
                rating.rating
                if rating
                else None,

            "review":
                rating.review
                if rating
                else None
        })

    return jsonify({

        "requests":
            history

    }), 200