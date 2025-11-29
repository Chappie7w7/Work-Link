from app.db.sql import db
from app.models.md_usuarios import UsuarioModel
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import os
import re


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

        # Validación: solo letras (incluye acentos) y espacios
        if not re.fullmatch(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ ]{2,50}", nombre):
            return None, "El nombre solo debe contener letras y espacios"

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


def update_user_with_photo(user_id: int, nombre: str, correo: str, foto_perfil_file=None):
    """
    Actualiza los datos del usuario incluyendo foto de perfil.
    Retorna (UsuarioModel, None) si se actualiza correctamente,
    o (None, mensaje_error) si hay algún problema.
    """
    try:
        user = UsuarioModel.query.get(user_id)
        if not user:
            return None, "Usuario no encontrado"

        if not nombre or not correo:
            return None, "Nombre y correo son obligatorios"

        # Validación: solo letras (incluye acentos) y espacios
        if not re.fullmatch(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ ]{2,50}", nombre):
            return None, "El nombre solo debe contener letras y espacios"

        # Actualizar campos básicos
        user.nombre = nombre
        user.correo = correo

        # Manejar subida de foto de perfil
        if foto_perfil_file and foto_perfil_file.filename:
            # Verificar extensión permitida
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
            filename = foto_perfil_file.filename
            if '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions:
                # Crear directorio si no existe
                upload_dir = os.path.join("app", "static", "uploads", "profile_pics")
                os.makedirs(upload_dir, exist_ok=True)
                
                # Generar nombre único para el archivo
                extension = filename.rsplit('.', 1)[1].lower()
                secure_name = secure_filename(f"{user_id}_{nombre}_{filename}")
                # Asegurar nombre único
                timestamp = str(int(datetime.now().timestamp()))
                unique_filename = f"{user_id}_{timestamp}.{extension}"
                filepath = os.path.join(upload_dir, unique_filename)
                
                # Guardar archivo
                foto_perfil_file.save(filepath)
                
                # Eliminar foto anterior si existe
                if user.foto_perfil:
                    old_filepath = os.path.join("app", "static", user.foto_perfil.lstrip('/'))
                    if os.path.exists(old_filepath):
                        try:
                            os.remove(old_filepath)
                        except:
                            pass
                
                # Guardar URL relativa en la base de datos (sin usar url_for ya que estamos en el controlador)
                user.foto_perfil = f"/static/uploads/profile_pics/{unique_filename}"
            else:
                return None, "Formato de imagen no permitido. Use: PNG, JPG, JPEG, GIF o WEBP"

        db.session.commit()
        return user, None
    except IntegrityError:
        db.session.rollback()
        return None, "El correo ya está registrado"
    except Exception as e:
        db.session.rollback()
        return None, str(e)
