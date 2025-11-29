from app.db.sql import db
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from app.utils.timezone_helper import get_mexico_time


class ContactoModel(db.Model):
    __tablename__ = 'contactos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(120), nullable=False)
    correo = Column(String(180), nullable=False)
    mensaje = Column(Text, nullable=False)
    fecha_envio = Column(DateTime, nullable=False, default=get_mexico_time)
    leido = Column(Boolean, nullable=False, default=False)

    def __init__(self, nombre, correo, mensaje, fecha_envio=None):
        self.nombre = nombre
        self.correo = correo
        self.mensaje = mensaje
        self.fecha_envio = fecha_envio or get_mexico_time()

    def to_json(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "correo": self.correo,
            "mensaje": self.mensaje,
            "fecha_envio": self.fecha_envio.isoformat() if self.fecha_envio else None,
            "leido": self.leido
        }
