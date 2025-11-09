from flask import Flask, session
from flask_migrate import Migrate
from app.config import Config
from app.db.sql import db, migrate
from .utils.first_user import first_user
from app.routes import register_routes
from app.extensiones import init_extensiones

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    
    # Inicializar extensiones (Flask-Mail, SocketIO, etc.)
    init_extensiones(app)
    
    # Registrar eventos de Socket.IO (después de inicializar extensiones)
    from app.extensiones import socketio
    from app.socketio_events import register_socketio_events
    register_socketio_events(socketio)

    # Context processor para variables globales en templates
    @app.context_processor
    def inject_mensajes_no_leidos():
        """Inyecta el contador de mensajes no leídos en todas las plantillas"""
        usuario = session.get('usuario')
        if usuario:
            from app.utils.mensaje_helper import contar_mensajes_no_leidos
            return {'mensajes_no_leidos': contar_mensajes_no_leidos(usuario['id'])}
        return {'mensajes_no_leidos': 0}

    # Registrar TODAS las rutas
    register_routes(app)

    with app.app_context():
        db.create_all()
        first_user()  

        return app
