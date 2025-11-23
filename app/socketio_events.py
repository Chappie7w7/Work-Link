"""
Eventos de Socket.IO para notificaciones y mensajes en tiempo real
"""
from flask import session, request
from flask_socketio import emit, join_room, leave_room
from app.db.sql import db
from app.models.md_notificacion import NotificacionModel
from app.models.md_mensaje import MensajeModel


def register_socketio_events(socketio):
    """Registra todos los eventos de Socket.IO"""
    
    @socketio.on('connect', namespace='/notificaciones')
    def handle_connect_notificaciones():
        """Maneja la conexión del cliente al namespace de notificaciones"""
        usuario = session.get('usuario')
        if usuario:
            # Unirse a la sala del usuario para recibir notificaciones personalizadas
            room = f"usuario_{usuario['id']}"
            join_room(room)
            print(f"Usuario {usuario['id']} conectado a notificaciones en sala {room}")
            emit('conectado', {'mensaje': 'Conectado a notificaciones en tiempo real'})
        else:
            emit('error', {'mensaje': 'No autenticado'})
            return False
    
    @socketio.on('disconnect', namespace='/notificaciones')
    def handle_disconnect_notificaciones():
        """Maneja la desconexión del cliente"""
        usuario = session.get('usuario')
        if usuario:
            room = f"usuario_{usuario['id']}"
            leave_room(room)
            print(f"Usuario {usuario['id']} desconectado de notificaciones")
    
    @socketio.on('connect', namespace='/mensajes')
    def handle_connect_mensajes():
        """Maneja la conexión del cliente al namespace de mensajes"""
        usuario = session.get('usuario')
        if usuario:
            room = f"usuario_{usuario['id']}"
            join_room(room)
            print(f"Usuario {usuario['id']} conectado a mensajes en sala {room}")
            emit('conectado', {'mensaje': 'Conectado a mensajes en tiempo real'})
        else:
            emit('error', {'mensaje': 'No autenticado'})
            return False
    
    @socketio.on('disconnect', namespace='/mensajes')
    def handle_disconnect_mensajes():
        """Maneja la desconexión del cliente de mensajes"""
        usuario = session.get('usuario')
        if usuario:
            room = f"usuario_{usuario['id']}"
            leave_room(room)
            print(f"Usuario {usuario['id']} desconectado de mensajes")
    
    @socketio.on('marcar_notificacion_leida', namespace='/notificaciones')
    def handle_marcar_notificacion_leida(data):
        """Marca una notificación como leída"""
        usuario = session.get('usuario')
        if not usuario:
            emit('error', {'mensaje': 'No autenticado'})
            return
        
        notificacion_id = data.get('notificacion_id')
        if notificacion_id:
            notificacion = NotificacionModel.query.get(notificacion_id)
            if notificacion and notificacion.usuario_id == usuario['id']:
                notificacion.leido = True
                db.session.commit()
                emit('notificacion_marcada', {'notificacion_id': notificacion_id})


def enviar_notificacion_tiempo_real(usuario_id, datos_notificacion):
    """
    Envía una notificación en tiempo real a un usuario específico
    """
    from app.extensiones import socketio
    
    room = f"usuario_{usuario_id}"
    socketio.emit('nueva_notificacion', datos_notificacion, 
                  room=room, namespace='/notificaciones')


def enviar_mensaje_tiempo_real(usuario_id, datos_mensaje):
    """
    Envía un mensaje en tiempo real a un usuario específico
    """
    from app.extensiones import socketio
    
    room = f"usuario_{usuario_id}"
    socketio.emit('nuevo_mensaje', datos_mensaje, 
                  room=room, namespace='/mensajes')

