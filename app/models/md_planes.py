from app.db.sql import db
from sqlalchemy import Column, Integer, String, Text, Enum, Numeric
from sqlalchemy.orm import relationship

class PlanModel(db.Model):
    __tablename__ = 'planes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre_plan = Column(String(100), nullable=True)
    tipo = Column(Enum('empleado', 'empresa'), nullable=True)
    descripcion = Column(Text, nullable=True)
    precio = Column(Numeric(10, 2), nullable=True)
    publicaciones_maximas = Column(Integer, nullable=True)
    beneficios = Column(Text, nullable=True)
    duracion_dias = Column(Integer, nullable=True)

    # Relación opcional (si los usuarios usan este plan)
    usuarios = relationship('UsuarioModel', backref='plan', lazy=True)

    def __init__(self, nombre_plan=None, tipo=None, descripcion=None, precio=None,
                 publicaciones_maximas=None, beneficios=None, duracion_dias=None):
        self.nombre_plan = nombre_plan
        self.tipo = tipo
        self.descripcion = descripcion
        self.precio = precio
        self.publicaciones_maximas = publicaciones_maximas
        self.beneficios = beneficios
        self.duracion_dias = duracion_dias

    def to_json(self):
        return {
            "id": self.id,
            "nombre_plan": self.nombre_plan,
            "tipo": self.tipo,
            "descripcion": self.descripcion,
            "precio": float(self.precio) if self.precio is not None else None,
            "publicaciones_maximas": self.publicaciones_maximas,
            "beneficios": self.beneficios,
            "duracion_dias": self.duracion_dias
        }
