from flask import Blueprint, request, jsonify, session
from app.utils.pusher_client import pusher_client, PUSHER_KEY, PUSHER_CLUSTER
from app.controller.ctr_empleos import get_user_from_session
from urllib.parse import parse_qs

rt_pusher = Blueprint('PusherRoute', __name__)

@rt_pusher.route('/pusher/auth', methods=['POST'])
def pusher_auth():
    usuario = session.get('usuario')
    if not usuario:
        user = get_user_from_session(session)
        if user:
            usuario = {'id': user.get('id'), 'nombre': user.get('nombre')}
    if not usuario:
        return jsonify({'error': 'No autenticado'}), 401
    data_json = request.get_json(silent=True) or {}
    socket_id = request.form.get('socket_id') or data_json.get('socket_id')
    channel_name = (
        request.form.get('channel_name')
        or request.form.get('channel_name[]')
        or data_json.get('channel_name')
        or data_json.get('channel_name[]')
    )
    if not socket_id or not channel_name:
        # Intentar parsear cuerpo urlencoded manualmente
        try:
            body = request.get_data(as_text=True) or ''
            parsed = parse_qs(body)
            socket_id = socket_id or (parsed.get('socket_id', [None])[0])
            channel_name = channel_name or (parsed.get('channel_name', [None])[0] or parsed.get('channel_name[]', [None])[0])
        except Exception:
            pass
    if not socket_id or not channel_name:
        return jsonify({'error': 'Datos incompletos'}), 400
    auth = pusher_client.authenticate(channel=channel_name, socket_id=socket_id)
    return jsonify(auth)

@rt_pusher.route('/pusher/config')
def pusher_config():
    return jsonify({
        'key': PUSHER_KEY,
        'cluster': PUSHER_CLUSTER
    })

@rt_pusher.route('/pusher/me')
def pusher_me():
    usuario = session.get('usuario')
    if not usuario:
        user = get_user_from_session(session)
        if user:
            return jsonify({'id': user.get('id'), 'nombre': user.get('nombre')})
        return jsonify({}), 401
    return jsonify({'id': usuario.get('id'), 'nombre': usuario.get('nombre')})
