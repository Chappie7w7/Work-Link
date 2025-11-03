from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from app.controller.ctr_empleos import get_user_from_session
from app.utils.decorators import login_role_required
from app.utils.roles import Roles
from app.db.sql import db
from app.models.md_vacantes import VacanteModel
from app.models.md_empleados import EmpleadoModel
from app.models.md_postulacion import PostulacionModel
from werkzeug.utils import secure_filename
import os

rt_empleos = Blueprint('EmpleosRoute', __name__)


from sqlalchemy.orm import joinedload

@rt_empleos.route("/empleos")
def empleos():
    user = get_user_from_session(session)
    if not user:
        return redirect(url_for('IndexRoute.index'))

    # Verificar y cerrar automáticamente vacantes publicadas que tengan contratados
    from app.models.md_postulacion import PostulacionModel
    from sqlalchemy import and_
    
    # Buscar vacantes publicadas que tienen contratados
    vacantes_con_contratados = (
        db.session.query(VacanteModel)
        .join(PostulacionModel, and_(
            VacanteModel.id == PostulacionModel.vacante_id,
            PostulacionModel.estado == 'contratado'
        ))
        .filter(VacanteModel.estado == 'publicada')
        .all()
    )
    
    # Cerrar automáticamente estas vacantes
    for vacante in vacantes_con_contratados:
        vacante.estado = 'cerrada'
    
    if vacantes_con_contratados:
        db.session.commit()
    
    # Traer solo las vacantes publicadas (activas) con la empresa cargada
    vacantes = VacanteModel.query.options(joinedload(VacanteModel.empresa)) \
                .filter_by(estado='publicada') \
                .order_by(VacanteModel.id.desc()).all()

    return render_template("empleos/empleos.jinja2", usuario=user, vacantes=vacantes)


@rt_empleos.route("/empleos/postular/<int:vacante_id>", methods=["GET", "POST"])
@login_role_required(Roles.EMPLEADO)
def postular(vacante_id: int):
    user = get_user_from_session(session)
    if not user:
        return redirect(url_for('IndexRoute.index'))

    # Verificar vacante
    vacante = VacanteModel.query.get(vacante_id)
    if not vacante:
        flash("La vacante no existe", "danger")
        return redirect(url_for('EmpleosRoute.empleos'))
    
    # Verificar que la vacante esté activa (publicada)
    if vacante.estado != 'publicada':
        if vacante.estado == 'cerrada':
            flash("Esta vacante está cerrada. Ya se ocupó la posición.", "warning")
        else:
            flash("Esta vacante no está disponible para postulaciones.", "warning")
        return redirect(url_for('EmpleosRoute.empleos'))
    
    # Verificar si ya hay alguien contratado en esta vacante
    ya_contratado = PostulacionModel.query.filter_by(
        vacante_id=vacante_id,
        estado='contratado'
    ).first()
    
    if ya_contratado:
        vacante.estado = 'cerrada'
        db.session.commit()
        flash("Esta vacante ya está ocupada y ha sido cerrada.", "warning")
        return redirect(url_for('EmpleosRoute.empleos'))

    # Obtener/crear perfil de empleado del usuario logueado
    empleado = EmpleadoModel.query.get(user["id"])  # PK de empleados es usuarios.id

    if request.method == "POST":
        try:
            # Datos Empleado
            educacion = request.form.get("educacion")
            experiencia = request.form.get("experiencia")
            habilidades = request.form.get("habilidades")
            cv_destacado = True if request.form.get("cv_destacado") == "on" else False

            # Manejo de CV (archivo opcional)
            cv_file = request.files.get("curriculum")
            curriculum_url = None
            if cv_file and cv_file.filename:
                filename = secure_filename(cv_file.filename)
                upload_dir = os.path.join("app", "static", "uploads", "cv")
                os.makedirs(upload_dir, exist_ok=True)
                filepath = os.path.join(upload_dir, filename)
                cv_file.save(filepath)
                # URL relativa para servir desde static
                curriculum_url = url_for('static', filename=f"uploads/cv/{filename}")

            # Crear o actualizar Empleado
            if not empleado:
                empleado = EmpleadoModel(
                    id=user["id"],
                    curriculum_url=curriculum_url,
                    educacion=educacion,
                    experiencia=experiencia,
                    habilidades=habilidades,
                    cv_destacado=cv_destacado,
                )
                db.session.add(empleado)
            else:
                if curriculum_url:
                    empleado.curriculum_url = curriculum_url
                empleado.educacion = educacion
                empleado.experiencia = experiencia
                empleado.habilidades = habilidades
                empleado.cv_destacado = cv_destacado

            # Datos de Postulación (mínimo estado inicial)
            estado = 'postulado'
            notas_empresa = request.form.get("notas")  # opcional, podría dejarse vacío

            postulacion = PostulacionModel(
                vacante_id=vacante.id,
                empleado_id=empleado.id,
                estado=estado,
                notas_empresa=notas_empresa,
            )

            db.session.add(postulacion)
            
            # Crear notificación para la empresa cuando alguien se postula
            from app.models.md_notificacion import NotificacionModel
            from app.utils.timezone_helper import get_mexico_time
            
            # Obtener información del empleado y la vacante
            nombre_empleado = user.get('nombre', 'Un candidato')
            titulo_vacante = vacante.titulo if vacante else 'una vacante'
            empresa_id = vacante.empresa_id if vacante else None
            
            if empresa_id:
                notificacion = NotificacionModel(
                    usuario_id=empresa_id,
                    mensaje=f"📝 {nombre_empleado} se ha postulado a la vacante: {titulo_vacante}",
                    tipo='postulacion',
                    leido=False,
                    fecha_envio=get_mexico_time()
                )
                db.session.add(notificacion)
            
            db.session.commit()
            flash("Tu postulación se registró correctamente", "success")
            return redirect(url_for('EmpleosRoute.empleos'))
        except Exception as e:
            db.session.rollback()
            import traceback
            print("Error en postulación:", e)
            traceback.print_exc()
            flash("Ocurrió un error al postularte", "danger")

    # GET: Renderizar formulario con datos existentes del empleado (si hay)
    return render_template(
        "empleos/postular.jinja2",
        usuario=user,
        vacante=vacante,
        empleado=empleado,
    )

