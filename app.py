from flask import Flask

app = Flask(__name__)


@app.route("/")
def home():
    return """
    <h1>RoadResQ</h1>
    <p>Smart Local Help & Emergency Assistance Platform</p>
    <p>Server is running successfully!</p>
    """


if __name__ == "__main__":
    app.run(debug=True)