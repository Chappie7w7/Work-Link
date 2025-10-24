from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from app.controller.ctr_empleos import get_user_from_session
from app.utils.decorators import login_role_required
from app.utils.roles import Roles
from app.db.sql import db
from app.models.md_vacantes import VacanteModel

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

    return render_template("empleos/jobs.jinja2", usuario=user, vacantes=vacantes)

