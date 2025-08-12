from app.db.sql import db
from sqlalchemy import Column, Integer, String, Text, Boolean

class CursoCapacitacionModel(db.Model):
    __tablename__ = 'cursos_capacitaciones'

    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String(150), nullable=True)
    descripcion = Column(Text, nullable=True)
    url = Column(Text, nullable=True)
    premium_online = Column(Boolean, default=False)

    def __init__(self, titulo=None, descripcion=None, url=None, premium_online=False):
        self.titulo = titulo
        self.descripcion = descripcion
        self.url = url
        self.premium_online = premium_online

    def to_json(self):
        return {
            "id": self.id,
            "titulo": self.titulo,
            "descripcion": self.descripcion,
            "url": self.url,
            "premium_online": self.premium_online
        }
