from app.db.sql import db
from sqlalchemy import Column, Integer, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship

class EmpleadoModel(db.Model):
    __tablename__ = 'empleados'

    id = Column(Integer, ForeignKey('usuarios.id'), primary_key=True)
    curriculum_url = Column(Text, nullable=True)
    educacion = Column(Text, nullable=True)
    experiencia = Column(Text, nullable=True)
    habilidades = Column(Text, nullable=True)
    cv_destacado = Column(Boolean, default=False)

    # Relación
    usuario = relationship('UsuarioModel', backref='empleado', uselist=False)

    def __init__(self, id, curriculum_url=None, educacion=None, experiencia=None, habilidades=None, cv_destacado=False):
        self.id = id
        self.curriculum_url = curriculum_url
        self.educacion = educacion
        self.experiencia = experiencia
        self.habilidades = habilidades
        self.cv_destacado = cv_destacado

    def to_json(self):
        return {
            "id": self.id,
            "curriculum_url": self.curriculum_url,
            "educacion": self.educacion,
            "experiencia": self.experiencia,
            "habilidades": self.habilidades,
            "cv_destacado": self.cv_destacado
        }
