from pathlib import Path

from flask import Flask

from config import Config
from .extensions import db, login_manager


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    from .models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from .routes.auth import auth_bp
    from .routes.dashboard import dashboard_bp, landing_bp
    from .routes.transactions import transactions_bp
    from .routes.import_routes import import_bp
    from .routes.receipt_routes import receipt_bp
    from .routes.investment_routes import investment_bp
    from .routes.analytics_routes import analytics_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(landing_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(import_bp)
    app.register_blueprint(receipt_bp)
    app.register_blueprint(investment_bp)
    app.register_blueprint(analytics_bp)

    from . import commands

    commands.register(app)

    return app
