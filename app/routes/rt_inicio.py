from flask import Blueprint, render_template, session, redirect, url_for
from app.utils.decorators import login_role_required
from app.utils.roles import Roles
from app.db.sql import db
from app.models.md_usuarios import UsuarioModel
from app.models.md_empresas import EmpresaModel
from app.models.md_vacantes import VacanteModel
from app.models.md_postulacion import PostulacionModel
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from app.utils.timezone_helper import get_mexico_time

rt_inicio = Blueprint("InicioRoute", __name__)

@rt_inicio.route("/inicio_empleado")
@login_role_required(Roles.EMPLEADO)
def inicio():
    usuario = session.get("usuario")
    if not usuario:
        return redirect(url_for("LoginRoute.login_form"))
    
    # Obtener usuario completo de la base de datos para tener acceso a foto_perfil
    current_user = UsuarioModel.query.get(usuario["id"])
    if not current_user:
        return redirect(url_for("LoginRoute.login_form"))
    
    #  Estadísticas de la plataforma
    total_empresas = EmpresaModel.query.count()
    total_usuarios = UsuarioModel.query.filter_by(tipo_usuario='empleado').count()
    total_vacantes = VacanteModel.query.filter_by(estado='publicada').count()
    
    #  Actividades recientes (últimas 5)
    actividades = []
    
    # Últimas vacantes publicadas
    vacantes_recientes = VacanteModel.query.filter_by(estado='publicada') \
        .order_by(desc(VacanteModel.fecha_publicacion)) \
        .limit(3).all()
    
    for v in vacantes_recientes:
        tiempo = calcular_tiempo_transcurrido(v.fecha_publicacion)
        actividades.append({
            'tipo': 'vacante',
            'titulo': 'Nueva vacante publicada',
            'descripcion': f"{v.titulo} - {v.empresa.nombre_empresa if v.empresa else 'Empresa'}",
            'tiempo': tiempo,
            'fecha': v.fecha_publicacion,
            'color': 'blue'
        })
    
    # Últimos usuarios registrados
    usuarios_recientes = UsuarioModel.query.filter_by(tipo_usuario='empleado') \
        .order_by(desc(UsuarioModel.fecha_registro)) \
        .limit(2).all()
    
    for u in usuarios_recientes:
        tiempo = calcular_tiempo_transcurrido(u.fecha_registro)
        actividades.append({
            'tipo': 'usuario',
            'titulo': 'Usuario registrado',
            'descripcion': f"{u.nombre} se unió a la plataforma",
            'tiempo': tiempo,
            'fecha': u.fecha_registro,
            'color': 'green'
        })
    
    # Últimas contrataciones (postulaciones con estado 'contratado')
    contrataciones = PostulacionModel.query.filter_by(estado='contratado') \
        .order_by(desc(PostulacionModel.fecha_postulacion)) \
        .limit(2).all()
    
    for c in contrataciones:
        if c.empleado and c.empleado.usuario and c.vacante:
            tiempo = calcular_tiempo_transcurrido(c.fecha_postulacion)
            actividades.append({
                'tipo': 'contratacion',
                'titulo': 'Contratación exitosa',
                'descripcion': f"{c.empleado.usuario.nombre} fue contratado como {c.vacante.titulo}",
                'tiempo': tiempo,
                'fecha': c.fecha_postulacion,
                'color': 'orange'
            })
    
    # Ordenar por fecha (más reciente primero) y tomar las 5 más recientes
    actividades = sorted(actividades, key=lambda x: x['fecha'] if x['fecha'] else datetime.min, reverse=True)[:5]
    
    # Empresas destacadas (con más vacantes activas)
    empresas_destacadas = db.session.query(
        EmpresaModel,
        func.count(VacanteModel.id).label('total_vacantes')
    ).join(VacanteModel, EmpresaModel.id == VacanteModel.empresa_id) \
     .filter(VacanteModel.estado == 'publicada') \
     .group_by(EmpresaModel.id) \
     .order_by(desc('total_vacantes')) \
     .limit(3).all()
    
    empresas = []
    for empresa, total in empresas_destacadas:
        empresas.append({
            'nombre': empresa.nombre_empresa,
            'vacantes': total,
            'inicial': empresa.nombre_empresa[0].upper() if empresa.nombre_empresa else 'E'
        })
    
    return render_template(
        "inicio.jinja2",
        current_user=current_user,
        total_empresas=total_empresas,
        total_usuarios=total_usuarios,
        total_vacantes=total_vacantes,
        actividades=actividades,
        empresas_destacadas=empresas
    )

def calcular_tiempo_transcurrido(fecha):
    """Calcula el tiempo transcurrido desde una fecha"""
    if not fecha:
        return "Hace un momento"
    
    ahora = get_mexico_time()
    diferencia = ahora - fecha
    
    if diferencia.days > 365:
        años = diferencia.days // 365
        return f"Hace {años} año{'s' if años > 1 else ''}"
    elif diferencia.days > 30:
        meses = diferencia.days // 30
        return f"Hace {meses} mes{'es' if meses > 1 else ''}"
    elif diferencia.days > 0:
        return f"Hace {diferencia.days} día{'s' if diferencia.days > 1 else ''}"
    elif diferencia.seconds > 3600:
        horas = diferencia.seconds // 3600
        return f"Hace {horas} hora{'s' if horas > 1 else ''}"
    elif diferencia.seconds > 60:
        minutos = diferencia.seconds // 60
        return f"Hace {minutos} minuto{'s' if minutos > 1 else ''}"
    else:
        return "Hace un momento"
