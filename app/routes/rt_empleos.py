from flask import Blueprint, render_template, session, redirect, url_for
from app.controller.ctr_empleos import get_user_from_session
from app.utils.decorators import login_role_required
from app.utils.roles import Roles

rt_empleos = Blueprint('EmpleosRoute', __name__)


@rt_empleos.route("/empleos")
def empleos():
    user = get_user_from_session(session)
    if not user:
        return redirect(url_for('IndexRoute.index'))
    return render_template("empleos/empleos.jinja2", usuario=user)
