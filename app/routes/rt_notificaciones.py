from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from app.utils.decorators import login_role_required
from app.utils.roles import Roles
from app.models.md_notificacion import NotificacionModel
from app.db.sql import db
from sqlalchemy import desc

rt_notificaciones = Blueprint('NotificacionesRoute', __name__)

@rt_notificaciones.route("/notificaciones")
def notificaciones():
    usuario = session.get('usuario')
    if not usuario:
        return redirect(url_for('IndexRoute.index'))
    
    # Obtener todas las notificaciones del usuario ordenadas por fecha
    notificaciones_list = NotificacionModel.query.filter_by(usuario_id=usuario['id']) \
        .order_by(desc(NotificacionModel.fecha_envio)) \
        .all()
    
    # Contar notificaciones no leídas
    no_leidas = NotificacionModel.query.filter_by(usuario_id=usuario['id'], leido=False).count()
    
    return render_template(
        "notificacion/notificaciones.jinja2",
        current_user=usuario,
        notificaciones=notificaciones_list,
        no_leidas=no_leidas
    )


@rt_notificaciones.route("/notificaciones/marcar_leida/<int:notificacion_id>", methods=["POST"])
def marcar_leida(notificacion_id):
    usuario = session.get('usuario')
    if not usuario:
        return redirect(url_for('IndexRoute.index'))
    
    notificacion = NotificacionModel.query.get(notificacion_id)
    if notificacion and notificacion.usuario_id == usuario['id']:
        notificacion.leido = True
        db.session.commit()
    
    return redirect(url_for('NotificacionesRoute.notificaciones'))


@rt_notificaciones.route("/notificaciones/marcar_todas_leidas", methods=["POST"])
def marcar_todas_leidas():
    usuario = session.get('usuario')
    if not usuario:
        return redirect(url_for('IndexRoute.index'))
    
    NotificacionModel.query.filter_by(usuario_id=usuario['id'], leido=False) \
        .update({'leido': True})
    db.session.commit()
    
    return redirect(url_for('NotificacionesRoute.notificaciones'))


@rt_notificaciones.route("/notificaciones/eliminar_todas", methods=["POST"])
def eliminar_todas():
    """Eliminar todas las notificaciones del usuario"""
    usuario = session.get('usuario')
    if not usuario:
        return redirect(url_for('IndexRoute.index'))
    
    NotificacionModel.query.filter_by(usuario_id=usuario['id']).delete()
    db.session.commit()
    
    return redirect(url_for('NotificacionesRoute.notificaciones'))


@rt_notificaciones.route("/api/notificaciones/contador")
def contador_notificaciones():
    """API endpoint para obtener el contador de notificaciones no leídas en tiempo real"""
    usuario = session.get('usuario')
    if not usuario:
        return jsonify({"count": 0})
    
    count = NotificacionModel.query.filter_by(usuario_id=usuario['id'], leido=False).count()
    return jsonify({"count": count})
