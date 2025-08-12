from app.db.sql import db
from sqlalchemy import Column, Integer, DateTime, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

class PostulacionModel(db.Model):
    __tablename__ = 'postulaciones'

    id = Column(Integer, primary_key=True, autoincrement=True)
    vacante_id = Column(Integer, ForeignKey('vacantes.id'), nullable=True)
    empleado_id = Column(Integer, ForeignKey('empleados.id'), nullable=True)
    fecha_postulacion = Column(DateTime, nullable=True)
    estado = Column(Enum('postulado', 'visto', 'en_proceso', 'rechazado', 'contratado'), nullable=True)
    notas_empresa = Column(Text, nullable=True)

    # Relaciones
    vacante = relationship('VacanteModel', backref='postulaciones')
    empleado = relationship('EmpleadoModel', backref='postulaciones')

    def __init__(self, vacante_id=None, empleado_id=None, fecha_postulacion=None, estado=None, notas_empresa=None):
        self.vacante_id = vacante_id
        self.empleado_id = empleado_id
        self.fecha_postulacion = fecha_postulacion or datetime.utcnow()
        self.estado = estado
        self.notas_empresa = notas_empresa

    def to_json(self):
        return {
            "id": self.id,
            "vacante_id": self.vacante_id,
            "empleado_id": self.empleado_id,
            "fecha_postulacion": self.fecha_postulacion.isoformat() if self.fecha_postulacion else None,
            "estado": self.estado,
            "notas_empresa": self.notas_empresa
        }
