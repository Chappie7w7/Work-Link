from app.db.sql import db
from app.models.md_usuarios import UsuarioModel
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.roles import Roles
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


def dar_baja_usuario(usuario_id: int):
    """Da de baja a un usuario (elimina su cuenta)"""
    try:
        usuario = UsuarioModel.query.get(usuario_id)
        if not usuario:
            return None, "Usuario no encontrado"
        
        # No permitir que el admin se dé de baja a sí mismo
        if usuario.tipo_usuario == Roles.SUPERADMIN:
            return None, "No se puede dar de baja a un administrador"
        
        # Eliminar relaciones primero si existen
        from app.models.md_empresas import EmpresaModel
        from app.models.md_empleados import EmpleadoModel
        
        # Si es empresa, eliminar registro de empresa
        if usuario.tipo_usuario == Roles.EMPRESA:
            empresa = EmpresaModel.query.get(usuario_id)
            if empresa:
                db.session.delete(empresa)
        
        # Si es empleado, eliminar registro de empleado
        if usuario.tipo_usuario == Roles.EMPLEADO:
            empleado = EmpleadoModel.query.get(usuario_id)
            if empleado:
                db.session.delete(empleado)
        
        # Eliminar el usuario
        db.session.delete(usuario)
        db.session.commit()
        return True, None
    except Exception as e:
        db.session.rollback()
        return None, str(e)


def eliminar_usuario(usuario_id: int):
    """Elimina completamente un usuario de la base de datos"""
    try:
        usuario = UsuarioModel.query.get(usuario_id)
        if not usuario:
            return None, "Usuario no encontrado"
        
        # No permitir que el admin se elimine a sí mismo
        if usuario.tipo_usuario == Roles.SUPERADMIN:
            return None, "No se puede eliminar a un administrador"
        
        # Eliminar relaciones primero si existen
        from app.models.md_empresas import EmpresaModel
        from app.models.md_empleados import EmpleadoModel
        
        # Si es empresa, eliminar registro de empresa
        if usuario.tipo_usuario == Roles.EMPRESA:
            empresa = EmpresaModel.query.get(usuario_id)
            if empresa:
                db.session.delete(empresa)
        
        # Si es empleado, eliminar registro de empleado
        if usuario.tipo_usuario == Roles.EMPLEADO:
            empleado = EmpleadoModel.query.get(usuario_id)
            if empleado:
                db.session.delete(empleado)
        
        # Eliminar el usuario
        db.session.delete(usuario)
        db.session.commit()
        return True, None
    except Exception as e:
        db.session.rollback()
        return None, str(e)


def get_all_usuarios():
    """Obtiene todos los usuarios excepto superadmins"""
    try:
        usuarios = UsuarioModel.query.filter(
            UsuarioModel.tipo_usuario != Roles.SUPERADMIN
        ).all()
        return usuarios, None
    except Exception as e:
        return None, str(e)
