from .rt_index import rt_index
from .rt_login import rt_login
from .rt_inicio import rt_inicio
from .rt_notificaciones import rt_notificaciones
from .rt_planes import rt_planes
from .rt_empleos import rt_empleos
from .rt_mensajes import rt_mensajes
from .rt_registro import rt_registro

def register_routes(app):
    app.register_blueprint(rt_index)
    app.register_blueprint(rt_login)
    app.register_blueprint(rt_inicio)
    app.register_blueprint(rt_notificaciones)
    app.register_blueprint(rt_planes)
    app.register_blueprint(rt_empleos)
    app.register_blueprint(rt_mensajes)
    app.register_blueprint(rt_registro)

