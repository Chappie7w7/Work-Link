from flask_mail import Mail
from flask_socketio import SocketIO
from itsdangerous import URLSafeTimedSerializer

mail = Mail()
socketio = SocketIO(cors_allowed_origins="*", async_mode='threading')
serializer = None

def init_extensiones(app):
    global serializer
    mail.init_app(app)
    socketio.init_app(app)
    serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])
