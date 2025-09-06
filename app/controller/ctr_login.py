from flask import session, flash
from datetime import datetime
from app.models.md_usuarios import UsuarioModel
from app.db.sql import db

def login_user(correo, password):
    usuario = UsuarioModel.query.filter_by(correo=correo).first()

    if not usuario:
        return None, "Usuario no encontrado"

    if usuario.contraseña != password:  
        return None, "Contraseña incorrecta"

    # Guardar último login
    usuario.ultimo_login = datetime.utcnow()
    db.session.commit()

    # Guardar en sesión (pero dejamos que la ruta decida qué guardar)
    return usuario, None


def logout_user():
    session.clear()
    return True