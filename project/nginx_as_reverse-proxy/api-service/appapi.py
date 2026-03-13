from flask import Flask, jsonify
app = Flask(__name__)

@app.route("/")
def api():
    return jsonify({"message": "API Service Working"})

if __name__ == "__main__":
    app.run(port=8002)
