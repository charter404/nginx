from flask import Flask
app = Flask(__name__)

@app.route("/")
def portfolio():
    return "Portfolio Service Page"

if __name__ == "__main__":
    app.run(port=8003)
