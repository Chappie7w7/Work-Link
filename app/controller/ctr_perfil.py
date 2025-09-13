from app.db.sql import db
from app.models.md_usuarios import UsuarioModel
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError


def get_user_by_id(user_id: int):
    """
    Obtiene un usuario desde la base de datos por su ID.
    Retorna (UsuarioModel, None) si todo va bien,
    o (None, mensaje_error) si hay algún problema.
    """
    try:
        user = UsuarioModel.query.get(user_id)
        if not user:
            return None, "Usuario no encontrado"
        return user, None
    except Exception as e:
        return None, str(e)


def update_user(user_id: int, nombre: str, correo: str, ubicacion: str = None):
    """
    Actualiza los datos básicos del usuario: nombre, correo, ubicación.
    Retorna (UsuarioModel, None) si se actualiza correctamente,
    o (None, mensaje_error) si hay algún problema.
    """
    try:
        user = UsuarioModel.query.get(user_id)
        if not user:
            return None, "Usuario no encontrado"

        if not nombre or not correo:
            return None, "Nombre y correo son obligatorios"

        # Actualizar campos
        user.nombre = nombre
        user.correo = correo
        user.ubicacion = ubicacion

        db.session.commit()
        return user, None
    except IntegrityError:
        db.session.rollback()
        return None, "El correo ya está registrado"
    except Exception as e:
        db.session.rollback()
        return None, str(e)
