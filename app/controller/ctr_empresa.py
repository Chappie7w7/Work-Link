from app.db.sql import db
from app.models.md_empresas import EmpresaModel
from app.models.md_usuarios import UsuarioModel
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import os


def get_empresa_by_id(empresa_id: int):
    """
    Obtiene una empresa desde la base de datos por su ID.
    Retorna (EmpresaModel, None) si todo va bien,
    o (None, mensaje_error) si hay algún problema.
    """
    try:
        empresa = EmpresaModel.query.get(empresa_id)
        if not empresa:
            return None, "Empresa no encontrada"
        return empresa, None
    except Exception as e:
        return None, str(e)


def update_empresa(empresa_id: int, nombre_empresa: str, sector: str = None, 
                  descripcion: str = None, direccion: str = None, 
                  telefono: str = None, correo: str = None, logo_file=None):
    """
    Actualiza los datos básicos de la empresa incluyendo logo.
    Retorna (EmpresaModel, None) si se actualiza correctamente,
    o (None, mensaje_error) si hay algún problema.
    """
    try:
        empresa = EmpresaModel.query.get(empresa_id)
        if not empresa:
            return None, "Empresa no encontrada"

        if not nombre_empresa:
            return None, "El nombre de la empresa es obligatorio"

        # Actualizar campos de empresa
        empresa.nombre_empresa = nombre_empresa
        empresa.sector = sector
        empresa.descripcion = descripcion
        empresa.direccion = direccion
        empresa.telefono = telefono

        # Actualizar correo del usuario si se proporciona
        if correo:
            usuario = UsuarioModel.query.get(empresa_id)
            if usuario:
                usuario.correo = correo

        # Manejar subida de logo
        if logo_file and logo_file.filename:
            # Verificar extensión permitida
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
            filename = logo_file.filename
            if '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions:
                # Crear directorio si no existe
                upload_dir = os.path.join("app", "static", "uploads", "company_logos")
                os.makedirs(upload_dir, exist_ok=True)
                
                # Generar nombre único para el archivo
                extension = filename.rsplit('.', 1)[1].lower()
                timestamp = str(int(datetime.now().timestamp()))
                unique_filename = f"empresa_{empresa_id}_{timestamp}.{extension}"
                filepath = os.path.join(upload_dir, unique_filename)
                
                # Guardar archivo
                logo_file.save(filepath)
                
                # Eliminar logo anterior si existe
                if empresa.logo_url:
                    old_filepath = os.path.join("app", "static", empresa.logo_url.lstrip('/'))
                    if os.path.exists(old_filepath):
                        try:
                            os.remove(old_filepath)
                        except:
                            pass
                
                # Guardar URL relativa en la base de datos
                empresa.logo_url = f"/static/uploads/company_logos/{unique_filename}"
            else:
                return None, "Formato de imagen no permitido. Use: PNG, JPG, JPEG, GIF o WEBP"

        db.session.commit()
        return empresa, None
    except IntegrityError:
        db.session.rollback()
        return None, "El correo ya está registrado"
    except Exception as e:
        db.session.rollback()
        return None, str(e)

