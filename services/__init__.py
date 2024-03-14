from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__, instance_relative_config=False)
app.url_map.strict_slashes = False
app.config.from_object('config.config.Config')
db = SQLAlchemy()


def create_app():
    """Construct the core application."""
    db.init_app(app)

    with app.app_context():
        # Imports
        from services.models import models
        from services.payload import UserDetails,Role
        # Initialize Global db
        db.create_all()
        return app
