from flask import Blueprint, redirect, render_template, request, url_for, session, flash, current_app
from app.controller.ctr_login import login_user, logout_user
from app.utils.roles import Roles
from flask_mail import Message
from app.models.md_usuarios import UsuarioModel
from app.models.md_empleados import EmpleadoModel
from werkzeug.security import generate_password_hash, check_password_hash
from app.db.sql import db
import secrets
import os
import requests
from datetime import datetime, timedelta
from app.extensiones import mail
from app.auth.google_auth import get_google_auth, get_google_provider_cfg
from authlib.integrations.requests_client import OAuth2Session

rt_login = Blueprint("LoginRoute", __name__)

@rt_login.route("/login")
def login_form():
    return render_template("login.jinja2")

@rt_login.route("/form-registro-empleado", methods=["GET"])
def form_usuario():
    return render_template("registro.jinja2")

@rt_login.route("/form-registro-empresa", methods=["GET"])
def form_empresa():
    return render_template("empresa/registro_empresa.jinja2")

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

# 🔹 Función para crear la sesión OAuth de Google
def get_google_auth():
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    redirect_uri = "http://127.0.0.1:5000/google/callback"  # Debe coincidir con la ruta definida en @rt_login.route

    return OAuth2Session(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=["openid", "email", "profile"]
    )

# 🔹 Inicia el flujo de autenticación con Google
@rt_login.route("/google/login")
def google_login():
    """Inicia el flujo de autenticación con Google"""
    google_auth = get_google_auth()

    # URL de autorización de Google
    authorization_url, state = google_auth.create_authorization_url(
        "https://accounts.google.com/o/oauth2/auth",
        access_type="offline",
        include_granted_scopes="true"
    )

    session["state"] = state
    return redirect(authorization_url)
# 🔹 Maneja la respuesta (callback) después del login con Google
@rt_login.route("/google/callback")
def google_callback():
    try:
        if request.args.get("state") != session.get("state"):
            flash("Sesión inválida. Por favor, inténtalo de nuevo.", "error")
            current_app.logger.error("Error de estado en Google OAuth: estado no coincide")
            return redirect(url_for("LoginRoute.login_form"))

        google_auth = get_google_auth()

        try:
            # Intercambia el código por un token
            token_response = google_auth.fetch_token(
                "https://oauth2.googleapis.com/token",
                authorization_response=request.url
            )
            current_app.logger.info("Token obtenido exitosamente")
        except Exception as e:
            current_app.logger.error(f"Error al obtener token de Google: {str(e)}")
            flash("Error al autenticar con Google. Por favor, inténtalo de nuevo.", "error")
            return redirect(url_for("LoginRoute.login_form"))

        try:
            # Obtiene la información del usuario desde Google
            userinfo_response = requests.get(
                "https://www.googleapis.com/oauth2/v1/userinfo",
                headers={"Authorization": f"Bearer {google_auth.token['access_token']}"}
            )
            userinfo_response.raise_for_status()
            user_data = userinfo_response.json()
            current_app.logger.info(f"Datos del usuario obtenidos: {user_data}")
        except Exception as e:
            current_app.logger.error(f"Error al obtener información del usuario: {str(e)}")
            flash("No se pudo obtener la información de tu cuenta de Google.", "error")
            return redirect(url_for("LoginRoute.login_form"))

        try:
            # Buscar o crear el usuario en tu base de datos
            usuario = UsuarioModel.query.filter_by(correo=user_data["email"]).first()
            
            if not usuario:
                # Crear nuevo usuario
                nombre = user_data.get("name") or user_data["email"].split("@")[0]
                usuario = UsuarioModel(
                    nombre=nombre,
                    correo=user_data["email"],
                    tipo_usuario=Roles.EMPLEADO,
                    google_id=user_data["id"],
                    foto_perfil=user_data.get("picture"),
                    fecha_registro=datetime.utcnow()
                )
                db.session.add(usuario)
                db.session.flush()  # Para obtener el ID del usuario recién creado
                
                # Crear perfil de empleado automáticamente si es empleado
                if usuario.tipo_usuario == Roles.EMPLEADO:
                    empleado = EmpleadoModel(id=usuario.id)
                    db.session.add(empleado)
                
                db.session.commit()
                current_app.logger.info(f"Nuevo usuario creado: {usuario.correo}")

            else:
                # Actualizar datos del usuario existente
                usuario.google_id = user_data["id"]
                usuario.foto_perfil = user_data.get("picture", usuario.foto_perfil)
                db.session.commit()
                current_app.logger.info(f"Usuario existente: {usuario.correo}")

            # Iniciar sesión
            session["user_id"] = usuario.id
            session["tipo_usuario"] = usuario.tipo_usuario
            session["usuario"] = {
                "id": usuario.id,
                "nombre": usuario.nombre,
                "correo": usuario.correo,
                "tipo_usuario": usuario.tipo_usuario,
                "foto_perfil": usuario.foto_perfil
            }

            flash(f"¡Bienvenido {usuario.nombre}!", "success")
            
            # Redirigir según el tipo de usuario
            if usuario.tipo_usuario == Roles.EMPRESA:
                return redirect(url_for("rt_empresa.dashboard"))
            return redirect(url_for("InicioRoute.inicio"))
                
        except Exception as e:
            current_app.logger.error(f"Error en el proceso de autenticación: {str(e)}")
            flash("Ocurrió un error al iniciar sesión con Google. Por favor, inténtalo de nuevo.", "error")
            return redirect(url_for("LoginRoute.login_form"))
    except Exception as e:
        current_app.logger.error(f"Error general en Google OAuth: {str(e)}")
        flash("Error inesperado. Por favor, inténtalo de nuevo más tarde.", "error")
        return redirect(url_for("LoginRoute.login_form"))

@rt_login.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("IndexRoute.index"))
