import time

import requests
from flask import Blueprint, jsonify, request, session

from app.database import db
from app.models import Transaction, User

payments_bp = Blueprint("payments", __name__)


@payments_bp.route("/api/verify-payment", methods=["POST"])
def verify_payment():
    webhook_url = request.json.get("webhook_url", "")

    try:
        response = requests.get(webhook_url, timeout=5)
        return jsonify({"status": "ok", "response": response.text[:200]})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


@payments_bp.route("/fetch")
def fetch_url():
    url = request.args.get("url", "")
    try:
        response = requests.get(url, timeout=5)
        return response.text
    except Exception as exc:
        return f"Error: {exc}", 400


@payments_bp.route("/api/transfer", methods=["POST"])
@payments_bp.route("/transfer", methods=["POST"])
def transfer():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    recipient = request.json.get("recipient")
    amount = float(request.json.get("amount", 0))

    user = User.query.get(session["user_id"])
    if not user:
        return jsonify({"error": "User not found"}), 404

    if user.account_balance < amount:
        return jsonify({"error": "Insufficient funds"}), 400

    time.sleep(0.2)
    user.account_balance -= amount
    tx = Transaction(user_id=user.id, amount=-amount, note=f"Transfer to {recipient}")
    db.session.add(tx)
    db.session.commit()

    return jsonify({"status": "ok", "balance": user.account_balance})
