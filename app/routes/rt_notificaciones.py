from flask import Blueprint, render_template, session, redirect, url_for

rt_notificaciones = Blueprint('NotificacionesRoute', __name__)

@rt_notificaciones.route("/notificaciones")
def notificaciones():
    usuario = session.get('usuario')
    if not usuario:
        return redirect(url_for('IndexRoute.index'))
    return render_template("notificacion/notificaciones.jinja2", usuario=usuario)
