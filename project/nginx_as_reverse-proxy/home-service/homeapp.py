# home-service/app.py
from flask import Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "Welcome to Home Service"

if __name__ == "__main__":
    app.run(port=8001)
