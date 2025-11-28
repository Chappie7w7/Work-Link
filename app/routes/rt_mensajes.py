from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from app.utils.decorators import login_role_required
from app.utils.roles import Roles
from app.models.md_mensaje import MensajeModel
from app.models.md_usuarios import UsuarioModel
from app.models.md_empresas import EmpresaModel
from app.models.md_empleados import EmpleadoModel
from app.models.md_notificacion import NotificacionModel
from app.db.sql import db
from sqlalchemy import or_, and_, desc
from app.utils.timezone_helper import get_mexico_time
from app.utils.mensaje_helper import contar_mensajes_no_leidos

rt_mensajes = Blueprint('MensajesRoute', __name__)

@rt_mensajes.route("/mensajes")
def mensajes():
    usuario = session.get('usuario')
    if not usuario:
        return redirect(url_for('IndexRoute.index'))
    
    # Obtener lista de conversaciones únicas (usuarios con los que ha chateado)
    conversaciones = db.session.query(
        UsuarioModel.id,
        UsuarioModel.nombre,
        UsuarioModel.tipo_usuario,
        db.func.max(MensajeModel.fecha_envio).label('ultima_fecha')
    ).join(
        MensajeModel,
        or_(
            and_(MensajeModel.remitente_id == UsuarioModel.id, MensajeModel.destinatario_id == usuario['id']),
            and_(MensajeModel.destinatario_id == UsuarioModel.id, MensajeModel.remitente_id == usuario['id'])
        )
    ).filter(
        UsuarioModel.id != usuario['id']
    ).group_by(
        UsuarioModel.id, UsuarioModel.nombre, UsuarioModel.tipo_usuario
    ).order_by(
        desc('ultima_fecha')
    ).all()
    
    # Obtener empresas disponibles para iniciar conversación
    empresas_disponibles = db.session.query(UsuarioModel).join(
        EmpresaModel, UsuarioModel.id == EmpresaModel.id
    ).filter(
        UsuarioModel.tipo_usuario == 'empresa'
    ).all()
    
    return render_template(
        "mensajes/mensajes.jinja2",
        usuario=usuario,
        current_user=usuario,
        conversaciones=conversaciones,
        empresas_disponibles=empresas_disponibles
    )


@rt_mensajes.route("/mensajes/conversacion/<int:destinatario_id>")
def obtener_conversacion(destinatario_id):
    usuario = session.get('usuario')
    if not usuario:
        return jsonify({"error": "No autenticado"}), 401
    
    # Obtener mensajes entre el usuario actual y el destinatario
    mensajes_list = MensajeModel.query.filter(
        or_(
            and_(MensajeModel.remitente_id == usuario['id'], MensajeModel.destinatario_id == destinatario_id),
            and_(MensajeModel.remitente_id == destinatario_id, MensajeModel.destinatario_id == usuario['id'])
        )
    ).order_by(MensajeModel.fecha_envio.asc()).all()
    
    # Marcar mensajes como leídos
    MensajeModel.query.filter(
        MensajeModel.remitente_id == destinatario_id,
        MensajeModel.destinatario_id == usuario['id'],
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
            "es_mio": m.remitente_id == usuario['id']
        } for m in mensajes_list],
        "destinatario": {
            "id": destinatario.id,
            "nombre": destinatario.nombre,
            "tipo_usuario": destinatario.tipo_usuario
        }
    })


@rt_mensajes.route("/mensajes/enviar", methods=["POST"])
def enviar_mensaje():
    usuario = session.get('usuario')
    if not usuario:
        return jsonify({"error": "No autenticado"}), 401
    
    data = request.get_json()
    destinatario_id = data.get('destinatario_id')
    contenido = data.get('contenido')
    
    if not destinatario_id or not contenido:
        return jsonify({"error": "Datos incompletos"}), 400
    
    # Crear mensaje
    nuevo_mensaje = MensajeModel(
        remitente_id=usuario['id'],
        destinatario_id=destinatario_id,
        contenido=contenido,
        leido=False,
        fecha_envio=get_mexico_time()
    )
    db.session.add(nuevo_mensaje)
    
    # Crear notificación para el destinatario
    notificacion = NotificacionModel(
        usuario_id=destinatario_id,
        mensaje=f"💬 Nuevo mensaje de {usuario['nombre']}",
        tipo='mensaje',
        leido=False,
        fecha_envio=get_mexico_time()
    )
    db.session.add(notificacion)
    db.session.flush()  # Para obtener el ID
    
    # Enviar notificación y mensaje en tiempo real usando WebSockets
    try:
        from app.socketio_events import enviar_notificacion_tiempo_real, enviar_mensaje_tiempo_real
        enviar_notificacion_tiempo_real(destinatario_id, {
            'id': notificacion.id,
            'usuario_id': destinatario_id,
            'mensaje': notificacion.mensaje,
            'tipo': 'mensaje',
            'leido': False,
            'fecha_envio': notificacion.fecha_envio.isoformat()
        })
        enviar_mensaje_tiempo_real(destinatario_id, {
            'id': nuevo_mensaje.id,
            'remitente_id': usuario['id'],
            'destinatario_id': destinatario_id,
            'contenido': nuevo_mensaje.contenido,
            'fecha_envio': nuevo_mensaje.fecha_envio.isoformat(),
            'leido': False
        })
    except Exception as e:
        print(f"Error al enviar notificación/mensaje en tiempo real: {str(e)}")
    
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


@rt_mensajes.route("/api/mensajes/contador")
def contador_mensajes():
    """API endpoint para obtener el contador de mensajes no leídos en tiempo real"""
    usuario = session.get('usuario')
    if not usuario:
        return jsonify({"count": 0})
    
    count = contar_mensajes_no_leidos(usuario['id'])
    return jsonify({"count": count})
