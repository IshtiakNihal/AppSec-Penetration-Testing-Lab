import ipaddress
import requests
from flask import Blueprint, jsonify, request, session

from app_patched.database import db
from app_patched.models import Transaction, User

payments_bp = Blueprint("payments", __name__)


def is_private_ip(url: str) -> bool:
    try:
        host = url.split("//", 1)[-1].split("/", 1)[0].split(":", 1)[0]
        return ipaddress.ip_address(host).is_private
    except Exception:
        return True


@payments_bp.route("/api/verify-payment", methods=["POST"])
def verify_payment():
    webhook_url = request.json.get("webhook_url", "")
    if is_private_ip(webhook_url):
        return jsonify({"error": "Blocked internal address"}), 400

    response = requests.get(webhook_url, timeout=5)
    return jsonify({"status": "ok", "response": response.text[:200]})


@payments_bp.route("/fetch")
def fetch_url():
    url = request.args.get("url", "")
    if is_private_ip(url):
        return "Blocked internal address", 400
    response = requests.get(url, timeout=5)
    return response.text


@payments_bp.route("/api/transfer", methods=["POST"])
@payments_bp.route("/transfer", methods=["POST"])
def transfer():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    token = request.headers.get("X-CSRF-Token")
    if token != session.get("csrf_token"):
        return jsonify({"error": "CSRF validation failed"}), 400

    recipient = request.json.get("recipient")
    amount = float(request.json.get("amount", 0))

    user = User.query.get(session["user_id"])
    if not user or user.account_balance < amount:
        return jsonify({"error": "Insufficient funds"}), 400

    user.account_balance -= amount
    tx = Transaction(user_id=user.id, amount=-amount, note=f"Transfer to {recipient}")
    db.session.add(tx)
    db.session.commit()

    return jsonify({"status": "ok", "balance": user.account_balance})
