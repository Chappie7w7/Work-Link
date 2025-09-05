from flask import Blueprint, redirect, render_template, request, url_for, session, flash
from app.controller.ctr_login import login_user, logout_user
from app.utils.roles import Roles

rt_login = Blueprint("LoginRoute", __name__)

@rt_login.route("/login")
def login_form():
    return render_template("login.jinja2")

@rt_login.route("/login", methods=["POST"])
def login():
    correo = request.form.get("correo", "").strip()
    password = request.form.get("password", "").strip()

    user, error = login_user(correo, password)

    if not user:
        flash(error, "error")
        return redirect(url_for("LoginRoute.login_form"))

    session["user_id"] = user.id
    session["tipo_usuario"] = user.tipo_usuario
    session["usuario"] = {
    "id": user.id,
    "nombre": user.nombre,
    "correo": user.correo,
    "tipo_usuario": user.tipo_usuario,  
}

    if user.tipo_usuario == Roles.EMPRESA:
        return redirect(url_for("rt_empresa.dashboard"))
    elif user.tipo_usuario == Roles.EMPLEADO:
        return redirect(url_for("InicioRoute.inicio"))
    elif user.tipo_usuario == Roles.SUPERADMIN:  
        return redirect(url_for("AdminRoute.dashboard"))
    else:
        return redirect(url_for("IndexRoute.index"))


@rt_login.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("LoginRoute.login_form"))
