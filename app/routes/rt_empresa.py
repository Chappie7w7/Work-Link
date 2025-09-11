from flask import Blueprint, render_template
from app.utils.decorators import login_role_required
from app.utils.roles import Roles
from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from app.controller.ctr_empleos import get_user_from_session
from app.utils.roles import Roles
from app.db.sql import db
from app.models.md_vacantes import VacanteModel
from app.models.md_empresas import EmpresaModel

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
    user = get_user_from_session(session)
    if not user:
        return redirect(url_for("IndexRoute.index"))
    return render_template("empresa/publicar_empleo.jinja2", usuario=user)


@rt_empresa.route("/empleos/nueva", methods=["GET", "POST"])
@login_role_required(Roles.EMPRESA)
def nueva_vacante():
    user = get_user_from_session(session)
    if not user:
        return redirect(url_for('IndexRoute.index'))

    if request.method == "POST":
        try:
            # Datos del formulario
            titulo = request.form.get("titulo")
            descripcion = request.form.get("descripcion")
            requisitos = request.form.get("requisitos")
            ubicacion = request.form.get("ubicacion")
            estado = request.form.get("estado")
            destacada = True if request.form.get("destacada") == "true" else False
            salario_aprox = request.form.get("salario_aprox")
            modalidad = request.form.get("modalidad")
            salario_aprox = float(salario_aprox) if salario_aprox else None

            # 🔹 Obtener empresa logueada desde la BD
            empresa = EmpresaModel.query.get(user["id"])
            if not empresa:
                flash("❌ No se encontró la empresa logueada.")
                return redirect(url_for("rt_empresa.dashboard"))

            # 🔹 Crear vacante
            nueva_vacante = VacanteModel(
                empresa_id=empresa.id,
                titulo=titulo,
                descripcion=descripcion,
                requisitos=requisitos,
                ubicacion=ubicacion,
                estado=estado,
                destacada=destacada,
                salario_aprox=salario_aprox,
                modalidad=modalidad
            )

            # 🔹 Guardar en la BD
            db.session.add(nueva_vacante)
            db.session.commit()

            flash("✅ Vacante registrada con éxito")
            return redirect(url_for("rt_empresa.dashboard"))

        except Exception as e:
            db.session.rollback()
            import traceback
            print("❌ ERROR al registrar vacante:", e)
            traceback.print_exc()
            flash(f"❌ Error al registrar la vacante: {str(e)}")

    # GET: renderizar formulario
    return render_template("empresa/publicar_empleo.jinja2", usuario=user)



# Ruta para ver perfil de candidato
@rt_empresa.route("/candidato/<int:candidato_id>")
@login_role_required(Roles.EMPRESA)
def ver_candidato(candidato_id):
    return f"<h3>Perfil del candidato con ID: {candidato_id}</h3>"
