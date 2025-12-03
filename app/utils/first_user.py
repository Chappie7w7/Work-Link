from werkzeug.security import generate_password_hash
from app.models.md_usuarios import UsuarioModel
from app.db.sql import db
from app.utils.roles import Roles 

def first_user():
    """Crea un super admin si no existe"""
    if not UsuarioModel.query.filter_by(correo="worklinkOco@gmail.com").first():
        admin = UsuarioModel(
            nombre="Admin",
            correo="worklinkOco@gmail.com",
            contraseña= generate_password_hash("admin123"),
            tipo_usuario=Roles.SUPERADMIN
        )
        db.session.add(admin)
        db.session.commit()
