from flask import Flask
from models import db

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///roadresq.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return """
    <h1>RoadResQ</h1>
    <p>Database connected successfully!</p>
    """


if __name__ == "__main__":
    app.run(debug=True)