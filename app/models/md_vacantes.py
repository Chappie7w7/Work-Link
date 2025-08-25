from app.db.sql import db
from sqlalchemy import Column, Integer, String, Text, Enum, Boolean, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

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

   
    empresa = relationship('EmpresaModel', backref='vacantes')

    def __init__(self, empresa_id=None, titulo=None, descripcion=None, requisitos=None,
                 fecha_publicacion=None, ubicacion=None, estado=None, destacada=False,
                 salario_aprox=None, modalidad=None):
        self.empresa_id = empresa_id
        self.titulo = titulo
        self.descripcion = descripcion
        self.requisitos = requisitos
        self.fecha_publicacion = fecha_publicacion or datetime.utcnow()
        self.ubicacion = ubicacion
        self.estado = estado
        self.destacada = destacada
        self.salario_aprox = salario_aprox
        self.modalidad = modalidad

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
            "destacada": self.destacada,
            "salario_aprox": float(self.salario_aprox) if self.salario_aprox is not None else None,
            "modalidad": self.modalidad
        }
