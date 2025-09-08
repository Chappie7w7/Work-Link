from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from app.controller.ctr_empleos import get_user_from_session
from app.utils.decorators import login_role_required
from app.utils.roles import Roles
from app.db.sql import db
from app.models.md_vacantes import VacanteModel

rt_empleos = Blueprint('EmpleosRoute', __name__)


@rt_empleos.route("/empleos")
def empleos():
    user = get_user_from_session(session)
    if not user:
        return redirect(url_for('IndexRoute.index'))

    # Traer todas las vacantes publicadas
    vacantes = VacanteModel.query.order_by(VacanteModel.fecha_publicacion.desc()).all()

    return render_template("empleos/empleos.jinja2", usuario=user, vacantes=vacantes)



# 🚀 Nueva ruta para publicar vacantes
@rt_empleos.route("/empleos/nueva", methods=["GET", "POST"])
@login_role_required(Roles.EMPRESA)  # <-- si quieres que solo empresas publiquen
def nueva_vacante():
    user = get_user_from_session(session)
    if not user:
        return redirect(url_for('IndexRoute.index'))

    if request.method == "POST":
        try:
            empresa_id = request.form.get("empresa_id")
            titulo = request.form.get("titulo")
            descripcion = request.form.get("descripcion")
            requisitos = request.form.get("requisitos")
            ubicacion = request.form.get("ubicacion")
            estado = request.form.get("estado")
            destacada = True if request.form.get("destacada") == "true" else False
            salario_aprox = request.form.get("salario_aprox")
            modalidad = request.form.get("modalidad")

            salario_aprox = float(salario_aprox) if salario_aprox else None

            nueva_vacante = VacanteModel(
                empresa_id=empresa_id,
                titulo=titulo,
                descripcion=descripcion,
                requisitos=requisitos,
                ubicacion=ubicacion,
                estado=estado,
                destacada=destacada,
                salario_aprox=salario_aprox,
                modalidad=modalidad
            )

            db.session.add(nueva_vacante)
            db.session.commit()

            flash("✅ Vacante registrada con éxito")
            return redirect(url_for("EmpleosRoute.nueva_vacante"))

        except Exception as e:
            db.session.rollback()
            flash(f"❌ Error al registrar la vacante: {str(e)}")

    return render_template("empresa/publicar_empleo.jinja2", usuario=user)
