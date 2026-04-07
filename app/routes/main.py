from flask import Blueprint, redirect, render_template, request, session, url_for

from app.database import db
from app.models import User, Comment

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return render_template("home.html")


@main_bp.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    user = User.query.get(session["user_id"])
    return render_template("dashboard.html", user=user)


@main_bp.route("/search")
def search():
    query = request.args.get("q", "")
    return render_template("search.html", query=query)


@main_bp.route("/settings")
def settings():
    color = request.args.get("color", "blue")
    return render_template("settings.html", color=color)


@main_bp.route("/comments", methods=["GET", "POST"])
def comments():
    if request.method == "POST":
        if "user_id" not in session:
            return "Unauthorized", 401
        text = request.form.get("text", "")
        comment = Comment(user_id=session["user_id"], text=text)
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for("main.comments"))

    all_comments = Comment.query.order_by(Comment.created_at.desc()).all()
    return render_template("comments.html", comments=all_comments)


@main_bp.route("/user/profile", methods=["GET", "POST"])
def user_profile():
    if request.method == "POST":
        if "user_id" not in session:
            return "Unauthorized", 401

        user = User.query.get(session["user_id"])
        payload = request.json or request.form
        for key, value in payload.items():
            if hasattr(user, key):
                setattr(user, key, value)
        db.session.commit()
        return {"status": "success", "role": user.role}

    user_id = request.args.get("id")
    if not user_id:
        return "Missing id", 400

    user = User.query.get(user_id)
    if not user:
        return "User not found", 404

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "account_balance": user.account_balance,
        "api_key": user.api_key,
    }
