from flask import Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "Secure Home Service"

@app.route("/api")
def api():
    return "Secure API"

app.run(host="0.0.0.0", port=8000)
