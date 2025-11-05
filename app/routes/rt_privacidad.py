from flask import Blueprint, render_template

# Crear el Blueprint
rt_privacidad = Blueprint('PrivacidadRoute', __name__, template_folder='templates')

@rt_privacidad.route('/aviso-privacidad')
def aviso_privacidad():
    """
    Ruta para mostrar el aviso de privacidad
    """
    return render_template('aviso_privacidad.jinja2')

# Si necesitas más rutas relacionadas con privacidad, las puedes agregar aquí
