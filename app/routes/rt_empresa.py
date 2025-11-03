from flask import Blueprint, render_template, session, redirect, url_for, request, flash, jsonify
from app.utils.decorators import login_role_required
from app.utils.roles import Roles
from app.controller.ctr_empleos import get_user_from_session
from app.controller import ctr_empresa
from app.db.sql import db
from app.models.md_vacantes import VacanteModel
from app.models.md_empresas import EmpresaModel
from app.models.md_postulacion import PostulacionModel
from app.models.md_empleados import EmpleadoModel
from app.models.md_mensaje import MensajeModel
from app.models.md_usuarios import UsuarioModel
from app.models.md_notificacion import NotificacionModel
from sqlalchemy import or_, and_, desc, func
from app.utils.timezone_helper import get_mexico_time
from app.utils.mensaje_helper import contar_mensajes_no_leidos

rt_empresa = Blueprint("rt_empresa", __name__, url_prefix="/empresa")



# Dashboard de empresa
@rt_empresa.route("/")
@login_role_required(Roles.EMPRESA)
def dashboard():
    try:
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
        from sqlalchemy.orm import joinedload, outerjoin
        try:
            postulantes = (
                db.session.query(PostulacionModel)
                .join(VacanteModel)
                .filter(VacanteModel.empresa_id == user["id"])
                .options(joinedload(PostulacionModel.empleado).joinedload(EmpleadoModel.usuario))
                .order_by(PostulacionModel.fecha_postulacion.desc())
                .limit(10)
                .all()
            )
        except Exception as e:
            # Si hay error en la consulta con joins, intentar sin los joins
            print(f"⚠️ Advertencia en consulta de postulantes: {str(e)}")
            postulantes = (
                db.session.query(PostulacionModel)
                .join(VacanteModel)
                .filter(VacanteModel.empresa_id == user["id"])
                .order_by(PostulacionModel.fecha_postulacion.desc())
                .limit(10)
                .all()
            )
        
        # Estadísticas de postulaciones por estado
        contratados = db.session.query(PostulacionModel).join(VacanteModel).filter(
            VacanteModel.empresa_id == user["id"],
            PostulacionModel.estado == 'contratado'
        ).count()
        
        en_proceso = db.session.query(PostulacionModel).join(VacanteModel).filter(
            VacanteModel.empresa_id == user["id"],
            PostulacionModel.estado == 'en_proceso'
        ).count()
        
        rechazados = db.session.query(PostulacionModel).join(VacanteModel).filter(
            VacanteModel.empresa_id == user["id"],
            PostulacionModel.estado == 'rechazado'
        ).count()
        
        postulados = db.session.query(PostulacionModel).join(VacanteModel).filter(
            VacanteModel.empresa_id == user["id"],
            PostulacionModel.estado == 'postulado'
        ).count()
        
        vistos = db.session.query(PostulacionModel).join(VacanteModel).filter(
            VacanteModel.empresa_id == user["id"],
            PostulacionModel.estado == 'visto'
        ).count()
        
        # Calcular porcentajes y tiempo promedio
        total_con_estados = postulados + vistos + en_proceso + contratados + rechazados
        tasa_conversion = round((contratados / total_con_estados * 100) if total_con_estados > 0 else 0, 1)

        # Métricas Clave - Vacante con más postulaciones
        vacante_mas_postulaciones = (
            db.session.query(VacanteModel, func.count(PostulacionModel.id).label('total_postulaciones'))
            .join(PostulacionModel, VacanteModel.id == PostulacionModel.vacante_id)
            .filter(VacanteModel.empresa_id == user["id"])
            .group_by(VacanteModel.id)
            .order_by(desc('total_postulaciones'))
            .first()
        )
        
        vacante_mas_vista = None
        if vacante_mas_postulaciones:
            vacante, total_post = vacante_mas_postulaciones
            vacante_mas_vista = {
                'titulo': vacante.titulo,
                'total_postulaciones': total_post
            }

        # Métricas Clave - Mejor tasa de respuesta (vacante con más postulaciones en relación a ofertas activas)
        mejor_tasa_respuesta = None
        if vacantes_empresa and len(vacantes_empresa) > 0:
            # Calcular tasa de respuesta por vacante
            tasas_vacantes = []
            for vacante in vacantes_empresa:
                if vacante.estado == 'publicada':
                    total_post_vacante = db.session.query(PostulacionModel).filter(
                        PostulacionModel.vacante_id == vacante.id
                    ).count()
                    tasa = round((total_post_vacante / ofertas_activas * 100) if ofertas_activas > 0 else 0, 1)
                    tasas_vacantes.append({
                        'titulo': vacante.titulo,
                        'tasa': tasa,
                        'postulaciones': total_post_vacante
                    })
            
            if tasas_vacantes:
                mejor_tasa_respuesta = max(tasas_vacantes, key=lambda x: x['tasa'])

        # Métricas Clave - Contrataciones del mes actual
        from datetime import datetime, timedelta
        mes_inicio = get_mexico_time().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        contrataciones_mes = db.session.query(PostulacionModel).join(VacanteModel).filter(
            VacanteModel.empresa_id == user["id"],
            PostulacionModel.estado == 'contratado',
            PostulacionModel.fecha_postulacion >= mes_inicio
        ).count()

        # Métricas Clave - Próximas entrevistas (postulaciones en proceso)
        entrevistas_programadas = en_proceso

        # Obtener datos de la empresa
        empresa = EmpresaModel.query.get(user["id"])
        usuario_empresa = UsuarioModel.query.get(user["id"])

        return render_template(
            "empresa/empresa.jinja2",
            ofertas_activas=ofertas_activas,
            postulantes_totales=postulantes_totales,
            ofertas=vacantes_empresa,
            candidatos=postulantes,
            contratados=contratados,
            en_proceso=en_proceso,
            rechazados=rechazados,
            postulados=postulados,
            vistos=vistos,
            total_con_estados=total_con_estados,
            tasa_conversion=tasa_conversion,
            empresa=empresa,
            usuario_empresa=usuario_empresa,
            vacante_mas_vista=vacante_mas_vista,
            mejor_tasa_respuesta=mejor_tasa_respuesta,
            contrataciones_mes=contrataciones_mes,
            entrevistas_programadas=entrevistas_programadas,
        )
    except Exception as e:
        import traceback
        print(f"❌ ERROR en dashboard de empresa: {str(e)}")
        traceback.print_exc()
        flash(f"Error al cargar el dashboard: {str(e)}", "error")
        return redirect(url_for("IndexRoute.index"))


# Ruta para editar perfil de empresa
@rt_empresa.route("/perfil/editar", methods=["GET", "POST"], endpoint="editar_perfil")
@login_role_required(Roles.EMPRESA)
def editar_perfil():
    user = get_user_from_session(session)
    if not user:
        return redirect(url_for("IndexRoute.index"))

    if request.method == "POST":
        nombre_empresa = request.form.get("nombre_empresa", "").strip()
        sector = request.form.get("sector", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        direccion = request.form.get("direccion", "").strip()
        telefono = request.form.get("telefono", "").strip()
        correo = request.form.get("correo", "").strip()
        logo_file = request.files.get("logo")

        empresa, error = ctr_empresa.update_empresa(
            user["id"], nombre_empresa, sector, descripcion, direccion, telefono, correo, logo_file
        )
        if error:
            flash(error, "error")
            return redirect(url_for("rt_empresa.editar_perfil"))

        flash("Perfil actualizado correctamente", "success")
        return redirect(url_for("rt_empresa.editar_perfil"))

    # GET: Obtener datos actuales
    empresa, error = ctr_empresa.get_empresa_by_id(user["id"])
    if error:
        flash(error, "error")
        return redirect(url_for("rt_empresa.dashboard"))

    usuario_empresa = UsuarioModel.query.get(user["id"])

    return render_template(
        "empresa/editar_perfil.jinja2",
        empresa=empresa,
        usuario_empresa=usuario_empresa,
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
            
            # Si se contrata alguien, cerrar automáticamente la vacante
            if nuevo_estado == 'contratado':
                vacante = postulacion.vacante
                if vacante and vacante.estado == 'publicada':
                    vacante.estado = 'cerrada'
                    flash(f"Estado actualizado a: {nuevo_estado}. La vacante ha sido cerrada automáticamente.", "success")
                else:
                    flash(f"Estado actualizado a: {nuevo_estado}", "success")
            else:
                flash(f"Estado actualizado a: {nuevo_estado}", "success")
        
        db.session.commit()
    else:
        flash("Estado inválido", "danger")
    
    return redirect(url_for("rt_empresa.ver_candidato", candidato_id=postulacion.empleado_id))


# Ruta para mensajes de empresa
@rt_empresa.route("/mensajes")
@login_role_required(Roles.EMPRESA)
def mensajes_empresa():
    user = get_user_from_session(session)
    if not user:
        return redirect(url_for("IndexRoute.index"))
    
    # Obtener lista de conversaciones únicas (usuarios con los que ha chateado)
    conversaciones = db.session.query(
        UsuarioModel.id,
        UsuarioModel.nombre,
        UsuarioModel.tipo_usuario,
        db.func.max(MensajeModel.fecha_envio).label('ultima_fecha')
    ).join(
        MensajeModel,
        or_(
            and_(MensajeModel.remitente_id == UsuarioModel.id, MensajeModel.destinatario_id == user['id']),
            and_(MensajeModel.destinatario_id == UsuarioModel.id, MensajeModel.remitente_id == user['id'])
        )
    ).filter(
        UsuarioModel.id != user['id']
    ).group_by(
        UsuarioModel.id, UsuarioModel.nombre, UsuarioModel.tipo_usuario
    ).order_by(
        desc('ultima_fecha')
    ).all()
    
    # Obtener empleados que se han postulado a vacantes de esta empresa
    empleados_disponibles = db.session.query(UsuarioModel).join(
        EmpleadoModel, UsuarioModel.id == EmpleadoModel.id
    ).join(
        PostulacionModel, EmpleadoModel.id == PostulacionModel.empleado_id
    ).join(
        VacanteModel, PostulacionModel.vacante_id == VacanteModel.id
    ).filter(
        VacanteModel.empresa_id == user['id'],
        UsuarioModel.tipo_usuario == 'empleado'
    ).distinct().all()
    
    return render_template(
        "empresa/mensajes_empresa.jinja2",
        usuario=user,
        conversaciones=conversaciones,
        empleados_disponibles=empleados_disponibles
    )


@rt_empresa.route("/mensajes/conversacion/<int:destinatario_id>")
@login_role_required(Roles.EMPRESA)
def obtener_conversacion_empresa(destinatario_id):
    user = get_user_from_session(session)
    if not user:
        return jsonify({"error": "No autenticado"}), 401
    
    # Obtener mensajes entre el usuario actual y el destinatario
    mensajes_list = MensajeModel.query.filter(
        or_(
            and_(MensajeModel.remitente_id == user['id'], MensajeModel.destinatario_id == destinatario_id),
            and_(MensajeModel.remitente_id == destinatario_id, MensajeModel.destinatario_id == user['id'])
        )
    ).order_by(MensajeModel.fecha_envio.asc()).all()
    
    # Marcar mensajes como leídos
    MensajeModel.query.filter(
        MensajeModel.remitente_id == destinatario_id,
        MensajeModel.destinatario_id == user['id'],
        MensajeModel.leido == False
    ).update({"leido": True})
    db.session.commit()
    
    # Obtener información del destinatario
    destinatario = UsuarioModel.query.get(destinatario_id)
    
    return jsonify({
        "mensajes": [{
            "id": m.id,
            "contenido": m.contenido,
            "remitente_id": m.remitente_id,
            "fecha_envio": m.fecha_envio.strftime('%H:%M') if m.fecha_envio else '',
            "es_mio": m.remitente_id == user['id']
        } for m in mensajes_list],
        "destinatario": {
            "id": destinatario.id,
            "nombre": destinatario.nombre,
            "tipo_usuario": destinatario.tipo_usuario
        }
    })


@rt_empresa.route("/mensajes/enviar", methods=["POST"])
@login_role_required(Roles.EMPRESA)
def enviar_mensaje_empresa():
    user = get_user_from_session(session)
    if not user:
        return jsonify({"error": "No autenticado"}), 401
    
    data = request.get_json()
    destinatario_id = data.get('destinatario_id')
    contenido = data.get('contenido')
    
    if not destinatario_id or not contenido:
        return jsonify({"error": "Datos incompletos"}), 400
    
    # Crear mensaje
    nuevo_mensaje = MensajeModel(
        remitente_id=user['id'],
        destinatario_id=destinatario_id,
        contenido=contenido,
        leido=False,
        fecha_envio=get_mexico_time()
    )
    db.session.add(nuevo_mensaje)
    
    # Crear notificación para el destinatario
    empresa = EmpresaModel.query.get(user['id'])
    nombre_empresa = empresa.nombre_empresa if empresa else user['nombre']
    
    notificacion = NotificacionModel(
        usuario_id=destinatario_id,
        mensaje=f"💬 Nuevo mensaje de {nombre_empresa}",
        tipo='mensaje',
        leido=False,
        fecha_envio=get_mexico_time()
    )
    db.session.add(notificacion)
    
    db.session.commit()
    
    return jsonify({
        "success": True,
        "mensaje": {
            "id": nuevo_mensaje.id,
            "contenido": nuevo_mensaje.contenido,
            "fecha_envio": nuevo_mensaje.fecha_envio.strftime('%H:%M'),
            "es_mio": True
        }
    })


@rt_empresa.route("/api/mensajes/contador")
@login_role_required(Roles.EMPRESA)
def contador_mensajes_empresa():
    """API endpoint para obtener el contador de mensajes no leídos en tiempo real"""
    user = get_user_from_session(session)
    if not user:
        return jsonify({"count": 0})
    
    count = contar_mensajes_no_leidos(user['id'])
    return jsonify({"count": count})


@rt_empresa.route("/notificaciones")
@login_role_required(Roles.EMPRESA)
def notificaciones_empresa():
    """Vista de notificaciones para empresas"""
    user = get_user_from_session(session)
    if not user:
        return redirect(url_for("IndexRoute.index"))
    
    # Obtener todas las notificaciones del usuario ordenadas por fecha
    notificaciones_list = NotificacionModel.query.filter_by(usuario_id=user['id']) \
        .order_by(desc(NotificacionModel.fecha_envio)) \
        .all()
    
    # Contar notificaciones no leídas
    no_leidas = NotificacionModel.query.filter_by(usuario_id=user['id'], leido=False).count()
    
    return render_template(
        "empresa/notificaciones_empresa.jinja2",
        usuario=user,
        notificaciones=notificaciones_list,
        no_leidas=no_leidas
    )


@rt_empresa.route("/notificaciones/marcar_todas_leidas", methods=["POST"])
@login_role_required(Roles.EMPRESA)
def marcar_todas_leidas_empresa():
    """Marcar todas las notificaciones como leídas"""
    user = get_user_from_session(session)
    if not user:
        return redirect(url_for("IndexRoute.index"))
    
    NotificacionModel.query.filter_by(usuario_id=user['id'], leido=False) \
        .update({'leido': True})
    db.session.commit()
    
    return redirect(url_for('rt_empresa.notificaciones_empresa'))


@rt_empresa.route("/notificaciones/eliminar_todas", methods=["POST"])
@login_role_required(Roles.EMPRESA)
def eliminar_todas_notificaciones_empresa():
    """Eliminar todas las notificaciones"""
    user = get_user_from_session(session)
    if not user:
        return redirect(url_for("IndexRoute.index"))
    
    NotificacionModel.query.filter_by(usuario_id=user['id']).delete()
    db.session.commit()
    
    return redirect(url_for('rt_empresa.notificaciones_empresa'))


def generar_reporte_html_content(user, vacantes, postulaciones, ofertas_activas, contratados, en_proceso, rechazados, vistos, postulados):
    """Función auxiliar para generar contenido HTML del reporte"""
    from datetime import datetime
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Reporte de Postulaciones - WorkLink</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ 
                font-family: 'Inter', 'Segoe UI', sans-serif; 
                background: #ffffff; 
                color: #1e293b; 
                line-height: 1.6; 
                padding: 40px;
            }}
            .header {{ 
                text-align: center; 
                border-bottom: 3px solid #3b82f6; 
                padding-bottom: 30px; 
                margin-bottom: 40px;
                background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
                padding: 40px 20px;
                border-radius: 12px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            }}
            .header h1 {{ 
                color: #0f172a; 
                font-size: 2.5rem;
                font-weight: 800;
                margin-bottom: 10px;
            }}
            .header p {{ 
                color: #64748b; 
                margin: 5px 0;
                font-size: 1rem;
            }}
            .company-name {{
                color: #3b82f6;
                font-weight: 700;
                font-size: 1.2rem;
            }}
            .section {{ 
                margin: 40px 0; 
            }}
            .section h2 {{ 
                color: #0f172a; 
                font-size: 1.5rem; 
                font-weight: 700; 
                margin-bottom: 20px; 
                padding-bottom: 10px; 
                border-bottom: 2px solid #e2e8f0; 
            }}
            .stats-grid {{ 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                gap: 20px; 
                margin: 20px 0; 
            }}
            .stat-box {{ 
                background: #ffffff; 
                border: 2px solid #e2e8f0; 
                border-radius: 12px; 
                padding: 25px; 
                text-align: center; 
                transition: all 0.3s ease;
                box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            }}
            .stat-box:hover {{
                transform: translateY(-5px);
                box-shadow: 0 8px 20px rgba(59,130,246,0.15);
                border-color: #3b82f6;
            }}
            .stat-box .number {{ 
                font-size: 2.5rem; 
                font-weight: 800; 
                color: #3b82f6; 
                margin-bottom: 8px;
                display: block;
            }}
            .stat-box .label {{
                color: #64748b;
                font-weight: 600;
                font-size: 0.95rem;
            }}
            .stat-success .number {{ color: #10b981; }}
            .stat-warning .number {{ color: #f59e0b; }}
            .stat-danger .number {{ color: #ef4444; }}
            table {{ 
                width: 100%; 
                border-collapse: collapse; 
                margin-top: 20px; 
                background: #ffffff;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            }}
            th, td {{ 
                border: 1px solid #e2e8f0; 
                padding: 15px 20px; 
                text-align: left; 
            }}
            th {{ 
                background: linear-gradient(135deg, #1e40af, #3b82f6); 
                color: white; 
                font-weight: 700;
                font-size: 0.95rem;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            tr:nth-child(even) {{ 
                background: #f8fafc; 
            }}
            tr:hover {{
                background: #f1f5f9;
            }}
            td {{ 
                color: #475569; 
                font-size: 0.95rem;
            }}
            .footer {{ 
                text-align: center; 
                margin-top: 60px; 
                padding-top: 30px;
                border-top: 2px solid #e2e8f0;
                color: #94a3b8; 
                font-size: 0.9rem;
            }}
            .footer strong {{ 
                color: #3b82f6;
                font-weight: 700;
            }}
            @media print {{ 
                body {{ 
                    padding: 20px; 
                }}
                .stat-box:hover {{
                    transform: none;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📊 Reporte de Postulaciones</h1>
            <p><strong>Generado:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
            <p class="company-name">🏢 {user.get('nombre', 'N/A')}</p>
        </div>
        
        <div class="section">
        <h2>📈 Resumen General</h2>
        <div class="stats-grid">
                <div class="stat-box">
                    <div class="number">{ofertas_activas}</div>
                    <div class="label">Ofertas Activas</div>
                </div>
                <div class="stat-box">
                    <div class="number">{len(postulaciones)}</div>
                    <div class="label">Total Postulaciones</div>
                </div>
                <div class="stat-box">
                    <div class="number">{len(vacantes)}</div>
                    <div class="label">Total Vacantes</div>
                </div>
            </div>
        </div>
        
        <div class="section">
        <h2>📊 Estado de Postulaciones</h2>
        <div class="stats-grid">
                <div class="stat-box stat-success">
                    <div class="number">✓ {contratados}</div>
                    <div class="label">Contratados</div>
                </div>
                <div class="stat-box stat-warning">
                    <div class="number">⏳ {en_proceso}</div>
                    <div class="label">En Proceso</div>
                </div>
                <div class="stat-box stat-danger">
                    <div class="number">✗ {rechazados}</div>
                    <div class="label">Rechazados</div>
                </div>
            </div>
        </div>
        
        <div class="section">
        <h2>💼 Vacantes Publicadas</h2>
        <table>
                <thead>
                    <tr>
                        <th>Título de la Vacante</th>
                        <th>Estado</th>
                        <th>Postulaciones</th>
                        <th>Fecha</th>
                    </tr>
                </thead>
            <tbody>
    """
    
    for vacante in vacantes:
        postulaciones_vacante = sum(1 for p in postulaciones if p.vacante_id == vacante.id)
        fecha = vacante.fecha_publicacion.strftime('%d/%m/%Y') if vacante.fecha_publicacion else 'N/A'
        html_content += f"<tr><td>{vacante.titulo}</td><td>{vacante.estado}</td><td>{postulaciones_vacante}</td><td>{fecha}</td></tr>"
    
    html_content += """
            </tbody>
        </table>
        </div>
        
        <div class="footer">
            <strong>WorkLink</strong> - Sistema de Gestión de Empleo<br>
            <small>Reporte generado automáticamente</small>
        </div>
    </body>
    </html>
    """
    
    return html_content


def generar_reporte_html(user, vacantes, postulaciones, ofertas_activas, contratados, en_proceso, rechazados, vistos, postulados):
    """Función auxiliar para generar reporte en HTML si reportlab no está disponible"""
    from flask import make_response
    from datetime import datetime
    
    html_content = generar_reporte_html_content(user, vacantes, postulaciones, ofertas_activas, 
                                               contratados, en_proceso, rechazados, vistos, postulados)
    
    response = make_response(html_content)
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    response.headers['Content-Disposition'] = 'inline; filename="reporte.html"'
    return response


@rt_empresa.route("/generar_reporte", methods=['GET', 'POST'])
@login_role_required(Roles.EMPRESA)
def generar_reporte():
    """Generar reporte en PDF con estadísticas de la empresa"""
    from flask import make_response, send_file
    from datetime import datetime
    from io import BytesIO
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    
    user = get_user_from_session(session)
    if not user:
        return redirect(url_for("IndexRoute.index"))
    
    # Obtener datos para el reporte
    vacantes = VacanteModel.query.filter_by(empresa_id=user["id"]).all()
    ofertas_activas = VacanteModel.query.filter_by(empresa_id=user["id"], estado="publicada").count()
    
    postulaciones = db.session.query(PostulacionModel).join(VacanteModel).filter(
        VacanteModel.empresa_id == user["id"]
    ).all()
    
    # Estadísticas por estado
    contratados = sum(1 for p in postulaciones if p.estado == 'contratado')
    en_proceso = sum(1 for p in postulaciones if p.estado == 'en_proceso')
    rechazados = sum(1 for p in postulaciones if p.estado == 'rechazado')
    vistos = sum(1 for p in postulaciones if p.estado == 'visto')
    postulados = sum(1 for p in postulaciones if p.estado == 'postulado')
    total_postulaciones = len(postulaciones)
    
    # Crear un objeto BytesIO para el PDF
    buffer = BytesIO()
    
    # Crear el documento PDF
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=20,
        textColor=colors.HexColor('#2c3e50')
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=10,
        textColor=colors.HexColor('#3498db')
    )
    
    normal_style = styles['Normal']
    
    # Contenido del PDF
    content = []
    
    # Título
    content.append(Paragraph("Reporte de Postulaciones", title_style))
    content.append(Paragraph(f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    content.append(Paragraph(f"Empresa: {user.get('nombre', 'N/A')}", styles['Normal']))
    content.append(Spacer(1, 20))
    
    # Resumen de estadísticas
    content.append(Paragraph("Resumen de Estadísticas", subtitle_style))
    
    # Tabla de estadísticas
    stats_data = [
        ['Métrica', 'Cantidad'],
        ['Total de vacantes', len(vacantes)],
        ['Ofertas activas', ofertas_activas],
        ['Total de postulaciones', total_postulaciones],
        ['Postulados', postulados],
        ['Vistos', vistos],
        ['En proceso', en_proceso],
        ['Contratados', contratados],
        ['Rechazados', rechazados]
    ]
    
    # Crear tabla de estadísticas
    stats_table = Table(stats_data, colWidths=[doc.width/2.0]*2)
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#6c757d')),
    ]))
    
    content.append(stats_table)
    content.append(Spacer(1, 20))
    
    # Detalle de vacantes
    if vacantes:
        content.append(Paragraph("Vacantes Publicadas", subtitle_style))
        
        vacantes_data = [['Título', 'Estado', 'Postulaciones']]
        for vacante in vacantes[:10]:  # Mostrar solo las 10 primeras vacantes
            vacantes_data.append([
                vacante.titulo,
                vacante.estado,
                len(vacante.postulaciones)
            ])
        
        vacantes_table = Table(vacantes_data, colWidths=[doc.width*0.5, doc.width*0.25, doc.width*0.25])
        vacantes_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6c757d')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#6c757d')),
        ]))
        
        content.append(vacantes_table)
        if len(vacantes) > 10:
            content.append(Paragraph(f"... y {len(vacantes) - 10} vacantes más", styles['Italic']))
    
    # Pie de página
    content.append(Spacer(1, 20))
    content.append(Paragraph("WorkLink - Sistema de Gestión de Empleo", styles['Italic']))
    content.append(Paragraph("Reporte generado automáticamente", styles['Italic']))
    
    # Construir el PDF
    doc.build(content)
    
    # Preparar la respuesta para descargar el PDF
    buffer.seek(0)
    response = make_response(buffer.getvalue())
    response.mimetype = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=reporte_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    
    return response


@rt_empresa.route("/api/notificaciones/contador")
@login_role_required(Roles.EMPRESA)
def contador_notificaciones_empresa():
    """API endpoint para obtener el contador de notificaciones no leídas en tiempo real"""
    user = get_user_from_session(session)
    if not user:
        return jsonify({"count": 0})
    
    count = NotificacionModel.query.filter_by(usuario_id=user['id'], leido=False).count()
    return jsonify({"count": count})
