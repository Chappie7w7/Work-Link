from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.models.md_usuarios import UsuarioModel
from app.db.sql import db
from app.utils.decorators import login_role_required
from app.utils.roles import Roles  
from werkzeug.security import generate_password_hash

usuarios_bp = Blueprint('UsuariosRoute', __name__, url_prefix='/usuarios')


class UsuariosRoute:
    INDEX = "UsuariosRoute.index"
    CREATE = "UsuariosRoute.get_crear"


@usuarios_bp.get('/')
@login_role_required(Roles.SUPERADMIN)
def index(current_user):
    usuarios = UsuarioModel.query.all()
    return render_template('usuarios/index.jinja2', usuarios=usuarios, current_user=current_user)


@usuarios_bp.get("/crear")
@login_role_required(Roles.SUPERADMIN)
def get_crear(current_user):
    return render_template("usuarios/formulario.jinja2", current_user=current_user)


@usuarios_bp.post("/crear")
@login_role_required(Roles.SUPERADMIN)
def post_crear(current_user):
    data = request.form
    nombre = data.get("nombre")
    correo = data.get("correo")
    contraseña = data.get("contraseña")
    tipo_usuario = data.get("tipo_usuario")  # empleado o empresa

    # Validar que no exista usuario
    if UsuarioModel.query.filter_by(correo=correo).first():
        flash("El correo ya está registrado", "error")
        return redirect(url_for(UsuariosRoute.CREATE))

    nuevo_usuario = UsuarioModel(
        nombre=nombre,
        correo=correo,
        contraseña=generate_password_hash(contraseña),
        tipo_usuario=tipo_usuario
    )
    db.session.add(nuevo_usuario)
    db.session.commit()

    flash("Usuario creado correctamente", "success")
    return redirect(url_for(UsuariosRoute.INDEX))
