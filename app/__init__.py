from flask import Flask
from flask_migrate import Migrate
from app.config import Config
from app.db.sql import db, migrate
from .utils.first_user import first_user
from app.routes import register_routes  # 👈 Importa la función que registra todo

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    # Registrar TODAS las rutas
    register_routes(app)

    with app.app_context():
        db.create_all()
        first_user()  

    return app
