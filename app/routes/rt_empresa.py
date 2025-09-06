from flask import Blueprint, render_template
from app.utils.decorators import login_role_required
from app.utils.roles import Roles

rt_empresa = Blueprint("rt_empresa", __name__, url_prefix="/empresa")

# Dashboard de empresa
@rt_empresa.route("/")
@login_role_required(Roles.EMPRESA)
def dashboard():
    ofertas = [
        {"id": 1, "titulo": "Desarrollador Backend", "estado": "Activo"},
        {"id": 2, "titulo": "Diseñador UX/UI", "estado": "Activo"},
    ]

    candidatos = [
        {"id": 101, "nombre": "Juan Pérez"},
        {"id": 102, "nombre": "María López"},
    ]

    return render_template(
        "empresa/empresa.jinja2",
        ofertas_activas=len(ofertas),
        postulantes_totales=len(candidatos),
        ofertas=ofertas,
        candidatos=candidatos,
    )

# Ruta para publicar empleo
@rt_empresa.route("/publicar")
@login_role_required(Roles.EMPRESA)
def publicar_empleo():
    return render_template("empresa/publicar_empleo.jinja2")

# Ruta para ver perfil de candidato
@rt_empresa.route("/candidato/<int:candidato_id>")
@login_role_required(Roles.EMPRESA)
def ver_candidato(candidato_id):
    return f"<h3>Perfil del candidato con ID: {candidato_id}</h3>"
