from flask import Blueprint, render_template, request, flash
from datetime import datetime
from app.db.sql import db
from app.models.md_usuarios import UsuarioModel
from werkzeug.security import generate_password_hash
import re

rt_registro = Blueprint('RegistroRoute', __name__)

@rt_registro.route("/registro", methods=["POST"])
def registro():
    nombre = request.form.get('nombre', '').strip()
    correo = request.form.get('correo', '').strip()
    password = request.form.get('password', '').strip()
    confirmar = request.form.get('confirmar', '').strip()

    # Validar campos
    if not nombre or not correo or not password or not confirmar:
        flash("Todos los campos son obligatorios", "error")
        return render_template("registro.jinja2", tab="empleado", nombre=nombre, correo=correo)
    
    # Validar nombre
    if not re.fullmatch(r"[A-Za-zÁÉÍÓÚáéíóúÑñ ]{2,50}", nombre):
        flash("El nombre solo puede contener letras y espacios", "error")
        return render_template("registro.jinja2", tab="empleado", nombre=nombre, correo=correo)

    # Validar correo
    correo_regex = r"^[a-zA-Z0-9._-]+@[a-zA-Z0-9-]+\.(com|org|net|edu|gov|io|co|info)$"
    if not re.fullmatch(correo_regex, correo):
        flash("Correo no tiene formato válido", "error")
        return render_template("registro.jinja2", tab="empleado", nombre=nombre, correo=correo)

    # Validar contraseña
    if len(password) < 6:
        flash("La contraseña debe tener al menos 6 caracteres", "error")
        return render_template("registro.jinja2", tab="empleado", nombre=nombre, correo=correo)

    if password != confirmar:
        flash("Las contraseñas no coinciden", "error")
        return render_template("registro.jinja2", tab="empleado", nombre=nombre, correo=correo)

    # Validar existencia de correo
    if UsuarioModel.query.filter_by(correo=correo).first():
        flash("El correo ya está registrado", "error")
        return render_template("registro.jinja2", tab="empleado", nombre=nombre, correo=correo)

    # Crear usuario
    nuevo_usuario = UsuarioModel(
        nombre=nombre,
        correo=correo,
        contraseña=generate_password_hash(password),
        fecha_registro=datetime.utcnow(),
        ultimo_login=None,
        tipo_usuario="empleado"
    )
    db.session.add(nuevo_usuario)
    db.session.commit()

    flash("Cuenta creada con éxito", "success")
    return render_template("login.jinja2", tab="empleado")
