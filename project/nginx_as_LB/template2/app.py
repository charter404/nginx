from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Template2 Website"

if __name__ == "__main__":
    app.run(port=8002)
