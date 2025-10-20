from flask import Blueprint, render_template, session, redirect, url_for, request, flash, jsonify
from app.utils.decorators import login_role_required
from app.utils.roles import Roles
from app.controller.ctr_empleos import get_user_from_session
from app.db.sql import db
from app.models.md_vacantes import VacanteModel
from app.models.md_empresas import EmpresaModel
from app.models.md_postulacion import PostulacionModel
from app.models.md_empleados import EmpleadoModel
from app.models.md_mensaje import MensajeModel
from app.models.md_usuarios import UsuarioModel
from app.models.md_notificacion import NotificacionModel
from sqlalchemy import or_, and_, desc
from app.utils.timezone_helper import get_mexico_time
from app.utils.mensaje_helper import contar_mensajes_no_leidos

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

    return render_template(
        "empresa/empresa.jinja2",
        ofertas_activas=ofertas_activas,
        postulantes_totales=postulantes_totales,
        ofertas=vacantes_empresa,
        candidatos=postulantes,
        contratados=contratados,
        en_proceso=en_proceso,
        rechazados=rechazados,
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


def generar_reporte_html(user, vacantes, postulaciones, ofertas_activas, contratados, en_proceso, rechazados, vistos, postulados):
    """Función auxiliar para generar reporte en HTML si reportlab no está disponible"""
    from flask import make_response
    from datetime import datetime
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Reporte de Postulaciones</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; color: #333; }}
            .header {{ text-align: center; border-bottom: 3px solid #6366f1; padding-bottom: 20px; margin-bottom: 30px; }}
            .header h1 {{ color: #6366f1; margin: 0; }}
            .stats-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin: 20px 0; }}
            .stat-box {{ background: #f9fafb; border: 2px solid #e5e7eb; border-radius: 10px; padding: 20px; text-align: center; }}
            .stat-box .number {{ font-size: 36px; font-weight: bold; color: #6366f1; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ border: 1px solid #e5e7eb; padding: 12px; text-align: left; }}
            th {{ background: #6366f1; color: white; }}
            tr:nth-child(even) {{ background: #f9fafb; }}
            @media print {{ body {{ margin: 20px; }} }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📊 Reporte de Postulaciones</h1>
            <p>Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
            <p><strong>Empresa:</strong> {user.get('nombre', 'N/A')}</p>
        </div>
        
        <h2>📈 Resumen General</h2>
        <div class="stats-grid">
            <div class="stat-box"><div class="number">{ofertas_activas}</div><div>Ofertas Activas</div></div>
            <div class="stat-box"><div class="number">{len(postulaciones)}</div><div>Total Postulaciones</div></div>
            <div class="stat-box"><div class="number">{len(vacantes)}</div><div>Total Vacantes</div></div>
        </div>
        
        <h2>📊 Estado de Postulaciones</h2>
        <div class="stats-grid">
            <div class="stat-box"><div class="number" style="color: #10b981;">✅ {contratados}</div><div>Contratados</div></div>
            <div class="stat-box"><div class="number" style="color: #f59e0b;">⏳ {en_proceso}</div><div>En Proceso</div></div>
            <div class="stat-box"><div class="number" style="color: #ef4444;">❌ {rechazados}</div><div>Rechazados</div></div>
        </div>
        
        <h2>💼 Vacantes Publicadas</h2>
        <table>
            <thead><tr><th>Título</th><th>Estado</th><th>Postulaciones</th><th>Fecha</th></tr></thead>
            <tbody>
    """
    
    for vacante in vacantes:
        postulaciones_vacante = sum(1 for p in postulaciones if p.vacante_id == vacante.id)
        fecha = vacante.fecha_publicacion.strftime('%d/%m/%Y') if vacante.fecha_publicacion else 'N/A'
        html_content += f"<tr><td>{vacante.titulo}</td><td>{vacante.estado}</td><td>{postulaciones_vacante}</td><td>{fecha}</td></tr>"
    
    html_content += """
            </tbody>
        </table>
        <p style="text-align: center; margin-top: 50px; color: #666;">
            WorkLink - Sistema de Gestión de Empleo<br>
            <small>Para guardar como PDF: Ctrl+P → Guardar como PDF</small>
        </p>
    </body>
    </html>
    """
    
    response = make_response(html_content)
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    return response


@rt_empresa.route("/generar_reporte")
@login_role_required(Roles.EMPRESA)
def generar_reporte():
    """Generar reporte en PDF con estadísticas de la empresa"""
    from flask import make_response
    from datetime import datetime
    from io import BytesIO
    
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        REPORTLAB_AVAILABLE = True
    except ImportError:
        REPORTLAB_AVAILABLE = False
    
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
    
    # Si reportlab no está disponible, generar HTML
    if not REPORTLAB_AVAILABLE:
        return generar_reporte_html(user, vacantes, postulaciones, ofertas_activas, 
                                   contratados, en_proceso, rechazados, vistos, postulados)
    
    # Crear PDF en memoria
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#6366f1'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#4f46e5'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    normal_style = styles['Normal']
    center_style = ParagraphStyle('Center', parent=normal_style, alignment=TA_CENTER)
    
    # Contenido del PDF
    story = []
    
    # Header
    story.append(Paragraph("Reporte de Postulaciones", title_style))
    story.append(Paragraph(f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}", center_style))
    story.append(Paragraph(f"<b>Empresa:</b> {user.get('nombre', 'N/A')}", center_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Resumen General
    story.append(Paragraph("Resumen General", heading_style))
    data_resumen = [
        ['Ofertas Activas', 'Total Postulaciones', 'Total Vacantes'],
        [str(ofertas_activas), str(len(postulaciones)), str(len(vacantes))]
    ]
    table_resumen = Table(data_resumen, colWidths=[2*inch, 2*inch, 2*inch])
    table_resumen.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6366f1')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9fafb')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
        ('FONTSIZE', (0, 1), (-1, -1), 14),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica-Bold'),
    ]))
    story.append(table_resumen)
    story.append(Spacer(1, 0.3*inch))
    
    # Estado de Postulaciones
    story.append(Paragraph("Estado de Postulaciones", heading_style))
    data_estados = [
        ['Contratados', 'En Proceso', 'Rechazados', 'Vistos', 'Postulados'],
        [str(contratados), str(en_proceso), str(rechazados), str(vistos), str(postulados)]
    ]
    table_estados = Table(data_estados, colWidths=[1.2*inch]*5)
    table_estados.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6366f1')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9fafb')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
        ('FONTSIZE', (0, 1), (-1, -1), 14),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica-Bold'),
    ]))
    story.append(table_estados)
    story.append(Spacer(1, 0.3*inch))
    
    # Vacantes Publicadas
    story.append(Paragraph("Vacantes Publicadas", heading_style))
    data_vacantes = [['Titulo', 'Estado', 'Postulaciones', 'Fecha']]
    
    for vacante in vacantes:
        postulaciones_vacante = sum(1 for p in postulaciones if p.vacante_id == vacante.id)
        fecha = vacante.fecha_publicacion.strftime('%d/%m/%Y') if vacante.fecha_publicacion else 'N/A'
        data_vacantes.append([
            vacante.titulo[:30] + '...' if len(vacante.titulo) > 30 else vacante.titulo,
            vacante.estado,
            str(postulaciones_vacante),
            fecha
        ])
    
    table_vacantes = Table(data_vacantes, colWidths=[2.5*inch, 1.5*inch, 1.2*inch, 1.2*inch])
    table_vacantes.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6366f1')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
    ]))
    story.append(table_vacantes)
    story.append(Spacer(1, 0.5*inch))
    
    # Footer
    story.append(Paragraph("<br/><br/>WorkLink - Sistema de Gestion de Empleo", center_style))
    story.append(Paragraph("Este reporte es confidencial y solo para uso interno", center_style))
    
    # Construir PDF
    doc.build(story)
    
    # Preparar respuesta
    buffer.seek(0)
    pdf_data = buffer.getvalue()
    
    # Guardar en base de datos
    try:
        from app.models.md_reporte import ReporteModel
        nombre_archivo = f'reporte_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        
        nuevo_reporte = ReporteModel(
            empresa_id=user['id'],
            nombre_archivo=nombre_archivo,
            tipo_reporte='postulaciones',
            archivo_pdf=pdf_data,
            total_vacantes=len(vacantes),
            total_postulaciones=len(postulaciones),
            ofertas_activas=ofertas_activas,
            contratados=contratados,
            en_proceso=en_proceso,
            rechazados=rechazados
        )
        
        db.session.add(nuevo_reporte)
        db.session.commit()
    except Exception as e:
        print(f"Error al guardar reporte: {e}")
    
    response = make_response(pdf_data)
    response.headers['Content-Type'] = 'application/pdf'
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
