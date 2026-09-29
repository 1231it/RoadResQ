from flask import Blueprint, render_template, jsonify
from flask_login import current_user

from routes.role_required import role_required

from models import (
    db,
    User,
    Provider,
    AssistanceRequest,
    Service,
    Category,
    Rating
)

admin = Blueprint("admin", __name__)


# ---------------------------------------------------------
# ADMIN DASHBOARD
# ---------------------------------------------------------

@admin.route("/dashboard", methods=["GET"])
@role_required("admin")
def dashboard():

    total_users = User.query.count()

    total_customers = User.query.filter_by(
        role="customer"
    ).count()

    total_providers = Provider.query.count()

    total_requests = AssistanceRequest.query.count()

    pending_requests = AssistanceRequest.query.filter_by(
        status="PENDING"
    ).count()

    accepted_requests = AssistanceRequest.query.filter_by(
        status="ACCEPTED"
    ).count()

    in_progress_requests = AssistanceRequest.query.filter_by(
        status="IN_PROGRESS"
    ).count()

    completed_requests = AssistanceRequest.query.filter_by(
        status="COMPLETED"
    ).count()

    rejected_requests = AssistanceRequest.query.filter_by(
        status="REJECTED"
    ).count()

    cancelled_requests = AssistanceRequest.query.filter_by(
        status="CANCELLED"
    ).count()

    available_providers = Provider.query.filter_by(
        is_available=True
    ).count()

    total_services = Service.query.filter_by(
        is_active=True
    ).count()

    total_categories = Category.query.filter_by(
        is_active=True
    ).count()

    total_ratings = Rating.query.count()

    return render_template(
        "admin_dashboard.html",

        total_users=total_users,
        total_customers=total_customers,
        total_providers=total_providers,

        total_requests=total_requests,
        pending_requests=pending_requests,
        accepted_requests=accepted_requests,
        in_progress_requests=in_progress_requests,
        completed_requests=completed_requests,
        rejected_requests=rejected_requests,
        cancelled_requests=cancelled_requests,

        available_providers=available_providers,

        total_services=total_services,
        total_categories=total_categories,
        total_ratings=total_ratings
    )


# ---------------------------------------------------------
# USERS
# ---------------------------------------------------------

@admin.route("/users", methods=["GET"])
@role_required("admin")
def users():

    users = User.query.order_by(
        User.id.desc()
    ).all()

    return jsonify([
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
        for user in users
    ])


# ---------------------------------------------------------
# PROVIDERS
# ---------------------------------------------------------

@admin.route("/providers", methods=["GET"])
@role_required("admin")
def providers():

    providers = Provider.query.order_by(
        Provider.id.desc()
    ).all()

    result = []

    for provider in providers:

        result.append({
            "id": provider.id,
            "name": (
                provider.user.name
                if provider.user
                else "Unknown"
            ),
            "email": (
                provider.user.email
                if provider.user
                else ""
            ),
            "phone": provider.phone,
            "available": provider.is_available,
            "rating": round(
                provider.rating,
                1
            )
        })

    return jsonify(result)


# ---------------------------------------------------------
# REQUESTS
# ---------------------------------------------------------

@admin.route("/requests", methods=["GET"])
@role_required("admin")
def requests():

    requests = AssistanceRequest.query.order_by(
        AssistanceRequest.id.desc()
    ).all()

    result = []

    for item in requests:

        service = db.session.get(
            Service,
            item.service_id
        )

        provider = None

        if item.provider_id:
            provider = db.session.get(
                Provider,
                item.provider_id
            )

        result.append({
            "id": item.id,

            "customer": (
                item.customer.name
                if item.customer
                else "Unknown"
            ),

            "service": (
                service.name
                if service
                else "Unknown"
            ),

            "provider": (
                provider.user.name
                if provider and provider.user
                else "Not assigned"
            ),

            "status": item.status,

            "description": item.description,

            "created_at": (
                item.created_at.strftime(
                    "%Y-%m-%d %H:%M"
                )
                if item.created_at
                else ""
            )
        })

    return jsonify(result)


# ---------------------------------------------------------
# ADMIN STATISTICS API
# ---------------------------------------------------------

@admin.route("/statistics", methods=["GET"])
@role_required("admin")
def statistics():

    return jsonify({
        "requests": {
            "pending": AssistanceRequest.query.filter_by(
                status="PENDING"
            ).count(),

            "accepted": AssistanceRequest.query.filter_by(
                status="ACCEPTED"
            ).count(),

            "in_progress": AssistanceRequest.query.filter_by(
                status="IN_PROGRESS"
            ).count(),

            "completed": AssistanceRequest.query.filter_by(
                status="COMPLETED"
            ).count(),

            "rejected": AssistanceRequest.query.filter_by(
                status="REJECTED"
            ).count(),

            "cancelled": AssistanceRequest.query.filter_by(
                status="CANCELLED"
            ).count()
        },

        "users": {
            "customers": User.query.filter_by(
                role="customer"
            ).count(),

            "providers": Provider.query.count()
        }
    })