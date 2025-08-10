from types import SimpleNamespace
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models.md_usuarios import UsuarioModel
from app.db.sql import db
from flask_login import login_required, current_user


index_bp = Blueprint('IndexRoute', __name__)


@index_bp.route('/')
def index():
    usuario_session = session.get("usuario")

    if isinstance(usuario_session, dict):
        current_user = SimpleNamespace(**usuario_session)
    else:
        current_user = None

    # Lista de trabajos de ejemplo (puedes luego cargarlos desde la BD)
    jobs = [
        {"title": "Desarrollador Web", "company": "Tech Solutions", "location": "Ocosingo, Chiapas"},
        {"title": "Diseñador Gráfico", "company": "Creativa Studio", "location": "San Cristóbal de las Casas"},
        {"title": "Vendedor de Campo", "company": "Ventas MX", "location": "Palenque, Chiapas"},
        {"title": "Recepcionista", "company": "Hotel Paraíso", "location": "Ocosingo, Chiapas"},
    ]

    return render_template('index.jinja2', current_user=current_user, jobs=jobs)


# Mostrar formulario de login
@index_bp.route('/login')
def login_form():
    return render_template('login.jinja2')

# Procesar el login
@index_bp.route('/login', methods=['POST'])
def login():
    correo = request.form.get('correo', '').strip()
    password = request.form.get('password', '').strip()

    # Buscar usuario en la base de datos por correo
    usuario = UsuarioModel.query.filter_by(correo=correo).first()

    # Validar que exista y contraseña sea correcta (en texto plano por ahora)
    if usuario and usuario.contraseña == password:
        session['usuario'] = usuario.correo
        session['nombre'] = usuario.nombre
        return redirect(url_for('IndexRoute.inicio'))
    
    flash('Usuario o contraseña incorrectos', 'error')
    return redirect(url_for('IndexRoute.login'))

# Página de inicio
@index_bp.route('/inicio')
def inicio():
    usuario = session.get('usuario')
    if not usuario:
        return redirect(url_for('IndexRoute.index'))
    return render_template('inicio.jinja2', usuario=usuario)


# Cerrar sesión
@index_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('IndexRoute.index'))


# ruta notificaciones
@index_bp.route("/notificaciones")
def notificaciones():
    usuario = session.get('usuario')
    if not usuario:
        return redirect(url_for('IndexRoute.index'))
    return render_template("notificacion/notificaciones.jinja2", usuario=usuario)

#ruta planes
@index_bp.route("/planes")
def planes():
    usuario = session.get('usuario')
    if not usuario:
        return redirect(url_for('IndexRoute.index'))
    return render_template("planes/planes.jinja2", usuario=usuario)

#ruta empleos
@index_bp.route("/empleos")
def empleos():
    usuario = session.get('usuario')
    if not usuario:
        return redirect(url_for('IndexRoute.index'))
    return render_template("empleos/empleos.jinja2", usuario=usuario)

#ruta mensajes
@index_bp.route("/mensajes")
def mensajes():
    usuario = session.get('usuario')
    if not usuario:
        return redirect(url_for('IndexRoute.index'))
    return render_template("mensajes/mensajes.jinja2", usuario=usuario)

#registro
@index_bp.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form['nombre']
        correo = request.form['correo']
        password = request.form['password']
        confirmar = request.form['confirmar']

        if password != confirmar:
            flash("Las contraseñas no coinciden", "error")
        else:
            # Aquí guarda al usuario en tu base de datos
            # (Valida duplicados, hashea la contraseña, etc.)
            flash("Cuenta creada con éxito", "success")
            return redirect(url_for('IndexRoute.index'))

    return render_template("registro.jinja2")

