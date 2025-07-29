from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models.md_usuarios import UsuarioModel
from app.db.sql import db


index_bp = Blueprint('IndexRoute', __name__)

# Página de login
@index_bp.route('/', methods=['GET'])
def index():
    return render_template('index.jinja2')


# Procesar el login
@index_bp.route('/', methods=['POST'])
def login():
    correo = request.form.get('correo', '').strip()
    password = request.form.get('password', '').strip()

    # Buscar usuario en la base de datos por correo
    usuario = UsuarioModel.query.filter_by(correo=correo).first()

    # Validar que exista y contraseña sea correcta (en texto plano por ahora)
    if usuario and usuario.contraseña == password:
        session['usuario'] = usuario.correo
        session['nombre'] = usuario.nombre
        return redirect(url_for('IndexRoute.bienvenida'))
    
    flash('Usuario o contraseña incorrectos', 'error')
    return redirect(url_for('IndexRoute.index'))

# Página de bienvenida
@index_bp.route('/bienvenida')
def bienvenida():
    usuario = session.get('usuario')
    if not usuario:
        return redirect(url_for('IndexRoute.index'))
    return render_template('bienvenida.jinja2', usuario=usuario)


# Cerrar sesión
@index_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('IndexRoute.index'))
