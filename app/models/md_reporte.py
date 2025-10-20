from app.db.sql import db
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship
from datetime import datetime

class ReporteModel(db.Model):
    __tablename__ = 'reportes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    empresa_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    nombre_archivo = Column(String(255), nullable=False)
    tipo_reporte = Column(String(50), nullable=False, default='postulaciones')  # postulaciones, metricas, etc
    archivo_pdf = Column(LargeBinary, nullable=True)  # Almacenar el PDF
    fecha_generacion = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Datos del reporte (para referencia rápida)
    total_vacantes = Column(Integer, nullable=True)
    total_postulaciones = Column(Integer, nullable=True)
    ofertas_activas = Column(Integer, nullable=True)
    contratados = Column(Integer, nullable=True)
    en_proceso = Column(Integer, nullable=True)
    rechazados = Column(Integer, nullable=True)

    # Relación con empresa
    empresa = relationship('UsuarioModel', backref='reportes', foreign_keys=[empresa_id])

    def __init__(self, empresa_id, nombre_archivo, tipo_reporte='postulaciones', archivo_pdf=None,
                 total_vacantes=0, total_postulaciones=0, ofertas_activas=0, 
                 contratados=0, en_proceso=0, rechazados=0):
        self.empresa_id = empresa_id
        self.nombre_archivo = nombre_archivo
        self.tipo_reporte = tipo_reporte
        self.archivo_pdf = archivo_pdf
        self.total_vacantes = total_vacantes
        self.total_postulaciones = total_postulaciones
        self.ofertas_activas = ofertas_activas
        self.contratados = contratados
        self.en_proceso = en_proceso
        self.rechazados = rechazados
        self.fecha_generacion = datetime.utcnow()

    def to_json(self):
        return {
            "id": self.id,
            "empresa_id": self.empresa_id,
            "nombre_archivo": self.nombre_archivo,
            "tipo_reporte": self.tipo_reporte,
            "fecha_generacion": self.fecha_generacion.isoformat() if self.fecha_generacion else None,
            "total_vacantes": self.total_vacantes,
            "total_postulaciones": self.total_postulaciones,
            "ofertas_activas": self.ofertas_activas,
            "contratados": self.contratados,
            "en_proceso": self.en_proceso,
            "rechazados": self.rechazados
        }
