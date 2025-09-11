from types import SimpleNamespace
from flask import Blueprint, render_template, session
from app.models.md_vacantes import VacanteModel
from sqlalchemy.orm import joinedload

rt_index = Blueprint('IndexRoute', __name__)

@rt_index.route('/')
def index():
    usuario_session = session.get("usuario")

    if isinstance(usuario_session, dict):
        current_user = SimpleNamespace(**usuario_session)
    else:
        current_user = None

    # 🔹 Traer las 3 vacantes más recientes, destacadas y activas
    jobs = (
        VacanteModel.query
        .options(joinedload(VacanteModel.empresa))  # Trae también la empresa
        .filter_by(destacada=True, estado='publicada')  # Solo destacadas y publicadas
        .order_by(VacanteModel.fecha_publicacion.desc())  # Las más recientes primero
        .limit(3)
        .all()
    )

    return render_template('index.jinja2', current_user=current_user, jobs=jobs)


