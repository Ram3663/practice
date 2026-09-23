from flask import Flask, jsonify


app = Flask(__name__)


@app.get("/")
def home():
    return "<h1>Hello from Flask</h1><p>Your small app is running.</p>"


@app.get("/health")
def health():
    return jsonify(status="ok")


if __name__ == "__main__":
    app.run(debug=True)