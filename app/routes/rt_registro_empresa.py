from flask import Blueprint, render_template, request, flash
from datetime import datetime
from app.db.sql import db
from app.models.md_usuarios import UsuarioModel
from app.models.md_empresas import EmpresaModel
from werkzeug.security import generate_password_hash
import re

rt_registro_empresa = Blueprint('RegistroEmpresaRoute', __name__)

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

    # Validar campos obligatorios
    if not nombre_empresa or not rfc or not sector or not descripcion or not direccion or not telefono or not correo or not password:
        flash("Todos los campos son obligatorios", "error")
        return render_template("login.jinja2", tab="empresa", 
                               nombre_empresa=nombre_empresa,
                               rfc=rfc,
                               sector=sector,
                               descripcion=descripcion,
                               direccion=direccion,
                               telefono=telefono,
                               correo=correo)
        # Crear usuario base
        from werkzeug.security import generate_password_hash
        nuevo_usuario = UsuarioModel(
            nombre=nombre_empresa,  
            correo=correo,
            contraseña=generate_password_hash(password),
            tipo_usuario="empresa"
        )
        db.session.add(nuevo_usuario)
        db.session.commit()

    # Validar nombre de empresa solo letras y espacios
    if not re.fullmatch(r"[A-Za-zÁÉÍÓÚáéíóúÑñ ]{2,100}", nombre_empresa):
        flash("El nombre de la empresa solo puede contener letras y espacios", "error")
        return render_template("login.jinja2", tab="empresa", **request.form)

    # RFC: solo letras y números, 13 caracteres
    if not re.fullmatch(r"[A-Za-z0-9]{13}", rfc):
        flash("El RFC debe contener solo letras y números (13 caracteres)", "error")
        return render_template("login.jinja2", tab="empresa", **request.form)

    # Teléfono: solo números
    if not telefono.isdigit():
        flash("El teléfono solo puede contener números", "error")
        return render_template("login.jinja2", tab="empresa", **request.form)

    # Teléfono: exactamente 10 dígitos
    if len(telefono) != 10:
        flash("El teléfono debe tener exactamente 10 dígitos", "error")
        return render_template("login.jinja2", tab="empresa", **request.form)

    # Correo
    correo_regex = r"^[a-zA-Z0-9._-]+@[a-zA-Z0-9-]+\.(com|org|net|edu|gov|io|co|info)$"
    if not re.fullmatch(correo_regex, correo):
        flash("Correo no tiene formato válido", "error")
        return render_template("login.jinja2", tab="empresa", **request.form)

    # Contraseña
    if len(password) < 6:
        flash("La contraseña debe tener al menos 6 caracteres", "error")
        return render_template("login.jinja2", tab="empresa", **request.form)

    # Validar existencia de correo
    if UsuarioModel.query.filter_by(correo=correo).first():
        flash("El correo ya está registrado", "error")
        return render_template("login.jinja2", tab="empresa", **request.form)

    # Crear usuario
    nuevo_usuario = UsuarioModel(
        nombre=nombre_empresa,
        correo=correo,
        contraseña=generate_password_hash(password),
        tipo_usuario="empresa",
        fecha_registro=datetime.utcnow(),
        ultimo_login=None
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

    flash("Cuenta de empresa creada con éxito", "success")
    return render_template("login.jinja2", tab="empresa")
