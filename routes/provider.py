from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user

from routes.role_required import role_required

from models import (
    db,
    Provider,
    Service,
    ProviderService,
    AssistanceRequest,
    User
)

provider = Blueprint("provider", __name__)


def get_provider():
    """Get the provider profile for the currently logged-in provider."""

    provider_profile = Provider.query.filter_by(
        user_id=current_user.id
    ).first()

    # Safety: create provider profile if missing
    if not provider_profile:
        provider_profile = Provider(
            user_id=current_user.id,
            phone="Not provided",
            latitude=None,
            longitude=None,
            is_available=False,
            rating=0.0
        )

        db.session.add(provider_profile)
        db.session.commit()

    return provider_profile


@provider.route("/dashboard", methods=["GET"])
@role_required("provider")
def dashboard():

    provider_profile = get_provider()

    # All active services for service selection
    services = Service.query.filter_by(
        is_active=True
    ).order_by(
        Service.category_id,
        Service.name
    ).all()

    # Services selected by THIS provider
    selected_service_ids = {
        item.service_id
        for item in ProviderService.query.filter_by(
            provider_id=provider_profile.id
        ).all()
    }

    # ---------------------------------------------------------
    # NEW REQUESTS
    # ---------------------------------------------------------
    #
    # If customer specifically selected this provider:
    #     provider_id == current provider
    #
    # If provider_id is NULL:
    #     request is available for providers offering the service
    #
    # This prevents Provider B from seeing a request already
    # specifically assigned to Provider A.
    # ---------------------------------------------------------

    pending_requests = []

    if selected_service_ids:

        pending_requests = AssistanceRequest.query.filter(
            AssistanceRequest.status == "PENDING",
            AssistanceRequest.service_id.in_(selected_service_ids),
            db.or_(
                AssistanceRequest.provider_id == None,
                AssistanceRequest.provider_id == provider_profile.id
            )
        ).order_by(
            AssistanceRequest.created_at.desc()
        ).all()

    # ---------------------------------------------------------
    # MY ACTIVE REQUESTS
    # ---------------------------------------------------------
    #
    # Only requests assigned to THIS provider.
    #
    # ACCEPTED / IN_PROGRESS
    # ---------------------------------------------------------

    active_requests = AssistanceRequest.query.filter(
        AssistanceRequest.provider_id == provider_profile.id,
        AssistanceRequest.status.in_([
            "ACCEPTED",
            "IN_PROGRESS"
        ])
    ).order_by(
        AssistanceRequest.created_at.desc()
    ).all()

    # ---------------------------------------------------------
    # COMPLETED REQUESTS
    # ---------------------------------------------------------

    completed_requests = AssistanceRequest.query.filter(
        AssistanceRequest.provider_id == provider_profile.id,
        AssistanceRequest.status == "COMPLETED"
    ).order_by(
        AssistanceRequest.created_at.desc()
    ).all()

    return render_template(
        "provider_dashboard.html",
        provider=provider_profile,
        services=services,
        selected_service_ids=selected_service_ids,
        pending_requests=pending_requests,
        active_requests=active_requests,
        completed_requests=completed_requests
    )


# =========================================================
# PROVIDER LOCATION
# =========================================================

@provider.route("/location", methods=["POST"])
@role_required("provider")
def update_location():

    data = request.get_json() or {}

    latitude = data.get("latitude")
    longitude = data.get("longitude")

    if latitude is None or longitude is None:
        return jsonify({
            "message": "Latitude and longitude are required"
        }), 400

    try:

        provider_profile = get_provider()

        provider_profile.latitude = float(latitude)
        provider_profile.longitude = float(longitude)

        db.session.commit()

        return jsonify({
            "message": "Location updated successfully",
            "latitude": provider_profile.latitude,
            "longitude": provider_profile.longitude
        }), 200

    except (ValueError, TypeError):

        return jsonify({
            "message": "Invalid location coordinates"
        }), 400


# =========================================================
# PROVIDER AVAILABILITY
# =========================================================

@provider.route("/availability", methods=["POST"])
@role_required("provider")
def update_availability():

    data = request.get_json() or {}

    is_available = data.get("is_available")

    if not isinstance(is_available, bool):
        return jsonify({
            "message": "Invalid availability value"
        }), 400

    provider_profile = get_provider()

    # Provider must share location before becoming available
    if is_available is True:

        if (
            provider_profile.latitude is None
            or provider_profile.longitude is None
        ):
            return jsonify({
                "message": (
                    "Please update your current location "
                    "before becoming available."
                )
            }), 400

    provider_profile.is_available = is_available

    db.session.commit()

    return jsonify({
        "message": "Availability updated successfully",
        "is_available": provider_profile.is_available
    }), 200


# =========================================================
# PROVIDER SERVICES
# =========================================================

@provider.route("/services", methods=["POST"])
@role_required("provider")
def update_services():

    data = request.get_json() or {}

    service_ids = data.get("service_ids", [])

    if not isinstance(service_ids, list):
        return jsonify({
            "message": "Invalid service selection"
        }), 400

    try:

        service_ids = list(
            set(
                int(service_id)
                for service_id in service_ids
            )
        )

    except (ValueError, TypeError):

        return jsonify({
            "message": "Invalid service IDs"
        }), 400

    provider_profile = get_provider()

    valid_services = Service.query.filter(
        Service.id.in_(service_ids),
        Service.is_active == True
    ).all()

    valid_service_ids = {
        service.id
        for service in valid_services
    }

    if set(service_ids) != valid_service_ids:

        return jsonify({
            "message": "One or more selected services are invalid"
        }), 400

    # Remove old services
    ProviderService.query.filter_by(
        provider_id=provider_profile.id
    ).delete()

    # Add new services
    for service_id in service_ids:

        db.session.add(
            ProviderService(
                provider_id=provider_profile.id,
                service_id=service_id
            )
        )

    db.session.commit()

    return jsonify({
        "message": "Services updated successfully",
        "service_count": len(service_ids)
    }), 200


# =========================================================
# ACCEPT REQUEST
# =========================================================

@provider.route("/request/<int:request_id>/accept", methods=["POST"])
@role_required("provider")
def accept_request(request_id):

    provider_profile = get_provider()

    if not provider_profile.is_available:

        return jsonify({
            "message": (
                "You must be available to accept requests."
            )
        }), 400

    assistance_request = db.session.get(
        AssistanceRequest,
        request_id
    )

    if not assistance_request:

        return jsonify({
            "message": "Request not found"
        }), 404

    if assistance_request.status != "PENDING":

        return jsonify({
            "message": "This request is no longer available."
        }), 409

    # If request is already assigned to another provider
    if (
        assistance_request.provider_id is not None
        and assistance_request.provider_id != provider_profile.id
    ):

        return jsonify({
            "message": (
                "This request is already assigned "
                "to another provider."
            )
        }), 409

    # Check whether this provider offers the service
    provider_service = ProviderService.query.filter_by(
        provider_id=provider_profile.id,
        service_id=assistance_request.service_id
    ).first()

    if not provider_service:

        return jsonify({
            "message": (
                "You are not registered for this service."
            )
        }), 403

    # Assign request to this provider
    assistance_request.provider_id = provider_profile.id
    assistance_request.status = "ACCEPTED"

    db.session.commit()

    return jsonify({
        "message": "Request accepted successfully",
        "request_id": assistance_request.id,
        "status": assistance_request.status
    }), 200


# =========================================================
# REJECT REQUEST
# =========================================================

@provider.route("/request/<int:request_id>/reject", methods=["POST"])
@role_required("provider")
def reject_request(request_id):

    provider_profile = get_provider()

    assistance_request = db.session.get(
        AssistanceRequest,
        request_id
    )

    if not assistance_request:

        return jsonify({
            "message": "Request not found"
        }), 404

    if assistance_request.status != "PENDING":

        return jsonify({
            "message": "This request is no longer available."
        }), 409

    # If specifically assigned to another provider,
    # this provider cannot reject it.
    if (
        assistance_request.provider_id is not None
        and assistance_request.provider_id != provider_profile.id
    ):

        return jsonify({
            "message": (
                "This request is assigned to another provider."
            )
        }), 403

    assistance_request.provider_id = provider_profile.id
    assistance_request.status = "REJECTED"

    db.session.commit()

    return jsonify({
        "message": "Request rejected",
        "request_id": assistance_request.id,
        "status": assistance_request.status
    }), 200


# =========================================================
# UPDATE REQUEST STATUS
# =========================================================

@provider.route(
    "/request/<int:request_id>/status",
    methods=["POST"]
)
@role_required("provider")
def update_request_status(request_id):

    data = request.get_json() or {}

    new_status = data.get("status")

    allowed_statuses = [
        "IN_PROGRESS",
        "COMPLETED"
    ]

    if new_status not in allowed_statuses:

        return jsonify({
            "message": "Invalid status"
        }), 400

    provider_profile = get_provider()

    assistance_request = db.session.get(
        AssistanceRequest,
        request_id
    )

    if not assistance_request:

        return jsonify({
            "message": "Request not found"
        }), 404

    # Security:
    # Provider can update ONLY their own requests.
    if assistance_request.provider_id != provider_profile.id:

        return jsonify({
            "message": "You do not own this request"
        }), 403

    # ACCEPTED -> IN_PROGRESS
    if new_status == "IN_PROGRESS":

        if assistance_request.status != "ACCEPTED":

            return jsonify({
                "message": (
                    "Only accepted requests can be started."
                )
            }), 400

    # IN_PROGRESS -> COMPLETED
    if new_status == "COMPLETED":

        if assistance_request.status != "IN_PROGRESS":

            return jsonify({
                "message": (
                    "Only active requests can be completed."
                )
            }), 400

    assistance_request.status = new_status

    db.session.commit()

    return jsonify({
        "message": "Request status updated",
        "request_id": assistance_request.id,
        "status": assistance_request.status
    }), 200