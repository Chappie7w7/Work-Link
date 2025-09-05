from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from app.db.sql import db
from app.models.md_usuarios import UsuarioModel

from app.models.md_empresas import EmpresaModel

rt_registro_empresa = Blueprint('RegistroEmpresaRoute', __name__)

@rt_registro_empresa.route("/registro/empresa", methods=["GET", "POST"])
def registro_empresa():
    if request.method == "POST":
        nombre_empresa = request.form['nombre_empresa']
        rfc = request.form['rfc']
        sector = request.form['sector']
        descripcion = request.form['descripcion']
        direccion = request.form['direccion']
        telefono = request.form['telefono']
        correo = request.form['email']
        password = request.form['password']

        # Validar que no exista usuario
        existente = UsuarioModel.query.filter_by(correo=correo).first()
        if existente:
            flash("El correo ya está registrado", "error")
            return redirect(url_for('RegistroEmpresaRoute.registro_empresa'))

        # Crear usuario base
        nuevo_usuario = UsuarioModel(
            nombre=nombre_empresa,  
            correo=correo,
            contraseña=password,
            tipo_usuario="empresa"
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
        return redirect(url_for('IndexRoute.index'))

    return render_template("empresa/registro_empresa.jinja2")
