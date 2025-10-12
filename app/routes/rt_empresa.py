from flask import Blueprint, render_template
from app.utils.decorators import login_role_required
from app.utils.roles import Roles
from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from app.controller.ctr_empleos import get_user_from_session
from app.utils.roles import Roles
from app.db.sql import db
from app.models.md_vacantes import VacanteModel
from app.models.md_empresas import EmpresaModel
from app.models.md_postulacion import PostulacionModel
from app.models.md_empleados import EmpleadoModel 

rt_empresa = Blueprint("rt_empresa", __name__, url_prefix="/empresa")



# Dashboard de empresa
@rt_empresa.route("/")
@login_role_required(Roles.EMPRESA)
def dashboard():
    user = get_user_from_session(session)
    if not user:
        return redirect(url_for("IndexRoute.index"))

    #  Traer vacantes de la empresa logueada
    vacantes_empresa = VacanteModel.query.filter_by(empresa_id=user["id"]).all()

    #  Contar postulaciones de todas las vacantes de la empresa
    postulantes_totales = (
        db.session.query(PostulacionModel)
        .join(VacanteModel)
        .filter(VacanteModel.empresa_id == user["id"])
        .count()
    )

    #  Contar ofertas activas
    ofertas_activas = VacanteModel.query.filter_by(empresa_id=user["id"], estado="publicada").count()

    #  Traer lista de postulaciones con empleado y usuario cargados
    from sqlalchemy.orm import joinedload
    from app.models.md_usuarios import UsuarioModel
    postulantes = (
        db.session.query(PostulacionModel)
        .join(VacanteModel)
        .filter(VacanteModel.empresa_id == user["id"])
        .options(joinedload(PostulacionModel.empleado).joinedload(EmpleadoModel.usuario))
        .order_by(PostulacionModel.fecha_postulacion.desc())
        .limit(10)
        .all()
    )

    return render_template(
        "empresa/empresa.jinja2",
        ofertas_activas=ofertas_activas,
        postulantes_totales=postulantes_totales,
        ofertas=vacantes_empresa,
        candidatos=postulantes,
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
    from app.models.md_empleados import EmpleadoModel
    from app.models.md_usuarios import UsuarioModel
    
    user = get_user_from_session(session)
    if not user:
        return redirect(url_for("IndexRoute.index"))
    
    # Obtener empleado y usuario
    empleado = EmpleadoModel.query.get(candidato_id)
    if not empleado:
        flash("Candidato no encontrado", "danger")
        return redirect(url_for("rt_empresa.dashboard"))
    
    usuario = UsuarioModel.query.get(candidato_id)
    
    # Obtener postulaciones del candidato para esta empresa
    postulaciones = PostulacionModel.query.join(VacanteModel) \
        .filter(PostulacionModel.empleado_id == candidato_id) \
        .filter(VacanteModel.empresa_id == user["id"]) \
        .all()
    
    return render_template(
        "empresa/ver_candidato.jinja2",
        empleado=empleado,
        usuario=usuario,
        postulaciones=postulaciones
    )


# Ruta para cambiar estado de postulación
@rt_empresa.route("/postulacion/<int:postulacion_id>/cambiar_estado", methods=["POST"])
@login_role_required(Roles.EMPRESA)
def cambiar_estado_postulacion(postulacion_id):
    from app.models.md_notificacion import NotificacionModel
    from app.utils.timezone_helper import get_mexico_time
    
    user = get_user_from_session(session)
    if not user:
        return redirect(url_for("IndexRoute.index"))
    
    postulacion = PostulacionModel.query.get(postulacion_id)
    if not postulacion:
        flash("Postulación no encontrada", "danger")
        return redirect(url_for("rt_empresa.dashboard"))
    
    # Verificar que la postulación pertenece a una vacante de esta empresa
    if postulacion.vacante.empresa_id != user["id"]:
        flash("No tienes permiso para modificar esta postulación", "danger")
        return redirect(url_for("rt_empresa.dashboard"))
    
    nuevo_estado = request.form.get("estado")
    notas = request.form.get("notas_empresa")
    estado_anterior = postulacion.estado
    
    if nuevo_estado in ['postulado', 'visto', 'en_proceso', 'rechazado', 'contratado']:
        postulacion.estado = nuevo_estado
        if notas:
            postulacion.notas_empresa = notas
        
        # Crear notificación para el empleado si el estado cambió
        if estado_anterior != nuevo_estado:
            # Mapeo de estados a emojis y mensajes
            estados_info = {
                'visto': {'emoji': '👁️', 'texto': 'ha revisado tu postulación'},
                'en_proceso': {'emoji': '⏳', 'texto': 'te ha puesto en proceso de selección'},
                'rechazado': {'emoji': '❌', 'texto': 'ha rechazado tu postulación'},
                'contratado': {'emoji': '🎉', 'texto': '¡te ha contratado! Felicidades'}
            }
            
            if nuevo_estado in estados_info:
                info = estados_info[nuevo_estado]
                mensaje = f"{info['emoji']} La empresa {postulacion.vacante.empresa.nombre_empresa} {info['texto']} para el puesto de {postulacion.vacante.titulo}"
                
                notificacion = NotificacionModel(
                    usuario_id=postulacion.empleado_id,
                    mensaje=mensaje,
                    tipo=nuevo_estado,
                    leido=False,
                    fecha_envio=get_mexico_time()
                )
                db.session.add(notificacion)
        
        db.session.commit()
        flash(f"Estado actualizado a: {nuevo_estado}", "success")
    else:
        flash("Estado inválido", "danger")
    
    return redirect(url_for("rt_empresa.ver_candidato", candidato_id=postulacion.empleado_id))
