from app.db.sql import db
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

class EmpresaModel(db.Model):
    __tablename__ = 'empresas'

    id = Column(Integer, ForeignKey('usuarios.id'), primary_key=True)
    nombre_empresa = Column(String(150), nullable=True)
    rfc = Column(String(20), nullable=True)
    sector = Column(String(100), nullable=True)
    descripcion = Column(Text, nullable=True)
    direccion = Column(String(255), nullable=True)
    telefono = Column(String(20), nullable=True)

    # Relación uno 
    usuario = relationship('UsuarioModel', backref='empresa', uselist=False)

    def __init__(self, id, nombre_empresa=None, rfc=None, sector=None, descripcion=None, direccion=None, telefono=None):
        self.id = id
        self.nombre_empresa = nombre_empresa
        self.rfc = rfc
        self.sector = sector
        self.descripcion = descripcion
        self.direccion = direccion
        self.telefono = telefono

    def to_json(self):
        return {
            "id": self.id,
            "nombre_empresa": self.nombre_empresa,
            "rfc": self.rfc,
            "sector": self.sector,
            "descripcion": self.descripcion,
            "direccion": self.direccion,
            "telefono": self.telefono
        }
