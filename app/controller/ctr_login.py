from flask import session, flash, redirect, url_for
from datetime import datetime
from app.models.md_usuarios import UsuarioModel
from app.db.sql import db

def login_user(correo, password):
    usuario = UsuarioModel.query.filter_by(correo=correo).first()

    if usuario and usuario.contraseña == password:
        # Guardar último login
        usuario.ultimo_login = datetime.utcnow()
        db.session.commit()

        # Guardar en sesión
        session['usuario'] = usuario.correo
        session['nombre'] = usuario.nombre
        session['user_id'] = usuario.id

        return True, redirect(url_for("InicioRoute.inicio"))
    
    flash("Usuario o contraseña incorrectos", "error")
    return False, redirect(url_for("LoginRoute.login_form"))

def logout_user():
    session.clear()
    return redirect(url_for("IndexRoute.index"))
