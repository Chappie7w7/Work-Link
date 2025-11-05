from .rt_index import rt_index
from .rt_login import rt_login
from .rt_inicio import rt_inicio
from .rt_notificaciones import rt_notificaciones
from .rt_planes import rt_planes
from .rt_empleos import rt_empleos
from .rt_mensajes import rt_mensajes
from .rt_registro import rt_registro
from .rt_empresa import rt_empresa
from .rt_registro_empresa import rt_registro_empresa
from .rt_perfil import rt_perfil
from .rt_desarrolladores import DesarrolladoresRoute
from .rt_usuarios import usuarios_bp
from .rt_privacidad import rt_privacidad

def register_routes(app):
    app.register_blueprint(rt_index)
    app.register_blueprint(rt_login)
    app.register_blueprint(rt_inicio)
    app.register_blueprint(rt_notificaciones)
    app.register_blueprint(rt_planes)
    app.register_blueprint(rt_empleos)
    app.register_blueprint(rt_mensajes)
    app.register_blueprint(rt_registro)
    app.register_blueprint(rt_registro_empresa)
    app.register_blueprint(rt_empresa)

    app.register_blueprint(rt_perfil)
    app.register_blueprint(DesarrolladoresRoute)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(rt_privacidad)




