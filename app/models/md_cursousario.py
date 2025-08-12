from app.db.sql import db
from sqlalchemy import Column, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

class CursoUsuarioModel(db.Model):
    __tablename__ = 'cursos_usuario'

    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=True)
    curso_id = Column(Integer, ForeignKey('cursos_capacitaciones.id'), nullable=True)
    fecha_inicio = Column(DateTime, nullable=True)
    completado = Column(Boolean, default=False)

    # Relaciones
    usuario = relationship('UsuarioModel', backref='cursos_usuario')
    curso = relationship('CursoCapacitacionModel', backref='usuarios_curso')

    def __init__(self, usuario_id=None, curso_id=None, fecha_inicio=None, completado=False):
        self.usuario_id = usuario_id
        self.curso_id = curso_id
        self.fecha_inicio = fecha_inicio or datetime.utcnow()
        self.completado = completado

    def to_json(self):
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "curso_id": self.curso_id,
            "fecha_inicio": self.fecha_inicio.isoformat() if self.fecha_inicio else None,
            "completado": self.completado
        }
