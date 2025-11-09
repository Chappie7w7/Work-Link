from app import create_app
from app.extensiones import socketio

app = create_app()

if __name__ == '__main__':
    # Usar socketio.run() en lugar de app.run() para soportar WebSockets
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
