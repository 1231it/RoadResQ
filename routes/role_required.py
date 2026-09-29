from functools import wraps
from flask import jsonify
from flask_login import current_user, login_required


def role_required(required_role):

    def decorator(function):

        @wraps(function)
        @login_required
        def wrapper(*args, **kwargs):

            if current_user.role != required_role:
                return jsonify({
                    "message": "Access denied"
                }), 403

            return function(*args, **kwargs)

        return wrapper

    return decorator