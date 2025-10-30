from app.db.sql import db
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.utils.timezone_helper import get_mexico_time

class MensajeModel(db.Model):
    __tablename__ = 'mensajes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    remitente_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    destinatario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    contenido = Column(Text, nullable=False)
    leido = Column(Boolean, default=False)
    fecha_envio = Column(DateTime, nullable=False)

    # Relaciones
    remitente = relationship('UsuarioModel', foreign_keys=[remitente_id], backref='mensajes_enviados')
    destinatario = relationship('UsuarioModel', foreign_keys=[destinatario_id], backref='mensajes_recibidos')

    def __init__(self, remitente_id, destinatario_id, contenido, leido=False, fecha_envio=None):
        self.remitente_id = remitente_id
        self.destinatario_id = destinatario_id
        self.contenido = contenido
        self.leido = leido
        self.fecha_envio = fecha_envio or get_mexico_time()

    def to_json(self):
        return {
            "id": self.id,
            "remitente_id": self.remitente_id,
            "destinatario_id": self.destinatario_id,
            "contenido": self.contenido,
            "leido": self.leido,
            "fecha_envio": self.fecha_envio.isoformat() if self.fecha_envio else None
        }
