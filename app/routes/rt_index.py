from types import SimpleNamespace
from flask import Blueprint, render_template, session

rt_index = Blueprint('IndexRoute', __name__)

@rt_index.route('/')
def index():
    usuario_session = session.get("usuario")

    if isinstance(usuario_session, dict):
        current_user = SimpleNamespace(**usuario_session)
    else:
        current_user = None

    return render_template('index.jinja2', current_user=current_user)
