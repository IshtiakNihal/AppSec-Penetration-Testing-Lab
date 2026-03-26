from flask import Blueprint, redirect, render_template, request, session, url_for

from app.database import db
from app.models import Comment

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin")
def admin_panel():
    comments = Comment.query.order_by(Comment.created_at.desc()).all()
    return render_template("admin.html", comments=comments)


@admin_bp.route("/api/admin/comments", methods=["POST"])
def add_comment():
    if "user_id" not in session:
        return "Unauthorized", 401

    text = request.form.get("text", "")
    comment = Comment(user_id=session["user_id"], text=text)
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for("admin.admin_panel"))
