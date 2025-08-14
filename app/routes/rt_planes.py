from flask import Blueprint, render_template, session, redirect, url_for

rt_planes = Blueprint('PlanesRoute', __name__)

@rt_planes.route("/planes")
def planes():
    usuario = session.get('usuario')
    if not usuario:
        return redirect(url_for('IndexRoute.index'))
    return render_template("planes/planes.jinja2", usuario=usuario)
