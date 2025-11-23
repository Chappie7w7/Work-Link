from flask import Blueprint, render_template, request, flash, redirect, url_for
from datetime import datetime
from app.db.sql import db
from app.models.md_usuarios import UsuarioModel
from app.models.md_empleados import EmpleadoModel
from werkzeug.security import generate_password_hash
import re

rt_registro = Blueprint('RegistroRoute', __name__)

@rt_registro.route("/registro", methods=["POST"])
def registro():
    nombre = request.form.get('nombre', '').strip()
    correo = request.form.get('correo', '').strip()
    password = request.form.get('password', '').strip()
    confirmar = request.form.get('confirmar', '').strip()

    # Crear usuario
    nuevo_usuario = UsuarioModel(
        nombre=nombre,
        correo=correo,
        contraseña=generate_password_hash(password),
        fecha_registro=datetime.utcnow(),
        ultimo_login=None,
        tipo_usuario="empleado",
        aprobado=False
    )
    db.session.add(nuevo_usuario)
    db.session.flush()  # Para obtener el ID del usuario recién creado
    
    # Crear perfil de empleado automáticamente
    if nuevo_usuario.tipo_usuario == 'empleado':
        empleado = EmpleadoModel(id=nuevo_usuario.id)
        db.session.add(empleado)
    
    db.session.commit()

    flash("Cuenta creada con éxito. Un administrador debe aprobar tu cuenta antes de poder iniciar sesión.", "success")
    return redirect(url_for("LoginRoute.login_form"))

@rt_registro.route("/verificar_correo", methods=["POST"])
def verificar_correo():
    correo = request.json.get("correo", "").strip()
    existe = UsuarioModel.query.filter_by(correo=correo).first() is not None
    return {"existe": existe}
