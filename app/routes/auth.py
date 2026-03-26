from datetime import datetime, timedelta

from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for
from sqlalchemy import text
import jwt

from app.config import Config
from app.database import db
from app.models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        query = (
            "SELECT * FROM users WHERE username='{}' AND password='{}'".format(
                username, password
            )
        )

        try:
            user = db.session.execute(text(query)).fetchone()
            if user:
                session["user_id"] = user[0]
                return redirect(url_for("main.dashboard"))
        except Exception as exc:
            return f"Database Error: {exc}", 500

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
            key="",
            algorithm="none",
        )
        return jsonify({"token": token})

    return jsonify({"error": "Invalid credentials"}), 401


@auth_bp.route("/api/login", methods=["POST"])
def api_login():
    username = request.json.get("username")
    password = request.json.get("password")

    user = User.query.filter_by(username=username).first()
    if user and user.password == password:
        return jsonify({"token": "valid_token_here"})

    return jsonify({"error": "Invalid credentials"}), 401
