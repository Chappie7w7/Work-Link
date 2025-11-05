from flask import session, flash, redirect, url_for
from datetime import datetime
from app.models.md_usuarios import UsuarioModel
from app.models.md_empresas import EmpresaModel
from app.db.sql import db
from app.utils.roles import Roles

def login_user(correo, password):
    # Buscar usuario por correo
    usuario = UsuarioModel.query.filter_by(correo=correo).first()

    if not usuario:
        return None, "Usuario no encontrado"
    
    # Verificar si el usuario es una empresa
    es_empresa = usuario.tipo_usuario == Roles.EMPRESA
    
    # Si es empresa, verificar que esté completamente registrada
    if es_empresa:
        empresa = EmpresaModel.query.get(usuario.id)
        if not empresa:
            return None, "La cuenta de empresa no está completamente configurada. Por favor, contacta al administrador."
    
    # Verificar si el usuario tiene contraseña
    if not usuario.contraseña:
        return None, "Esta cuenta no tiene contraseña configurada. Por favor, usa el inicio de sesión con Google o restablece tu contraseña."

    # Verificar contraseña
    from werkzeug.security import check_password_hash
    if not check_password_hash(usuario.contraseña, password):
        return None, "Contraseña incorrecta"

    # Actualizar último inicio de sesión
    try:
        usuario.ultimo_login = datetime.utcnow()
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error al actualizar último login: {str(e)}")
        # No es crítico, continuamos a pesar del error

    return usuario, None


def logout_user():
    session.clear()
    return True

