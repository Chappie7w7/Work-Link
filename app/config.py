from dotenv import load_dotenv
import os

load_dotenv('.env')

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'clave-por-defecto')
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
