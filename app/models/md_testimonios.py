from app.db.sql import db
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from datetime import datetime
from app.utils.timezone_helper import get_mexico_time
from sqlalchemy.orm import relationship


class TestimonioModel(db.Model):
    __tablename__ = 'testimonios'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(120), nullable=False)
    cargo = Column(String(120), nullable=True)
    empresa = Column(String(120), nullable=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=True)
    mensaje = Column(Text, nullable=False)
    aprobado = Column(Boolean, default=False)
    fecha_publicacion = Column(DateTime, nullable=False)

    usuario = relationship('UsuarioModel', backref='testimonios')

    def __init__(self, nombre, mensaje, cargo=None, empresa=None, usuario_id=None, aprobado=False, fecha_publicacion=None):
        self.nombre = nombre
        self.mensaje = mensaje
        self.cargo = cargo
        self.empresa = empresa
        self.usuario_id = usuario_id
        self.aprobado = aprobado
        self.fecha_publicacion = fecha_publicacion or get_mexico_time()

    def to_json(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "cargo": self.cargo,
            "empresa": self.empresa,
            "mensaje": self.mensaje,
            "usuario_id": self.usuario_id,
            "usuario": self.usuario.to_json() if self.usuario else None,
            "aprobado": self.aprobado,
            "fecha_publicacion": self.fecha_publicacion.isoformat() if self.fecha_publicacion else None
        }
