from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required


assistant = Blueprint("assistant", __name__)


# ---------------------------------------------------------
# ASSISTANT PAGE
# ---------------------------------------------------------

@assistant.route("/", methods=["GET"])
@login_required
def assistant_page():
    return render_template("assistant.html")


# ---------------------------------------------------------
# SMART SERVICE RECOMMENDATION
# ---------------------------------------------------------

@assistant.route("/recommend", methods=["POST"])
@login_required
def recommend():

    data = request.get_json() or {}

    problem = data.get("problem", "").strip().lower()

    if not problem:
        return jsonify({
            "message": "Please describe your problem."
        }), 400


    # -----------------------------------------------------
    # VEHICLE - TYRE
    # -----------------------------------------------------

    tyre_words = [
        "puncture",
        "flat tyre",
        "flat tire",
        "tyre",
        "tire"
    ]

    if any(word in problem for word in tyre_words):

        return jsonify({
            "category": "Vehicle Assistance",
            "service": "Tyre Assistance",
            "icon": "🛞",
            "message": (
                "It looks like you have a tyre-related problem. "
                "Tyre Assistance can help you at your location."
            )
        })


    # -----------------------------------------------------
    # VEHICLE - FUEL
    # -----------------------------------------------------

    fuel_words = [
        "fuel",
        "petrol",
        "diesel",
        "empty tank",
        "out of fuel",
        "no petrol",
        "no diesel"
    ]

    if any(word in problem for word in fuel_words):

        return jsonify({
            "category": "Vehicle Assistance",
            "service": "Fuel Delivery",
            "icon": "⛽",
            "message": (
                "You appear to be out of fuel. "
                "Fuel Delivery can bring fuel to your current location."
            )
        })


    # -----------------------------------------------------
    # VEHICLE - BATTERY
    # -----------------------------------------------------

    battery_words = [
        "battery",
        "dead battery",
        "battery dead",
        "car won't start",
        "bike won't start",
        "vehicle won't start"
    ]

    if any(word in problem for word in battery_words):

        return jsonify({
            "category": "Vehicle Assistance",
            "service": "Mechanic",
            "icon": "🔋",
            "message": (
                "This sounds like a battery or starting problem. "
                "A Mechanic can come to your location."
            )
        })


    # -----------------------------------------------------
    # VEHICLE - BREAKDOWN
    # -----------------------------------------------------

    breakdown_words = [
        "breakdown",
        "vehicle broke down",
        "car broke down",
        "bike broke down",
        "engine problem",
        "engine failure"
    ]

    if any(word in problem for word in breakdown_words):

        return jsonify({
            "category": "Vehicle Assistance",
            "service": "Mechanic",
            "icon": "🔧",
            "message": (
                "Your vehicle appears to have broken down. "
                "A Mechanic can inspect it at your location."
            )
        })


    # -----------------------------------------------------
    # TOWING
    # -----------------------------------------------------

    towing_words = [
        "tow",
        "towing",
        "tow truck",
        "vehicle cannot move",
        "car cannot move"
    ]

    if any(word in problem for word in towing_words):

        return jsonify({
            "category": "Vehicle Assistance",
            "service": "Towing",
            "icon": "🚛",
            "message": (
                "Your vehicle may need to be transported. "
                "Towing assistance is recommended."
            )
        })


    # -----------------------------------------------------
    # FOOD
    # -----------------------------------------------------

    food_words = [
        "food",
        "hungry",
        "eat",
        "meal",
        "food delivery"
    ]

    if any(word in problem for word in food_words):

        return jsonify({
            "category": "Food Assistance",
            "service": "Food Delivery",
            "icon": "🍱",
            "message": (
                "You need food assistance. "
                "Food Delivery can bring food to your location."
            )
        })


    # -----------------------------------------------------
    # MEDICAL / PHARMACY
    # -----------------------------------------------------

    medicine_words = [
        "medicine",
        "medicines",
        "tablet",
        "tablets",
        "pharmacy",
        "medical",
        "medicine delivery"
    ]

    if any(word in problem for word in medicine_words):

        return jsonify({
            "category": "Medical Assistance",
            "service": "Medicine Delivery",
            "icon": "💊",
            "message": (
                "You appear to need medicine. "
                "Medicine Delivery can help you get it locally."
            )
        })


    # -----------------------------------------------------
    # ELECTRICIAN
    # -----------------------------------------------------

    electrician_words = [
        "electrician",
        "electricity",
        "power problem",
        "wiring",
        "switch",
        "electric"
    ]

    if any(word in problem for word in electrician_words):

        return jsonify({
            "category": "Home Services",
            "service": "Electrician",
            "icon": "⚡",
            "message": (
                "This looks like an electrical problem. "
                "An Electrician can assist you."
            )
        })


    # -----------------------------------------------------
    # PLUMBER
    # -----------------------------------------------------

    plumber_words = [
        "plumber",
        "water leakage",
        "pipe leak",
        "water leak",
        "tap",
        "pipe problem"
    ]

    if any(word in problem for word in plumber_words):

        return jsonify({
            "category": "Home Services",
            "service": "Plumber",
            "icon": "🚰",
            "message": (
                "This appears to be a plumbing problem. "
                "A Plumber can assist you."
            )
        })


    # -----------------------------------------------------
    # LOCAL DELIVERY
    # -----------------------------------------------------

    delivery_words = [
        "package",
        "parcel",
        "pickup",
        "delivery",
        "deliver something"
    ]

    if any(word in problem for word in delivery_words):

        return jsonify({
            "category": "Local Delivery",
            "service": "Small Package Delivery",
            "icon": "📦",
            "message": (
                "You need a local delivery service. "
                "Small Package Delivery can help."
            )
        })


    # -----------------------------------------------------
    # DEFAULT
    # -----------------------------------------------------

    return jsonify({
        "category": "Other Help",
        "service": "General Local Assistance",
        "icon": "🆘",
        "message": (
            "I could not identify a specific service. "
            "General Local Assistance may be suitable."
        )
    })