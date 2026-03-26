from flask import Flask

from app.config import Config
from app.database import db
from app.models import Comment, Transaction, User
from app.routes import admin_bp, api_bp, auth_bp, import_bp, main_bp, payments_bp, upload_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        db.create_all()
        seed_data()

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(import_bp)

    return app


def seed_data():
    if User.query.count() > 0:
        return

    admin = User(
        username="admin",
        email="admin@example.com",
        password="admin123",
        role="admin",
        account_balance=100000,
        api_key="sk-admin-key-12345",
    )
    alice = User(
        username="alice",
        email="alice@example.com",
        password="alice123",
        role="user",
        account_balance=5000,
        api_key="sk-alice-key-67890",
    )
    bob = User(
        username="bob",
        email="bob@example.com",
        password="bob123",
        role="user",
        account_balance=12500,
        api_key="sk-bob-key-99999",
    )

    db.session.add_all([admin, alice, bob])
    db.session.commit()

    sample_tx = [
        Transaction(user_id=1, amount=-100.0, note="Subscription"),
        Transaction(user_id=2, amount=250.0, note="Salary"),
        Transaction(user_id=3, amount=-55.0, note="Book purchase"),
    ]
    db.session.add_all(sample_tx)
    db.session.commit()

    comment = Comment(user_id=1, text="<b>Welcome to the lab</b>")
    db.session.add(comment)
    db.session.commit()


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
