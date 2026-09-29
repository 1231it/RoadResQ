from flask import Flask, redirect
from flask_login import LoginManager

from models import db

from routes.auth import auth
from routes.customer import customer
from routes.provider import provider
from routes.admin import admin
from routes.assistant import assistant


app = Flask(__name__)

app.config["SECRET_KEY"] = "roadresq-dev-secret-key"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///roadresq.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# ---------------------------------------------------------
# DATABASE
# ---------------------------------------------------------

db.init_app(app)


# ---------------------------------------------------------
# LOGIN MANAGER
# ---------------------------------------------------------

login_manager = LoginManager()

login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):

    from models import User

    return db.session.get(
        User,
        int(user_id)
    )


# ---------------------------------------------------------
# BLUEPRINTS
# ---------------------------------------------------------

app.register_blueprint(
    auth,
    url_prefix="/auth"
)

app.register_blueprint(
    customer,
    url_prefix="/customer"
)

app.register_blueprint(
    provider,
    url_prefix="/provider"
)

app.register_blueprint(
    admin,
    url_prefix="/admin"
)

app.register_blueprint(
    assistant,
    url_prefix="/assistant"
)


# ---------------------------------------------------------
# CREATE DATABASE TABLES
# ---------------------------------------------------------

with app.app_context():

    db.create_all()


# ---------------------------------------------------------
# HOME
# ---------------------------------------------------------

@app.route("/")
def home():

    return redirect(
        "/auth/login-page"
    )


# ---------------------------------------------------------
# RUN APPLICATION
# ---------------------------------------------------------

if __name__ == "__main__":

    app.run(
        debug=True
    )