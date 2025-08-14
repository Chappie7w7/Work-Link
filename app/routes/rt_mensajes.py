from flask import Blueprint, render_template, session, redirect, url_for

rt_mensajes = Blueprint('MensajesRoute', __name__)

@rt_mensajes.route("/mensajes")
def mensajes():
    usuario = session.get('usuario')
    if not usuario:
        return redirect(url_for('IndexRoute.index'))
    return render_template("mensajes/mensajes.jinja2", usuario=usuario)
