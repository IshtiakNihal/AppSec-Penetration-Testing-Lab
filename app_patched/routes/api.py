from flask import Blueprint, jsonify, request, session

from app_patched.database import db
from app_patched.models import Transaction, User

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/users")
def users():
    users = User.query.all()
    return jsonify(
        [
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "account_balance": u.account_balance,
                "role": u.role,
            }
            for u in users
        ]
    )


@api_bp.route("/user/<int:user_id>/statements")
def statements(user_id):
    if "user_id" not in session or session["user_id"] != user_id:
        return jsonify({"error": "Forbidden"}), 403

    transactions = Transaction.query.filter_by(user_id=user_id).all()
    return jsonify(
        [
            {
                "id": t.id,
                "user_id": t.user_id,
                "amount": t.amount,
                "note": t.note,
            }
            for t in transactions
        ]
    )


@api_bp.route("/user/profile", methods=["POST"])
def update_profile():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user = User.query.get(session["user_id"])
    payload = request.json or {}

    for field in ["email", "username"]:
        if field in payload:
            setattr(user, field, payload[field])

    db.session.commit()
    return jsonify({"status": "success"})


@api_bp.route("/search", methods=["POST"])
def search_transactions():
    term = request.json.get("q", "")
    results = Transaction.query.filter(Transaction.note.ilike(f"%{term}%")).all()
    return jsonify(
        [
            {"id": row.id, "user_id": row.user_id, "amount": row.amount, "note": row.note}
            for row in results
        ]
    )
