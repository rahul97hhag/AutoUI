import os

from flask import Flask

from config import config_by_name
from app.extensions import db, ma, migrate, cors, jwt
from app.errors import register_error_handlers


def create_app(config_name=None):
    config_name = config_name or os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_by_name[config_name])

    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)
    jwt.init_app(app)

    register_error_handlers(app)

    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix="/api")

    @app.cli.command("seed-db")
    def seed_db_command():
        from scripts.seed_data import seed

        counts = seed()
        print(f"Seeded: {counts}")

    return app
