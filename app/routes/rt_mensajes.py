from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from app.utils.decorators import login_role_required
from app.utils.roles import Roles
from app.models.md_mensaje import MensajeModel
from app.models.md_usuarios import UsuarioModel
from app.models.md_empresas import EmpresaModel
from app.models.md_notificacion import NotificacionModel
from app.db.sql import db
from sqlalchemy import or_, and_, desc
from app.utils.timezone_helper import get_mexico_time
from app.utils.mensaje_helper import contar_mensajes_no_leidos
from app.utils.pusher_client import pusher_client

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
        UsuarioModel.foto_perfil,
        EmpresaModel.logo_url.label('logo_url'),
        EmpresaModel.nombre_empresa.label('nombre_empresa'),
        db.func.max(MensajeModel.fecha_envio).label('ultima_fecha')
    ).outerjoin(
        EmpresaModel, EmpresaModel.id == UsuarioModel.id
    ).join(
        MensajeModel,
        or_(
            and_(MensajeModel.remitente_id == UsuarioModel.id, MensajeModel.destinatario_id == usuario['id']),
            and_(MensajeModel.destinatario_id == UsuarioModel.id, MensajeModel.remitente_id == usuario['id'])
        )
    ).filter(
        UsuarioModel.id != usuario['id']
    ).group_by(
        UsuarioModel.id, UsuarioModel.nombre, UsuarioModel.tipo_usuario, UsuarioModel.foto_perfil, EmpresaModel.logo_url, EmpresaModel.nombre_empresa
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
    
    # Marcar mensajes como leídos ANTES de consultar (para que el contador baje al abrir)
    MensajeModel.query.filter(
        MensajeModel.remitente_id == destinatario_id,
        MensajeModel.destinatario_id == usuario['id'],
        MensajeModel.leido == False
    ).update({"leido": True}, synchronize_session=False)
    db.session.commit()

    # Obtener mensajes entre el usuario actual y el destinatario
    mensajes_list = MensajeModel.query.filter(
        or_(
            and_(MensajeModel.remitente_id == usuario['id'], MensajeModel.destinatario_id == destinatario_id),
            and_(MensajeModel.remitente_id == destinatario_id, MensajeModel.destinatario_id == usuario['id'])
        )
    ).order_by(MensajeModel.fecha_envio.asc()).all()
    
    # Obtener información del destinatario
    destinatario = UsuarioModel.query.get(destinatario_id)
    logo_url = None
    nombre_mostrar = destinatario.nombre if destinatario else ''
    foto = destinatario.foto_perfil if destinatario else None
    if destinatario and destinatario.tipo_usuario == 'empresa':
        emp = EmpresaModel.query.get(destinatario_id)
        if emp:
            logo_url = emp.logo_url
            nombre_mostrar = emp.nombre_empresa or destinatario.nombre
    
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
            "tipo_usuario": destinatario.tipo_usuario,
            "nombre_mostrar": nombre_mostrar,
            "foto_perfil": foto,
            "logo_url": logo_url
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
    
    # Enviar evento en tiempo real via Pusher Channels
    try:
        channel = f"private-chat-{destinatario_id}"
        event = "new-message"
        payload = {
            'user': {
                'id': usuario['id'],
                'nombre': usuario.get('nombre')
            },
            'message': nuevo_mensaje.contenido,
            'timestamp': nuevo_mensaje.fecha_envio.isoformat(),
            'mensaje': {
                'id': nuevo_mensaje.id,
                'remitente_id': usuario['id'],
                'destinatario_id': destinatario_id
            }
        }
        pusher_client.trigger(channel, event, payload)
    except Exception as e:
        print(f"Error al emitir evento Pusher: {str(e)}")
    
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


@rt_mensajes.route("/mensajes/marcar_leidos", methods=["POST"])
def marcar_leidos_en_tiempo_real():
    usuario = session.get('usuario')
    if not usuario:
        return jsonify({"success": False}), 401
    data = request.get_json() or {}
    remitente_id = data.get('remitente_id')
    if not remitente_id:
        return jsonify({"success": False, "error": "remitente_id requerido"}), 400
    try:
        MensajeModel.query.filter(
            MensajeModel.remitente_id == remitente_id,
            MensajeModel.destinatario_id == usuario['id'],
            MensajeModel.leido == False
        ).update({"leido": True}, synchronize_session=False)
        db.session.commit()
        return jsonify({"success": True})
    except Exception:
        db.session.rollback()
        return jsonify({"success": False}), 500
