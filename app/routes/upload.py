import os

from flask import Blueprint, current_app, redirect, render_template, request, send_file, send_from_directory

from app.database import db
from app.models import FileRecord

upload_bp = Blueprint("upload", __name__)


@upload_bp.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if "file" not in request.files:
            return "No file part", 400

        file = request.files["file"]
        filename = file.filename
        upload_dir = current_app.config["UPLOAD_FOLDER"]
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)

        record = FileRecord(user_id=None, filename=filename, path=file_path)
        db.session.add(record)
        db.session.commit()

        return f"File uploaded: {filename}"

    return render_template("upload.html")


@upload_bp.route("/uploads/<path:filename>")
def serve_upload(filename):
    upload_dir = current_app.config["UPLOAD_FOLDER"]
    return send_from_directory(upload_dir, filename)


@upload_bp.route("/download")
def download():
    filename = request.args.get("file", "")
    upload_dir = current_app.config["UPLOAD_FOLDER"]
    file_path = os.path.join(upload_dir, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return "File not found", 404
