from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from app.models.md_usuarios import UsuarioModel
from app.models.md_empresas import EmpresaModel
from app.models.md_empleados import EmpleadoModel
from app.models.md_contacto import ContactoModel
from app.db.sql import db
from app.utils.decorators import login_role_required
from app.utils.roles import Roles
from app.controller.ctr_usuarios import dar_baja_usuario, eliminar_usuario, get_all_usuarios, aprobar_usuario
from app.controller.ctr_empleos import get_user_from_session

rt_admin = Blueprint('AdminRoute', __name__, url_prefix='/admin')


@rt_admin.route('/dashboard')
@login_role_required(Roles.SUPERADMIN)
def dashboard():
    """Dashboard principal del administrador"""
    try:
        user = get_user_from_session(session)
        if not user:
            flash("Sesión no válida", "error")
            return redirect(url_for("LoginRoute.login_form"))
        
        usuarios, error = get_all_usuarios()
        if error:
            flash(error, "error")
            usuarios = []
        
        # Calcular estadísticas
        total_usuarios = len(usuarios)
        total_empresas = sum(1 for u in usuarios if u.tipo_usuario == Roles.EMPRESA)
        total_empleados = sum(1 for u in usuarios if u.tipo_usuario == Roles.EMPLEADO)
        total_solicitudes = sum(1 for u in usuarios if getattr(u, 'solicitud_eliminacion', False))
        
        # Filtro opcional por solicitudes (usuarios deshabilitados)
        current_filter = request.args.get('f', '').lower()
        if current_filter == 'solicitudes':
            usuarios_iter = [u for u in usuarios if getattr(u, 'solicitud_eliminacion', False)]
        else:
            usuarios_iter = usuarios

        # Obtener información adicional de empresas y empleados
        usuarios_data = []
        for usuario in usuarios_iter:
            try:
                usuario_info = {
                    "id": usuario.id,
                    "nombre": usuario.nombre,
                    "correo": usuario.correo,
                    "tipo_usuario": usuario.tipo_usuario,
                    "fecha_registro": usuario.fecha_registro,
                    "ultimo_login": usuario.ultimo_login,
                    "premium": usuario.premium,
                    "aprobado": usuario.aprobado,
                    "foto_perfil": usuario.foto_perfil,
                    "solicitud_eliminacion": getattr(usuario, 'solicitud_eliminacion', False)
                }
                
                # Agregar información específica según el tipo
                if usuario.tipo_usuario == Roles.EMPRESA:
                    empresa = EmpresaModel.query.get(usuario.id)
                    if empresa:
                        usuario_info["nombre_empresa"] = empresa.nombre_empresa
                        usuario_info["rfc"] = empresa.rfc
                
                usuarios_data.append(usuario_info)
            except Exception as e:
                print(f"Error procesando usuario {usuario.id}: {str(e)}")
                continue
        
        return render_template('admin/dashboard.jinja2', 
                             usuarios=usuarios_data, 
                             current_user=user,
                             total_usuarios=total_usuarios,
                             total_empresas=total_empresas,
                             total_empleados=total_empleados,
                             total_solicitudes=total_solicitudes,
                             current_filter=current_filter,
                             active_page='dashboard')
    except Exception as e:
        import traceback
        print(f"Error en dashboard admin: {str(e)}")
        print(traceback.format_exc())
        flash(f"Error al cargar el dashboard: {str(e)}", "error")
        return redirect(url_for("IndexRoute.index"))


@rt_admin.route('/ayuda')
@login_role_required(Roles.SUPERADMIN)
def ayuda():
    try:
        user = get_user_from_session(session)
        if not user:
            flash("Sesión no válida", "error")
            return redirect(url_for("LoginRoute.login_form"))
        mensajes = (
            ContactoModel.query
            .order_by(ContactoModel.fecha_envio.desc())
            .all()
        )
        return render_template('admin/ayuda.jinja2', 
                               current_user=user,
                               mensajes=mensajes,
                               active_page='ayuda')
    except Exception as e:
        print(f"Error cargando mensajes de ayuda: {str(e)}")
        flash("No se pudieron cargar los mensajes de ayuda.", "error")
        return redirect(url_for('AdminRoute.dashboard'))


@rt_admin.route('/ayuda/limpiar', methods=['POST'])
@login_role_required(Roles.SUPERADMIN)
def limpiar_ayuda():
    try:
        ContactoModel.query.delete()
        db.session.commit()
        flash("Mensajes de ayuda eliminados.", "success")
    except Exception as e:
        print(f"Error eliminando mensajes de ayuda: {e}")
        db.session.rollback()
        flash("No se pudieron eliminar los mensajes.", "error")
    return redirect(url_for('AdminRoute.ayuda'))


@rt_admin.route('/api/ayuda/contador')
@login_role_required(Roles.SUPERADMIN)
def contador_ayuda():
    try:
        count = ContactoModel.query.filter_by(leido=False).count()
        return jsonify({"count": count})
    except Exception as e:
        print(f"Error obteniendo contador de ayuda: {e}")
        return jsonify({"count": 0})


@rt_admin.route('/ayuda/marcar-leido/<int:contacto_id>', methods=['POST'])
@login_role_required(Roles.SUPERADMIN)
def marcar_ayuda_leido(contacto_id):
    try:
        contacto = ContactoModel.query.get(contacto_id)
        if not contacto:
            flash("Mensaje no encontrado.", "error")
            return redirect(url_for('AdminRoute.ayuda'))
        contacto.leido = True
        db.session.commit()
        flash("Mensaje marcado como leído.", "success")
        return redirect(url_for('AdminRoute.ayuda'))
    except Exception as e:
        print(f"Error marcando mensaje como leído: {e}")
        flash("No se pudo actualizar el mensaje.", "error")
        return redirect(url_for('AdminRoute.ayuda'))


@rt_admin.route('/usuarios/dar-baja/<int:usuario_id>', methods=['POST'])
@login_role_required(Roles.SUPERADMIN)
def dar_baja(usuario_id):
    """Da de baja a un usuario"""
    try:
        success, error = dar_baja_usuario(usuario_id)
        if error:
            flash(error, "error")
        else:
            flash("Usuario dado de baja exitosamente", "success")
    except Exception as e:
        flash(f"Error al dar de baja al usuario: {str(e)}", "error")
    
    return redirect(url_for("AdminRoute.dashboard"))


@rt_admin.route('/usuarios/eliminar/<int:usuario_id>', methods=['POST'])
@login_role_required(Roles.SUPERADMIN)
def eliminar(usuario_id):
    """Deshabilita un usuario (soft-delete)"""
    try:
        success, error = eliminar_usuario(usuario_id)
        if error:
            flash(error, "error")
        else:
            flash("Usuario deshabilitado exitosamente", "success")
    except Exception as e:
        flash(f"Error al deshabilitar el usuario: {str(e)}", "error")
    
    return redirect(url_for("AdminRoute.dashboard"))


@rt_admin.route('/usuarios/aprobar/<int:usuario_id>', methods=['POST'])
@login_role_required(Roles.SUPERADMIN)
def aprobar(usuario_id):
    """Aprueba (habilita) un usuario pendiente"""
    try:
        success, error = aprobar_usuario(usuario_id)
        if error:
            flash(error, "error")
        else:
            flash("Usuario habilitado exitosamente", "success")
    except Exception as e:
        flash(f"Error al aprobar al usuario: {str(e)}", "error")
    return redirect(url_for("AdminRoute.dashboard"))

