from flask import redirect, session, url_for, current_app
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from google_auth_oauthlib.flow import Flow
import os
import json

def get_google_auth():
    """Configura y retorna el flujo de autenticación de Google"""
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": current_app.config["GOOGLE_CLIENT_ID"],
                "client_secret": current_app.config["GOOGLE_CLIENT_SECRET"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [
                    "http://localhost:5000/auth/google/callback",
                    "http://localhost/auth/google/callback",
                    "https://tudominio.com/auth/google/callback"
                ]
            }
        },
        scopes=[
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile"
        ]
    )
    return flow

def get_google_provider_cfg():
    """Obtiene la configuración del proveedor de Google"""
    return requests.get("https://accounts.google.com/.well-known/openid-configuration").json()
