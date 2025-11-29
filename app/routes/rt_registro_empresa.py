from flask import Blueprint, render_template, request, flash, redirect, url_for
from datetime import datetime
from app.db.sql import db
from app.models.md_usuarios import UsuarioModel
from app.models.md_empresas import EmpresaModel
from werkzeug.security import generate_password_hash
import re

rt_registro_empresa = Blueprint('RegistroEmpresaRoute', __name__)

# ------------------------------------------------------
# VALIDACIÓN AVANZADA RFC (FORMATO SAT + FECHA REAL)
# ------------------------------------------------------
def validar_rfc(rfc: str) -> bool:
    """
    Valida RFC de Persona Física y Moral incluyendo:
    - estructura oficial SAT
    - validación de fecha real (YY-MM-DD)
    """
    rfc = rfc.upper().strip()

    # Expresión oficial SAT (Personas Físicas y Morales)
    patron = r"^([A-ZÑ&]{3,4})(\d{2})(\d{2})(\d{2})([A-Z\d]{3})$"
    match = re.match(patron, rfc)

    if not match:
        return False

    letras, yy, mm, dd, homoclave = match.groups()

    # Validar fecha interna
    try:
        year = int(yy)
        # RFC usa regla: >=30 es 1900, <30 es 2000
        year += 1900 if year >= 30 else 2000

        month = int(mm)
        day = int(dd)

        datetime(year, month, day)  # Error = fecha inválida
    except ValueError:
        return False

    return True

@rt_registro_empresa.route("/registro/empresa", methods=["POST"])
def registro_empresa():
    nombre_empresa = request.form.get('nombre_empresa', '').strip()
    rfc = request.form.get('rfc', '').strip()
    sector = request.form.get('sector', '').strip()
    descripcion = request.form.get('descripcion', '').strip()
    direccion = request.form.get('direccion', '').strip()
    telefono = request.form.get('telefono', '').strip()
    correo = request.form.get('email', '').strip()
    password = request.form.get('password', '').strip()

     # ------------------------------------------------------
    # Validación avanzada de RFC
    # ------------------------------------------------------
    if not validar_rfc(rfc):
        flash("El RFC no es válido. Verifica que cumpla la estructura del SAT y contenga una fecha real.", "danger")
        return redirect(url_for("LoginRoute.form_empresa"))

        # ------------------------------------------------------
    # Validar si el correo ya existe
    # ------------------------------------------------------
    if UsuarioModel.query.filter_by(correo=correo).first():
        flash("Este correo ya está registrado. Usa otro o recupera tu cuenta.", "warning")
        return redirect(url_for("LoginRoute.form_empresa"))

    # Crear usuario base
    nuevo_usuario = UsuarioModel(
        nombre=nombre_empresa,
        correo=correo,
        contraseña=generate_password_hash(password),
        tipo_usuario="empresa",
        fecha_registro=datetime.utcnow(),
        ultimo_login=None,
        aprobado=False
    )
    db.session.add(nuevo_usuario)
    db.session.commit()

    # Crear registro en tabla empresas
    nueva_empresa = EmpresaModel(
        id=nuevo_usuario.id,
        nombre_empresa=nombre_empresa,
        rfc=rfc,
        sector=sector,
        descripcion=descripcion,
        direccion=direccion,
        telefono=telefono
    )
    db.session.add(nueva_empresa)
    db.session.commit()

    flash("Cuenta de empresa creada con éxito. Un administrador debe aprobar tu cuenta antes de poder iniciar sesión.", "success")
    return redirect(url_for("LoginRoute.login_form"))

@rt_registro_empresa.route("/verificar_correo", methods=["POST"])
def verificar_correo():
    correo = request.json.get("email", "").strip()
    existe = UsuarioModel.query.filter_by(correo=correo).first() is not None
    return {"existe": existe}