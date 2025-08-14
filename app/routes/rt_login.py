from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models.md_usuarios import UsuarioModel

rt_login = Blueprint('LoginRoute', __name__)

@rt_login.route('/login')
def login_form():
    return render_template('login.jinja2')

@rt_login.route('/login', methods=['POST'])
def login():
    correo = request.form.get('correo', '').strip()
    password = request.form.get('password', '').strip()

    usuario = UsuarioModel.query.filter_by(correo=correo).first()

    if usuario and usuario.contraseña == password:
        session['usuario'] = usuario.correo
        session['nombre'] = usuario.nombre
        return redirect(url_for('InicioRoute.inicio'))
    
    flash('Usuario o contraseña incorrectos', 'error')
    return redirect(url_for('LoginRoute.login_form'))

@rt_login.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('IndexRoute.index'))
