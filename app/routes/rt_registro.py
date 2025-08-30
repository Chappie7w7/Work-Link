from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from app.db.sql import db
from app.models.md_usuarios import UsuarioModel

rt_registro = Blueprint('RegistroRoute', __name__)

@rt_registro.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form['nombre']
        correo = request.form['correo']
        password = request.form['password']
        confirmar = request.form['confirmar']

        # Validar contraseñas
        if password != confirmar:
            flash("Las contraseñas no coinciden", "error")
            return redirect(url_for('IndexRoute.index'))

        # Validar que no exista un usuario con ese correo
        existente = UsuarioModel.query.filter_by(correo=correo).first()
        if existente:
            flash("El correo ya está registrado", "error")
            return redirect(url_for('IndexRoute.index'))

        # Crear usuario
        nuevo_usuario = UsuarioModel(
            nombre=nombre,
            correo=correo,
            contraseña=password,   
            fecha_registro=datetime.utcnow(),
            ultimo_login=None,
            tipo_usuario="empleado"
        )

        db.session.add(nuevo_usuario)
        db.session.commit()

        flash("Cuenta creada con éxito", "success")
        return redirect(url_for('IndexRoute.index'))

    return render_template("registro.jinja2")
