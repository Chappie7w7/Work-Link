from flask_mail import Mail

mail = Mail()

def init_extensions(app):
    """Inicializa todas las extensiones de Flask"""
    mail.init_app(app)