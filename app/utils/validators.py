import re
import bleach
from email_validator import validate_email, EmailNotValidError

def validar_nombre(nombre: str):
    if not nombre:
        return False, "El nombre es obligatorio"
    if not re.fullmatch(r"[A-Za-zÁÉÍÓÚáéíóúÑñ ]{2,50}", nombre):
        return False, "El nombre solo puede contener letras y espacios"
    # Limpiar código malicioso
    nombre = bleach.clean(nombre, tags=[], strip=True)
    return True, nombre

def validar_correo(correo: str):
    if not correo:
        return False, "El correo es obligatorio"

    try:
        # Validación estricta del correo
        resultado = validate_email(correo)
        correo_normalizado = resultado.email  # convierte a minúsculas y normaliza
        # Limpiar posibles códigos maliciosos
        correo_normalizado = bleach.clean(correo_normalizado, tags=[], strip=True)
        return True, correo_normalizado
    except EmailNotValidError as e:
        return False, str(e)  # devuelve mensaje de error descriptivo

def validar_password(password: str, confirmar: str, min_length: int = 6):
    if not password:
        return False, "La contraseña es obligatoria"
    if len(password) < min_length:
        return False, f"La contraseña debe tener al menos {min_length} caracteres"
    if password != confirmar:
        return False, "Las contraseñas no coinciden"
    return True, None

def validar_rfc(rfc: str):
    if not rfc:
        return False, "El RFC es obligatorio"  
    rfc = rfc.strip().upper()
    # patrón simple para RFC (persona moral y física no exhaustivo)
    if not re.fullmatch(r"[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}", rfc):
        return False, "RFC no válido"
    return True, rfc

def validar_telefono(telefono: str):
    if not telefono:
        return False, "El teléfono es obligatorio"   
    tel = re.sub(r"[^\d]", "", telefono)
    if not 7 <= len(tel) <= 15:
        return False, "Teléfono no válido"
    return True, tel

def validar_sector(sector: str):
    if not sector:
        return False, "El sector es obligatorio"
    if not re.fullmatch(r"[A-Za-zÁÉÍÓÚáéíóúÑñ ]{2,100}", sector):
        return False, "El sector solo puede contener letras y espacios (2-100)"
    return True, bleach.clean(sector, tags=[], strip=True)


def validar_descripcion(descripcion: str):
    if not descripcion:
        return False, "La descripción es obligatoria"
    if len(descripcion) < 10:
        return False, "La descripción debe tener al menos 10 caracteres"
    return True, bleach.clean(descripcion, tags=[], strip=True)