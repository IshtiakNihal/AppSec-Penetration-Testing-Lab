import secrets
from datetime import datetime, timedelta

from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for
import jwt

from app_patched.config import Config
from app_patched.database import db
from app_patched.models import User

auth_bp = Blueprint("auth", __name__)


RATE_LIMIT = {}


def allow_request(ip: str) -> bool:
    window = RATE_LIMIT.setdefault(ip, [])
    now = datetime.utcnow()
    window[:] = [t for t in window if (now - t).seconds < 60]
    if len(window) >= 5:
        return False
    window.append(now)
    return True


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        ip = request.remote_addr or "unknown"
        if not allow_request(ip):
            return "Too many attempts", 429

        username = request.form.get("username", "")
        password = request.form.get("password", "")

        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session["user_id"] = user.id
            session["csrf_token"] = secrets.token_hex(16)
            return redirect(url_for("main.dashboard"))
        return "Invalid credentials", 401

    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        if User.query.filter_by(username=username).first():
            return "Username already exists", 400

        user = User(
            username=username,
            email=email,
            password=password,
            role="user",
            api_key=f"sk-{username}-key",
        )
        db.session.add(user)
        db.session.commit()

        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.index"))


@auth_bp.route("/api/auth/token", methods=["POST"])
def get_token():
    username = request.json.get("username")
    password = request.json.get("password")

    user = User.query.filter_by(username=username).first()
    if user and user.password == password:
        token = jwt.encode(
            {
                "sub": username,
                "role": user.role,
                "exp": datetime.utcnow() + timedelta(hours=24),
            },
            key=Config.JWT_SECRET,
            algorithm="HS256",
        )
        return jsonify({"token": token})

    return jsonify({"error": "Invalid credentials"}), 401
