from flask import Blueprint, render_template, session, redirect, url_for

rt_empleos = Blueprint('EmpleosRoute', __name__)

@rt_empleos.route("/empleos")
def empleos():
    usuario = session.get('usuario')
    if not usuario:
        return redirect(url_for('IndexRoute.index'))
    return render_template("empleos/empleos.jinja2", usuario=usuario)
