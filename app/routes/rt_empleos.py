from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from app.controller.ctr_empleos import get_user_from_session
from app.utils.decorators import login_role_required
from app.utils.roles import Roles
from app.db.sql import db
from app.models.md_vacantes import VacanteModel
from app.models.md_postulacion import PostulacionModel
from app.models.md_empleados import EmpleadoModel
from datetime import datetime

rt_empleos = Blueprint('EmpleosRoute', __name__)


from sqlalchemy.orm import joinedload

@rt_empleos.route("/empleos")
def empleos():
    user = get_user_from_session(session)
    if not user:
        return redirect(url_for('IndexRoute.index'))

    # Traer todas las vacantes con la empresa cargada
    vacantes = VacanteModel.query.options(joinedload(VacanteModel.empresa)) \
                .order_by(VacanteModel.id.desc()).all()

    postulaciones_user = []
    if user.get("tipo_usuario") == "empleado":
        postulaciones_user = [p.vacante_id for p in PostulacionModel.query.filter_by(empleado_id=user["id"]).all()]


    return render_template("empleos/empleos.jinja2", usuario=user, vacantes=vacantes, postulaciones_user=postulaciones_user)




@rt_empleos.route("/empleos/postular/<int:vacante_id>", methods=["POST"])
def postular(vacante_id):
    user = get_user_from_session(session)
    if not user:
        return redirect(url_for("IndexRoute.index"))

    # Verificamos si es un empleado
    empleado = EmpleadoModel.query.get(user["id"])
    if not empleado:
        flash("❌ Solo los empleados pueden postularse.")
        return redirect(url_for("EmpleosRoute.empleos"))

    # Revisar si ya está postulado
    postulacion_existente = PostulacionModel.query.filter_by(
        vacante_id=vacante_id,
        empleado_id=empleado.id
    ).first()

    if postulacion_existente:
        flash("⚠️ Ya te has postulado a esta vacante.")
        return redirect(url_for("EmpleosRoute.empleos"))

    # Crear la postulación
    nueva_postulacion = PostulacionModel(
        vacante_id=vacante_id,
        empleado_id=empleado.id,
        fecha_postulacion=datetime.utcnow(),
        estado="postulado"
    )

    try:
        db.session.add(nueva_postulacion)
        db.session.commit()
        flash("✅ Te postulaste con éxito.")
    except Exception as e:
        db.session.rollback()
        flash(f"❌ Error al postular: {str(e)}")

    return redirect(url_for("EmpleosRoute.empleos"))
