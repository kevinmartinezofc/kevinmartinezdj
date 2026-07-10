from flask import Flask

from config import Config
from app.extensions import db, bcrypt, login_manager


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Erweiterungen initialisieren
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # Blueprints registrieren
    from app.auth.routes import auth_bp
    from app.main.routes import main_bp
    from app.booking.routes import booking_bp
    from app.api.routes import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(booking_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    with app.app_context():
        db.create_all()

    return app
