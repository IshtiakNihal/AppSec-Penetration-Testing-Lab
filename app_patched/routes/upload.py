import os
import uuid

from flask import Blueprint, current_app, redirect, render_template, request, send_from_directory
from werkzeug.utils import secure_filename

from app_patched.database import db
from app_patched.models import FileRecord

upload_bp = Blueprint("upload", __name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "pdf"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@upload_bp.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if "file" not in request.files:
            return "No file part", 400

        file = request.files["file"]
        filename = secure_filename(file.filename)
        if not allowed_file(filename):
            return "Invalid file type", 400

        upload_dir = current_app.config["UPLOAD_FOLDER"]
        os.makedirs(upload_dir, exist_ok=True)
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        file_path = os.path.join(upload_dir, unique_name)
        file.save(file_path)

        record = FileRecord(user_id=None, filename=unique_name, path=file_path)
        db.session.add(record)
        db.session.commit()

        return f"File uploaded: {unique_name}"

    return render_template("upload.html")


@upload_bp.route("/uploads/<path:filename>")
def serve_upload(filename):
    upload_dir = current_app.config["UPLOAD_FOLDER"]
    return send_from_directory(upload_dir, filename)


@upload_bp.route("/download")
def download():
    filename = request.args.get("file", "")
    upload_dir = current_app.config["UPLOAD_FOLDER"]
    safe_name = os.path.basename(filename)
    file_path = os.path.join(upload_dir, safe_name)
    if os.path.exists(file_path):
        return send_from_directory(upload_dir, safe_name, as_attachment=True)
    return "File not found", 404
