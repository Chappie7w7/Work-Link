from app.db.sql import db
from sqlalchemy import Column, Integer, String, Text, Enum, Boolean, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.utils.timezone_helper import get_mexico_time

class VacanteModel(db.Model):
    __tablename__ = 'vacantes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    empresa_id = Column(Integer, ForeignKey('empresas.id'), nullable=True)
    titulo = Column(String(150), nullable=True)
    descripcion = Column(Text, nullable=True)
    requisitos = Column(Text, nullable=True)
    fecha_publicacion = Column(DateTime, nullable=True)
    ubicacion = Column(String(255), nullable=True)
    estado = Column(Enum('publicada', 'cerrada', 'pausada'), nullable=True)
    destacada = Column(Boolean, default=False)
    salario_aprox = Column(Numeric(10, 2), nullable=True)
    modalidad = Column(Enum('presencial', 'remoto', 'híbrido'), nullable=True)
    max_postulantes = Column(Integer, nullable=True, default=None)
    postulantes_actuales = Column(Integer, default=0, nullable=False)
    eliminada = Column(Boolean, default=False, nullable=False)

   
    empresa = relationship('EmpresaModel', backref='vacantes')

    def __init__(self, empresa_id=None, titulo=None, descripcion=None, requisitos=None,
                 fecha_publicacion=None, ubicacion=None, estado=None, destacada=False,
                 salario_aprox=None, modalidad=None, max_postulantes=None, 
                 postulantes_actuales=0, eliminada=False):
        self.empresa_id = empresa_id
        self.titulo = titulo
        self.descripcion = descripcion
        self.requisitos = requisitos
        self.fecha_publicacion = fecha_publicacion or get_mexico_time()
        self.ubicacion = ubicacion
        self.estado = estado
        self.destacada = destacada
        self.salario_aprox = salario_aprox
        self.modalidad = modalidad
        self.max_postulantes = max_postulantes
        self.postulantes_actuales = postulantes_actuales
        self.eliminada = eliminada

    def disponible_para_postular(self):
        """Verifica si la vacante está disponible para recibir más postulaciones"""
        # Si la vacante está eliminada o no está publicada, no está disponible
        if self.eliminada or self.estado != 'publicada':
            return False
            
        # Si no hay límite de postulantes, siempre está disponible
        if self.max_postulantes is None or self.max_postulantes <= 0:
            return True
            
        # Asegurarse de que postulantes_actuales sea un número entero
        postulantes = self.postulantes_actuales or 0
        
        # Verificar si hay cupo disponible
        return postulantes < self.max_postulantes

    def to_json(self):
        return {
            "id": self.id,
            "empresa_id": self.empresa_id,
            "titulo": self.titulo,
            "descripcion": self.descripcion,
            "requisitos": self.requisitos,
            "fecha_publicacion": self.fecha_publicacion.isoformat() if self.fecha_publicacion else None,
            "ubicacion": self.ubicacion,
            "estado": self.estado,
            "max_postulantes": self.max_postulantes,
            "postulantes_actuales": self.postulantes_actuales,
            "disponible_para_postular": self.disponible_para_postular(),
            "destacada": self.destacada,
            "salario_aprox": float(self.salario_aprox) if self.salario_aprox is not None else None,
            "eliminada": self.eliminada,
            "modalidad": self.modalidad
        }
