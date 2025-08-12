from app.db.sql import db
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

class NotificacionModel(db.Model):
    __tablename__ = 'notificaciones'

    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=True)
    mensaje = Column(Text, nullable=True)
    tipo = Column(String(50), nullable=True)
    leido = Column(Boolean, default=False)
    fecha_envio = Column(DateTime, nullable=True)

    # Relación con UsuarioModel
    usuario = relationship('UsuarioModel', backref='notificaciones')

    def __init__(self, usuario_id=None, mensaje=None, tipo=None, leido=False, fecha_envio=None):
        self.usuario_id = usuario_id
        self.mensaje = mensaje
        self.tipo = tipo
        self.leido = leido
        self.fecha_envio = fecha_envio or datetime.utcnow()

    def to_json(self):
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "mensaje": self.mensaje,
            "tipo": self.tipo,
            "leido": self.leido,
            "fecha_envio": self.fecha_envio.isoformat() if self.fecha_envio else None
        }
