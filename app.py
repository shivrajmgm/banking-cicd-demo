from flask import Flask, jsonify, request

app = Flask(__name__)

# Mock Database simulating customer state
db = {
    "user123": {
        "password": "securepass",
        "failed_attempts": 0,
        "locked": False,
        "balance": 150000.00,
        "daily_transferred": 0,
        "card_status": "Active"
    }
}


# BANK-6: Customer Login
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user = db.get(data.get("user_id"))

    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    if user["locked"]:
        return jsonify({"error": "Account locked for 30 minutes"}), 403

    if data.get("password") != user["password"]:
        user["failed_attempts"] += 1
        if user["failed_attempts"] >= 3:
            user["locked"] = True
            return jsonify({"error": "Account locked for 30 minutes"}), 403
        return jsonify({"error": "Invalid credentials"}), 401

    user["failed_attempts"] = 0
    return jsonify({"message": "Dashboard access granted", "session_timeout": "5 minutes"})


# BANK-7: View Balance and Mini Statement
@app.route("/dashboard/<user_id>", methods=["GET"])
def dashboard(user_id):
    user = db.get(user_id)
    return jsonify({
        "balance": round(user["balance"], 2),
        "transactions": [
            {"date": "2026-10-14", "desc": "Grocery", "amount": 500.00, "type": "Dr"},
            {"date": "2026-10-15", "desc": "Salary", "amount": 50000.00, "type": "Cr"}
        ]
    })


# BANK-8: Fund Transfer
@app.route("/transfer", methods=["POST"])
def transfer():
    data = request.json
    user = db.get(data.get("user_id"))
    amount = data.get("amount", 0)

    if data.get("otp") != "123456":
        return jsonify({"error": "OTP verification failed"}), 400

    if amount > user["balance"]:
        return jsonify({"error": "Insufficient balance"}), 400

    if amount + user["daily_transferred"] > 100000:
        return jsonify({"error": "Daily limit of Rs. 1,00,000 exceeded"}), 400

    user["balance"] -= amount
    user["daily_transferred"] += amount
    return jsonify({"message": "Transfer successful", "ref": "TXN998877", "alert": "SMS sent"})


# BANK-10: Block/Unblock Debit Card
@app.route("/card/status", methods=["POST"])
def card_status():
    data = request.json
    user = db.get(data.get("user_id"))
    if data.get("otp") != "123456":
        return jsonify({"error": "OTP verification failed"}), 400

    user["card_status"] = data.get("action")
    return jsonify({"message": f"Card is now {user['card_status']}", "alert": "Confirmation sent"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)