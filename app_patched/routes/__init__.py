from .main import main_bp
from .auth import auth_bp
from .api import api_bp
from .upload import upload_bp
from .payments import payments_bp
from .import_data import import_bp

__all__ = [
    "main_bp",
    "auth_bp",
    "api_bp",
    "upload_bp",
    "payments_bp",
    "import_bp",
]
