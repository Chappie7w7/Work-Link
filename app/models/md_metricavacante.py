from app.db.sql import db
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

class MetricaVacanteModel(db.Model):
    __tablename__ = 'metricas_vacante'

    id = Column(Integer, primary_key=True, autoincrement=True)
    vacante_id = Column(Integer, ForeignKey('vacantes.id'), nullable=True)
    vistas = Column(Integer, nullable=True)
    postulaciones = Column(Integer, nullable=True)
    fecha_ultimo_reporte = Column(DateTime, nullable=True)

    # Relación con el modelo VacanteModel
    vacante = relationship('VacanteModel', backref='metricas')

    def __init__(self, vacante_id=None, vistas=None, postulaciones=None, fecha_ultimo_reporte=None):
        self.vacante_id = vacante_id
        self.vistas = vistas
        self.postulaciones = postulaciones
        self.fecha_ultimo_reporte = fecha_ultimo_reporte or datetime.utcnow()

    def to_json(self):
        return {
            "id": self.id,
            "vacante_id": self.vacante_id,
            "vistas": self.vistas,
            "postulaciones": self.postulaciones,
            "fecha_ultimo_reporte": self.fecha_ultimo_reporte.isoformat() if self.fecha_ultimo_reporte else None
        }
