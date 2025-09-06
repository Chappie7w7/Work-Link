from functools import wraps
from flask import session, redirect, url_for, flash
from app.utils.roles import Roles  


def login_role_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if "user_id" not in session or "tipo_usuario" not in session:
                flash("Debes iniciar sesión", "error")
                return redirect(url_for("LoginRoute.login_form"))

            user_role = session["tipo_usuario"].lower()
            allowed_roles = [r.lower() for r in roles]

            if user_role not in allowed_roles:
                flash("No tienes permiso para acceder a esta sección", "error")
                return redirect(url_for("IndexRoute.index"))

            return f(*args, **kwargs)
        return wrapped
    return decorator

















   