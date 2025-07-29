from flask import Flask
from flask_migrate import Migrate
from app.config import Config
from app.db.sql import db, migrate
from .utils.first_user import first_user  # 👈 import correcto

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    # registrar blueprints y rutas cuando se tenga
    # from app.routes import main_bp
    # app.register_blueprint(main_bp)
    
    from app.routes import index_bp
    app.register_blueprint(index_bp)


    with app.app_context():
        db.create_all()
        first_user()  

    return app
