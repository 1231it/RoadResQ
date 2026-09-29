from flask import Blueprint, request, jsonify, render_template
from flask_login import login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

from models import (
    db,
    User,
    Provider,
    Category,
    Service,
    ProviderService
)

from routes.role_required import role_required


auth = Blueprint("auth", __name__)


# =========================
# LOGIN PAGE
# =========================

@auth.route("/login-page", methods=["GET"])
def login_page():

    return render_template("login.html")


# =========================
# REGISTER PAGE
# =========================

@auth.route("/register-page", methods=["GET"])
def register_page():

    categories = Category.query.filter_by(
        is_active=True
    ).all()

    return render_template(
        "register.html",
        categories=categories
    )


# =========================
# REGISTER API
# =========================

@auth.route("/register", methods=["POST"])
def register():

    data = request.get_json() or {}

    name = data.get("name", "").strip()

    email = data.get("email", "").strip().lower()

    password = data.get("password", "")

    role = data.get("role", "customer")

    phone = data.get("phone", "").strip()

    service_ids = data.get("service_ids", [])


    # Only Customer and Provider can register
    if role not in ["customer", "provider"]:

        return jsonify({
            "message": "Invalid registration role"
        }), 400


    if not name or not email or not password:

        return jsonify({
            "message": "Name, email and password are required"
        }), 400


    if len(password) < 6:

        return jsonify({
            "message": "Password must contain at least 6 characters"
        }), 400


    existing_user = User.query.filter_by(
        email=email
    ).first()


    if existing_user:

        return jsonify({
            "message": "Email already registered"
        }), 409


    # Provider-specific validation
    if role == "provider":

        if not phone:

            return jsonify({
                "message": "Phone number is required for providers"
            }), 400


        if not service_ids:

            return jsonify({
                "message": "Select at least one service"
            }), 400


        valid_services = Service.query.filter(
            Service.id.in_(service_ids),
            Service.is_active == True
        ).all()


        if len(valid_services) != len(set(service_ids)):

            return jsonify({
                "message": "One or more selected services are invalid"
            }), 400


    try:

        hashed_password = generate_password_hash(
            password
        )


        user = User(
            name=name,
            email=email,
            password=hashed_password,
            role=role
        )


        db.session.add(user)

        db.session.flush()


        # Create provider profile
        if role == "provider":

            provider_profile = Provider(
                user_id=user.id,
                phone=phone,
                latitude=None,
                longitude=None,
                is_available=False,
                rating=0.0
            )


            db.session.add(provider_profile)

            db.session.flush()


            # Assign selected services
            for service_id in set(service_ids):

                provider_service = ProviderService(
                    provider_id=provider_profile.id,
                    service_id=int(service_id)
                )

                db.session.add(provider_service)


        db.session.commit()


        return jsonify({
            "message": "Registration successful"
        }), 201


    except Exception as error:

        db.session.rollback()

        print("Registration error:", error)

        return jsonify({
            "message": "Registration failed. Please try again."
        }), 500


# =========================
# LOGIN API
# =========================

@auth.route("/login", methods=["POST"])
def login():

    data = request.get_json() or {}


    email = data.get(
        "email",
        ""
    ).strip().lower()


    password = data.get(
        "password",
        ""
    )


    selected_role = data.get(
        "role",
        "customer"
    )


    if not email or not password:

        return jsonify({
            "message": "Email and password are required"
        }), 400


    # Customer + Provider + Admin
    if selected_role not in [
        "customer",
        "provider",
        "admin"
    ]:

        return jsonify({
            "message": "Invalid login role"
        }), 400


    user = User.query.filter_by(
        email=email
    ).first()


    if not user:

        return jsonify({
            "message": "Invalid email or password"
        }), 401


    if not check_password_hash(
        user.password,
        password
    ):

        return jsonify({
            "message": "Invalid email or password"
        }), 401


    # Important role verification
    if user.role != selected_role:

        return jsonify({
            "message":
                f"This account is registered as {user.role}. "
                f"Please select the correct login type."
        }), 403


    login_user(user)


    # Redirect according to role
    if user.role == "admin":

        redirect_url = "/admin/dashboard"

    elif user.role == "provider":

        redirect_url = "/provider/dashboard"

    else:

        redirect_url = "/customer/dashboard"


    return jsonify({

        "message": "Login successful",

        "redirect_url": redirect_url,

        "user": {

            "id": user.id,

            "name": user.name,

            "email": user.email,

            "role": user.role

        }

    }), 200


# =========================
# PROFILE
# =========================

@auth.route("/profile", methods=["GET"])
@login_required
def profile():

    return jsonify({

        "message": "You are logged in",

        "user": {

            "id": current_user.id,

            "name": current_user.name,

            "email": current_user.email,

            "role": current_user.role

        }

    }), 200


# =========================
# LOGOUT
# =========================

@auth.route("/logout", methods=["POST"])
@login_required
def logout():

    logout_user()

    return jsonify({
        "message": "Logout successful"
    }), 200


# =========================
# CUSTOMER AREA
# =========================

@auth.route("/customer-area", methods=["GET"])
@role_required("customer")
def customer_area():

    return jsonify({

        "message": "Welcome Customer!",

        "role": current_user.role

    }), 200


# =========================
# PROVIDER AREA
# =========================

@auth.route("/provider-area", methods=["GET"])
@role_required("provider")
def provider_area():

    return jsonify({

        "message": "Welcome Service Provider!",

        "role": current_user.role

    }), 200


# =========================
# ADMIN AREA
# =========================

@auth.route("/admin-area", methods=["GET"])
@role_required("admin")
def admin_area():

    return jsonify({

        "message": "Welcome Admin!",

        "role": current_user.role

    }), 200