from flask import Blueprint, render_template, request, flash, redirect, url_for
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

    # Crear usuario base
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

    flash("Cuenta de empresa creada con éxito. Por favor inicia sesión.", "success")
    return redirect(url_for("LoginRoute.login_form"))

@rt_registro_empresa.route("/verificar_correo", methods=["POST"])
def verificar_correo():
    correo = request.json.get("email", "").strip()
    existe = UsuarioModel.query.filter_by(correo=correo).first() is not None
    return {"existe": existe}
