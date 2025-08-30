from flask import Blueprint, render_template, session, redirect, url_for
from app.controller.ctr_empleos import get_user_from_session

rt_empleos = Blueprint('EmpleosRoute', __name__)


@rt_empleos.route("/empleos")
def empleos():
    user = get_user_from_session(session)
    if not user:
        return redirect(url_for('IndexRoute.index'))
    return render_template("empleos/empleos.jinja2", usuario=user)
