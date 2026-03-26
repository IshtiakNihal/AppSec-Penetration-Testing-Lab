import os


class Config:
    SECRET_KEY = os.getenv("APP_SECRET_KEY", "change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://appsec_user:appsec_pass@db:5432/appsec_lab",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
    JWT_SECRET = os.getenv("JWT_SECRET", "change-me")
