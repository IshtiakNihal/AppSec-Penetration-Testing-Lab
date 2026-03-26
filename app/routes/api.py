from flask import Blueprint, jsonify, request, session
from sqlalchemy import text

from app.database import db
from app.models import Transaction, User

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
                "password": u.password,
                "api_key": u.api_key,
                "account_balance": u.account_balance,
                "role": u.role,
            }
            for u in users
        ]
    )


@api_bp.route("/user/<int:user_id>/statements")
def statements(user_id):
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
    for key, value in request.json.items():
        if hasattr(user, key):
            setattr(user, key, value)

    db.session.commit()
    return jsonify({"status": "success", "user": {"role": user.role}})


@api_bp.route("/search", methods=["POST"])
def search_transactions():
    term = request.json.get("q", "")
    query = f"SELECT * FROM transactions WHERE note LIKE '%{term}%'"

    try:
        results = db.session.execute(text(query)).fetchall()
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(
        [
            {"id": row[0], "user_id": row[1], "amount": row[2], "note": row[3]}
            for row in results
        ]
    )
