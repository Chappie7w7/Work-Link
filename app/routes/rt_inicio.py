from flask import Blueprint, render_template, session, redirect, url_for

rt_inicio = Blueprint('InicioRoute', __name__)

@rt_inicio.route('/inicio')
def inicio():
    usuario = session.get('usuario')
    if not usuario:
        return redirect(url_for('IndexRoute.index'))
    return render_template('inicio.jinja2', usuario=usuario)
