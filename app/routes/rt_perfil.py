from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.controller import ctr_perfil
from app.utils.decorators import login_role_required
from app.utils.roles import Roles

rt_perfil = Blueprint("PerfilRoute", __name__, url_prefix="/perfil")


@rt_perfil.route("/editar", methods=["GET", "POST"])
@login_role_required(Roles.EMPLEADO)
def editar():
    usuario = session.get("usuario")
    if not usuario:
        flash("Debes iniciar sesión", "error")
        return redirect(url_for("LoginRoute.login_form"))

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        correo = request.form.get("correo", "").strip()
        foto_perfil_file = request.files.get("foto_perfil")

        user_db, error = ctr_perfil.update_user_with_photo(
            usuario["id"], nombre, correo, foto_perfil_file
        )
        if error:
            flash(error, "error")
            return redirect(url_for("PerfilRoute.editar"))

        # Actualizar sesión
        session["usuario"]["nombre"] = user_db.nombre
        session["usuario"]["correo"] = user_db.correo

        flash("Perfil actualizado correctamente", "success")
        return redirect(url_for("PerfilRoute.editar"))

    # Obtener usuario desde la base de datos para que siempre esté actualizado
    user_db, error = ctr_perfil.get_user_by_id(usuario["id"])
    if error:
        flash(error, "error")
        return redirect(url_for("InicioRoute.inicio"))

    return render_template("perfil/editar_perfil.jinja2", current_user=user_db)
