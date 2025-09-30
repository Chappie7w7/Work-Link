from flask import Blueprint, redirect, render_template, request, url_for, session, flash
from app.controller.ctr_login import login_user, logout_user
from app.utils.roles import Roles
from flask_mail import Message
from app.models.md_usuarios import UsuarioModel
from werkzeug.security import generate_password_hash
from app.db.sql import db
import secrets
from datetime import datetime, timedelta
from app.extensiones import mail

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
        return redirect(url_for("InicioRoute.inicio"))
    else:
        return redirect(url_for("IndexRoute.index"))

# Ruta para mostrar formulario de recuperación de contraseña
@rt_login.route("/recuperar", methods=["GET", "POST"])
def recuperar():
    if request.method == "POST":
        correo = request.form.get("correo", "").strip()
        usuario = UsuarioModel.query.filter_by(correo=correo).first()

        if not usuario:
            flash("No existe una cuenta registrada con ese correo.", "danger")
            return redirect(url_for("LoginRoute.recuperar"))

        # Generar token y expiración
        usuario.reset_token = secrets.token_hex(16)
        usuario.reset_token_expiration = datetime.utcnow() + timedelta(hours=1)
        db.session.commit()

        reset_link = url_for("LoginRoute.reset_password", token=usuario.reset_token, _external=True)

        try:
            msg = Message(
                "Recuperación de contraseña - Work Link",
                sender="desarrollopractica81@gmail.com",
                recipients=[correo],
                body=f"Hola {usuario.nombre},\n\n"
                     f"Para restablecer tu contraseña, haz clic en el siguiente enlace:\n{reset_link}\n\n"
                     f"Si no solicitaste este cambio, ignora este mensaje."
            )
            mail.send(msg)
            flash("Se ha enviado un correo con las instrucciones para restablecer tu contraseña.", "success")
        except Exception as e:
            flash(f"Hubo un problema al enviar el correo: {e}", "danger")

        return redirect(url_for("LoginRoute.login"))

    return render_template("recuperar.jinja2")


# -------------------------------
# RESETEAR CONTRASEÑA
# -------------------------------
@rt_login.route("/reset/<token>", methods=["GET", "POST"])
def reset_password(token):
    usuario = UsuarioModel.query.filter_by(reset_token=token).first()

    if not usuario or usuario.reset_token_expiration < datetime.utcnow():
        flash("El enlace para restablecer la contraseña es inválido o ha caducado.", "danger")
        return redirect(url_for("LoginRoute.recuperar"))

    if request.method == "POST":
        nueva_contra = request.form.get("password")
        confirm_contra = request.form.get("confirm_password")

        if not nueva_contra or not confirm_contra:
            flash("Todos los campos son obligatorios.", "danger")
            return redirect(url_for("LoginRoute.reset_password", token=token))

        if nueva_contra != confirm_contra:
            flash("Las contraseñas no coinciden.", "danger")
            return redirect(url_for("LoginRoute.reset_password", token=token))

        usuario.contraseña = generate_password_hash(nueva_contra)
        usuario.reset_token = None
        usuario.reset_token_expiration = None
        db.session.commit()

        flash("Tu contraseña ha sido restablecida con éxito.", "success")
        return redirect(url_for("LoginRoute.recuperar"))

    return render_template("reset_password.jinja2", token=token)

@rt_login.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("IndexRoute.index"))
