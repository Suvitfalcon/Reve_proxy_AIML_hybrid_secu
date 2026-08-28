from flask import Flask, jsonify, make_response
import time

app = Flask(__name__)


@app.route("/")
def home():
    return jsonify({
        "message": "Backend Server is Running",
        "server": "Backend :5001"
    })


@app.route("/products")
def products():
    response = make_response(jsonify({
        "products": [
            {"id": 1, "name": "Laptop", "price": 55000},
            {"id": 2, "name": "Phone", "price": 25000},
            {"id": 3, "name": "Headphones", "price": 3000}
        ],
        "generated_at": time.time()
    }))

    # This response is safe for our demo cache
    response.headers["Cache-Control"] = "public, max-age=60"

    return response


@app.route("/news")
def news():
    response = make_response(jsonify({
        "news": [
            "Technology news",
            "Cybersecurity news",
            "AI news"
        ],
        "generated_at": time.time()
    }))

    response.headers["Cache-Control"] = "public, max-age=60"

    return response


@app.route("/profile")
def profile():
    response = make_response(jsonify({
        "user": "Demo User",
        "email": "demo@example.com",
        "message": "This is private user information"
    }))

    # This response should NOT be stored in a shared cache
    response.headers["Cache-Control"] = "private, no-store"
    response.set_cookie("session", "demo-session-123")

    return response


@app.route("/login", methods=["POST"])
def login():
    response = make_response(jsonify({
        "message": "Login successful"
    }))

    # Login responses should not be cached
    response.headers["Cache-Control"] = "no-store"
    response.set_cookie("session", "demo-session-456")

    return response

@app.route("/offers")
def offers():

    response = make_response(jsonify({
        "offers": [
            "10% off laptops",
            "20% off headphones",
            "15% off phones"
        ],
        "generated_at": time.time()
    }))

    response.headers["Cache-Control"] = "public, max-age=60"

    return response


@app.route("/suvit")
def offers():

    response = make_response(jsonify({
        "offers": [
            "hero",
            "tall guy",
            "spider man"
        ],
        "generated_at": time.time()
    }))

    response.headers["Cache-Control"] = "public, max-age=30"

    return response

@app.route("/vidya")
def offers():

    response = make_response(jsonify({
        "offers": [
            "beautiful",
            "cute",
            "cry  baby"
        ],
        "generated_at": time.time()
    }))

    response.headers["Cache-Control"] = "public, max-age=50"

    return response


if __name__ == "__main__":
    print("Backend server running on http://localhost:5001")

    app.run(
        host="127.0.0.1",
        port=5001,
        debug=True
    )