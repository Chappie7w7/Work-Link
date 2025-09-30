from flask_mail import Mail
from itsdangerous import URLSafeTimedSerializer

mail = Mail()
serializer = None

def init_extensiones(app):
    global serializer
    mail.init_app(app)
    serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])
