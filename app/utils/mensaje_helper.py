"""
Helper para funciones relacionadas con mensajes
"""
from app.models.md_mensaje import MensajeModel

def contar_mensajes_no_leidos(usuario_id):
    """
    Cuenta los mensajes no leídos para un usuario
    
    Args:
        usuario_id: ID del usuario
        
    Returns:
        int: Número de mensajes no leídos
    """
    return MensajeModel.query.filter_by(
        destinatario_id=usuario_id,
        leido=False
    ).count()
