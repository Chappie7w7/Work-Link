from app.models.md_usuarios import UsuarioModel
from app.db.sql import db

def first_user():
    """Crea un usuario admin por defecto si no existe"""
    if not UsuarioModel.query.filter_by(correo="admin@worklink.com").first():
        admin = UsuarioModel(
            nombre="Admin",
            correo="adminAle@worklink.com",
            contraseña="admin123",  
            tipo_usuario="admin"
        )
        db.session.add(admin)
        db.session.commit()
