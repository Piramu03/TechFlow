from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from pathlib import Path
from flask_migrate import Migrate
import os

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    base = Path(__file__).resolve().parents[1]
    db_path = base / "stockflow.db"
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = "dev-secret"  # change for production

    db.init_app(app)
    migrate.init_app(app, db)  

    from .routes import main
    app.register_blueprint(main)

    # serve static folder if necessary (Flask does by default)

    return app
