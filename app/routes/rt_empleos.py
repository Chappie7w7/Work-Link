from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from app.controller.ctr_empleos import get_user_from_session
from app.utils.decorators import login_role_required
from app.utils.roles import Roles
from app.db.sql import db
from app.models.md_vacantes import VacanteModel
from app.models.md_empleados import EmpleadoModel
from app.models.md_postulacion import PostulacionModel
from werkzeug.utils import secure_filename
from datetime import datetime
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
    
    # Traer solo las vacantes publicadas (activas) y no eliminadas con la empresa cargada
    vacantes = VacanteModel.query.options(joinedload(VacanteModel.empresa)) \
                .filter_by(estado='publicada', eliminada=False) \
                .order_by(VacanteModel.id.desc()).all()

    return render_template("empleos/empleos.jinja2", usuario=user, vacantes=vacantes)


@rt_empleos.route("/empleos/postular/<int:vacante_id>", methods=["GET", "POST"])
@login_role_required(Roles.EMPLEADO)
def postular(vacante_id: int):
    user = get_user_from_session(session)
    if not user:
        return redirect(url_for('IndexRoute.index'))

    # Verificar vacante (solo si no está eliminada)
    vacante = VacanteModel.query.filter_by(id=vacante_id, eliminada=False).first()
    if not vacante:
        flash("La vacante no existe o ha sido eliminada", "danger")
        return redirect(url_for('EmpleosRoute.empleos'))
    
    # Verificar que la vacante esté activa (publicada) y disponible para postular
    if not vacante.disponible_para_postular():
        if vacante.estado == 'cerrada':
            flash("Esta vacante está cerrada. Ya se ocupó la posición.", "warning")
        elif vacante.max_postulantes is not None and vacante.postulantes_actuales >= vacante.max_postulantes:
            flash("Esta vacante ha alcanzado el número máximo de postulantes permitidos.", "warning")
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

    # Obtener perfil de empleado del usuario logueado
    empleado = EmpleadoModel.query.get(user["id"])  # PK de empleados es usuarios.id
    if not empleado:
        flash("No se encontró tu perfil de empleado. Por favor, completa tu perfil primero.", "danger")
        return redirect(url_for('PerfilRoute.editar'))

    if request.method == "POST":
        try:
            # Validar datos requeridos
            if not all([request.form.get('educacion'), request.form.get('experiencia'), request.form.get('habilidades')]):
                flash("Por favor completa todos los campos requeridos", "warning")
                return redirect(url_for('EmpleosRoute.postular', vacante_id=vacante_id))

            # Datos del formulario
            educacion = request.form.get("educacion", "").strip()
            experiencia = request.form.get("experiencia", "").strip()
            habilidades = request.form.get("habilidades", "").strip()
            cv_destacado = request.form.get("cv_destacado") == "on"
            notas = request.form.get("notas", "").strip()

            # Manejo de CV (archivo opcional)
            cv_file = request.files.get("curriculum")
            
            if cv_file and cv_file.filename:
                try:
                    filename = secure_filename(cv_file.filename)
                    upload_dir = os.path.join("app", "static", "uploads", "cv")
                    os.makedirs(upload_dir, exist_ok=True)
                    filepath = os.path.join(upload_dir, filename)
                    cv_file.save(filepath)
                    # Actualizar el curriculum_url del empleado
                    empleado.curriculum_url = url_for('static', filename=f"uploads/cv/{filename}", _external=True)
                except Exception as e:
                    print(f"Error al guardar el archivo: {str(e)}")
                    flash("Hubo un error al procesar tu archivo CV. Por favor, inténtalo de nuevo.", "danger")
                    return redirect(url_for('EmpleosRoute.postular', vacante_id=vacante_id))

            # Verificar nuevamente la disponibilidad antes de crear la postulación
            if not vacante.disponible_para_postular():
                flash("Lo sentimos, esta vacante ya no está disponible para postulaciones.", "warning")
                return redirect(url_for('EmpleosRoute.empleos'))

            # Verificar si el usuario ya se postuló a esta vacante
            postulacion_existente = PostulacionModel.query.filter_by(
                empleado_id=user["id"],
                vacante_id=vacante_id
            ).first()
            
            if postulacion_existente:
                flash("Ya te has postulado a esta vacante anteriormente.", "info")
                return redirect(url_for('EmpleosRoute.empleos'))

            # Crear postulación
            try:
                # Primero actualizamos el perfil del empleado
                empleado.educacion = educacion
                empleado.experiencia = experiencia
                empleado.habilidades = habilidades
                empleado.cv_destacado = cv_destacado
                db.session.add(empleado)
                
                # Luego creamos la postulación con los datos mínimos necesarios
                postulacion = PostulacionModel(
                    empleado_id=user["id"],
                    vacante_id=vacante_id,
                    estado="postulado"
                )
                db.session.add(postulacion)
                
                # Incrementar el contador de postulantes
                vacante.postulantes_actuales = (vacante.postulantes_actuales or 0) + 1
                
                # Si se alcanzó el límite de postulantes, pausar la vacante
                if vacante.max_postulantes is not None and vacante.postulantes_actuales >= vacante.max_postulantes:
                    vacante.estado = 'pausada'
                    mensaje_exito = "✅ ¡Postulación exitosa! Esta vacante ha alcanzado el número máximo de postulantes y ha sido pausada temporalmente."
                else:
                    mensaje_exito = "✅ ¡Postulación exitosa! Tu solicitud ha sido enviada."
                
                # Crear notificación para la empresa
                try:
                    from app.models.md_notificacion import NotificacionModel
                    from app.utils.timezone_helper import get_mexico_time
                    from app import socketio
                    
                    nombre_empleado = f"{user.get('nombre', '')} {user.get('apellido', '')}".strip() or 'Un candidato'
                    titulo_vacante = getattr(vacante, 'titulo', 'una vacante')
                    empresa_id = getattr(vacante, 'empresa_id', None)
                    
                    if empresa_id:
                        # Crear notificación en la base de datos
                        notificacion = NotificacionModel(
                            usuario_id=empresa_id,
                            mensaje=f"📝 {nombre_empleado} se ha postulado a tu vacante: {titulo_vacante}",
                            tipo='postulacion',
                            leido=False,
                            fecha_envio=get_mexico_time(),
                            enlace=url_for('rt_empresa.ver_postulaciones', vacante_id=vacante_id)
                        )
                        db.session.add(notificacion)
                        db.session.flush()  # Para obtener el ID de la notificación
                        
                        # Enviar notificación en tiempo real
                        socketio.emit('nueva_notificacion', {
                            'id': notificacion.id,
                            'usuario_id': empresa_id,
                            'mensaje': notificacion.mensaje,
                            'tipo': 'postulacion',
                            'leido': False,
                            'fecha_envio': notificacion.fecha_envio.isoformat(),
                            'enlace': notificacion.enlace
                        }, namespace='/notificaciones')
                        
                except Exception as e:
                    print(f"Error al crear notificación: {str(e)}")
                    # Continuar aunque falle la notificación
                
                # Confirmar todos los cambios en la base de datos
                db.session.commit()
                flash(mensaje_exito, "success")
                return redirect(url_for('EmpleosRoute.empleos'))
                
            except Exception as e:
                db.session.rollback()
                import traceback
                error_details = traceback.format_exc()
                print(f"=== ERROR AL CREAR POSTULACIÓN ===")
                print(f"Tipo de error: {type(e).__name__}")
                print(f"Mensaje: {str(e)}")
                print("Traceback completo:")
                print(error_details)
                print("Datos del formulario:", request.form)
                print("Datos del archivo:", request.files)
                print("Datos del empleado:", {
                    'id': user.get('id'),
                    'nombre': user.get('nombre'),
                    'apellido': user.get('apellido')
                })
                print("Datos de la vacante:", {
                    'id': vacante_id,
                    'titulo': getattr(vacante, 'titulo', None),
                    'empresa_id': getattr(vacante, 'empresa_id', None)
                })
                print("==================================")
                
                flash(f"Error al procesar la postulación: {str(e)}. Por favor, inténtalo de nuevo o contacta al soporte.", "danger")
                return redirect(url_for('EmpleosRoute.postular', vacante_id=vacante_id))
                
        except Exception as e:
            db.session.rollback()
            print(f"Error inesperado en la postulación: {str(e)}")
            import traceback
            traceback.print_exc()
            flash("Ocurrió un error inesperado al procesar tu solicitud. Por favor, inténtalo de nuevo más tarde.", "danger")

    # GET: Renderizar formulario con datos existentes del empleado (si hay)
    # Asegurarse de que los campos tengan valores por defecto si están vacíos
    context = {
        'usuario': user,
        'vacante': vacante,
        'empleado': empleado,
        'educacion': empleado.educacion or '',
        'experiencia': empleado.experiencia or '',
        'habilidades': empleado.habilidades or ''
    }
    
    return render_template("empleos/postular.jinja2", **context)

