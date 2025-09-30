from app.db.sql import db
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from datetime import datetime
from sqlalchemy.orm import relationship


from flask_login import UserMixin

class UsuarioModel(db.Model):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), nullable=False)
    correo = Column(String(100), unique=True, nullable=False)
    contraseña = Column(String(255), nullable=False)
    tipo_usuario = Column(String(50), nullable=False)
    foto_perfil = Column(String(255), nullable=True)
    fecha_registro = Column(DateTime, default=datetime.utcnow)
    premium = Column(Boolean, default=False)
    plan_id = Column(Integer, ForeignKey('planes.id'), nullable=True)
    ubicacion = Column(String(100), nullable=True)
    ultimo_login = Column(DateTime, nullable=True)

    # Relación con el modelo PlanModel (si lo tienes)
    #plan = relationship("PlanModel", backref="usuarios")

    def __init__(self, nombre, correo, contraseña, tipo_usuario, foto_perfil=None,
            premium=False, plan_id=None, ubicacion=None, fecha_registro=None,
            ultimo_login=None):
        self.nombre = nombre
        self.correo = correo
        self.contraseña = contraseña
        self.tipo_usuario = tipo_usuario 
        self.tipo_usuario = tipo_usuario
        self.foto_perfil = foto_perfil
        self.premium = premium
        self.plan_id = plan_id
        self.ubicacion = ubicacion
        self.fecha_registro = fecha_registro or datetime.utcnow()
        self.ultimo_login = ultimo_login

    def to_json(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "correo": self.correo,
            "tipo_usuario": self.tipo_usuario,
            "foto_perfil": self.foto_perfil,
            "fecha_registro": self.fecha_registro.isoformat(),
            "premium": self.premium,
            "plan_id": self.plan_id,
            "ubicacion": self.ubicacion,
            "ultimo_login": self.ultimo_login.isoformat() if self.ultimo_login else None
        }


class UsuarioLogin(UserMixin):
    def __init__(self, usuario: UsuarioModel) -> None:
        self.id = usuario.id
        self.nombre = usuario.nombre
        self.correo = usuario.correo
        self.contraseña = usuario.contraseña
        self.tipo_usuario = usuario.tipo_usuario
        self.plan_id = usuario.plan_id
        self.premium = usuario.premium

    @staticmethod
    def query(id):
        user: UsuarioModel = UsuarioModel.query.get(id)
        return UsuarioLogin(user) if user else None
