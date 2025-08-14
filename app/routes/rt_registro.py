from flask import Blueprint, render_template, request, redirect, url_for, flash

rt_registro = Blueprint('RegistroRoute', __name__)

@rt_registro.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form['nombre']
        correo = request.form['correo']
        password = request.form['password']
        confirmar = request.form['confirmar']

        if password != confirmar:
            flash("Las contraseñas no coinciden", "error")
        else:
            # Guardar usuario en la BD (aquí deberías validar duplicados y hashear la contraseña)
            flash("Cuenta creada con éxito", "success")
            return redirect(url_for('IndexRoute.index'))

    return render_template("registro.jinja2")
