from flask import Blueprint, render_template, session, redirect, url_for
from app.utils.decorators import login_role_required
from app.utils.roles import Roles

rt_inicio = Blueprint("InicioRoute", __name__)

@rt_inicio.route("/inicio_empleado")
@login_role_required(Roles.EMPLEADO)
def inicio():
    usuario = session.get("usuario")
    if not usuario:
        return redirect(url_for("LoginRoute.login_form"))
    return render_template("inicio.jinja2", current_user=usuario)
