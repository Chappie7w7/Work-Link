from app.db.sql import db
from app.models.md_usuarios import UsuarioModel
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils import Roles
from sqlalchemy.exc import IntegrityError


def add_usuario(nombre: str, correo: str, contraseña: str, tipo_usuario: str):
    try:
        if not nombre or not correo or not contraseña or not tipo_usuario:
            raise Exception("Todos los campos son obligatorios")

        if tipo_usuario not in Roles.get_roles():
            raise Exception("Tipo de usuario no válido")

        nuevo_usuario = UsuarioModel(
            nombre=nombre,
            correo=correo,
            contraseña=generate_password_hash(contraseña),
            tipo_usuario=tipo_usuario
        )
        db.session.add(nuevo_usuario)
        db.session.commit()
        return nuevo_usuario.id, None

    except IntegrityError:
        return None, "El correo ya está registrado"
    except Exception as e:
        return None, str(e)


def check_user(correo, contraseña):
    try:
        user = UsuarioModel.query.filter_by(correo=correo).first()
        if not user:
            return None, "Correo o contraseña inválidos"

        if not check_password_hash(user.contraseña, contraseña):
            return None, "Contraseña incorrecta"

        return user, None
    except Exception as e:
        return None, str(e)
