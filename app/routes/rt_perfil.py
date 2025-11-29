from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.controller import ctr_perfil
from app.utils.decorators import login_role_required
from app.utils.roles import Roles
from app.db.sql import db
from app.models.md_usuarios import UsuarioModel
from flask import current_app
from app.extensiones import socketio

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
        # Asegurar que la nueva foto de perfil también se refleje en todas las páginas
        if hasattr(user_db, "foto_perfil"):
            session["usuario"]["foto_perfil"] = user_db.foto_perfil

        flash("Perfil actualizado correctamente", "success")
        return redirect(url_for("PerfilRoute.editar"))

    # Obtener usuario desde la base de datos para que siempre esté actualizado
    user_db, error = ctr_perfil.get_user_by_id(usuario["id"])
    if error:
        flash(error, "error")
        return redirect(url_for("InicioRoute.inicio"))

    return render_template("perfil/editar_perfil.jinja2", current_user=user_db)


@rt_perfil.route("/solicitar-eliminacion", methods=["POST"])
@login_role_required(Roles.EMPLEADO, Roles.EMPRESA)
def solicitar_eliminacion():
    """El usuario solicita eliminar su cuenta: se deshabilita (aprobado=False) y se notifica por flash."""
    usuario = session.get("usuario")
    if not usuario:
        flash("Debes iniciar sesión", "error")
        return redirect(url_for("LoginRoute.login_form"))

    try:
        user = UsuarioModel.query.get(usuario["id"])
        if not user:
            flash("Usuario no encontrado", "error")
            return redirect(url_for("PerfilRoute.editar"))

        # Marcar solicitud persistente (no deshabilita la cuenta)
        user.solicitud_eliminacion = True
        db.session.commit()

        # Notificar en tiempo real al dashboard del admin (sin correo)
        try:
            socketio.emit(
                "solicitud_eliminacion",
                {
                    "id": user.id,
                    "nombre": user.nombre,
                    "correo": user.correo,
                    "tipo_usuario": user.tipo_usuario,
                    "solicitud_eliminacion": True,
                },
                broadcast=True,
                namespace='/notificaciones',
            )
        except Exception:
            # Si no está activo SocketIO, continuar sin fallar
            pass

        flash("Se envió tu solicitud de eliminación al administrador. Tu cuenta seguirá activa hasta que la procesen.", "success")
    except Exception as e:
        flash(f"No se pudo enviar la solicitud: {str(e)}", "error")

    return redirect(url_for("PerfilRoute.editar"))
