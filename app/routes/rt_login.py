from flask import Blueprint, render_template, request
from app.controller.ctr_login import login_user, logout_user


rt_login = Blueprint("LoginRoute", __name__)

@rt_login.route("/login")
def login_form():
    return render_template("login.jinja2")

@rt_login.route("/login", methods=["POST"])
def login():
    correo = request.form.get("correo", "").strip()
    password = request.form.get("password", "").strip()
    _, response = login_user(correo, password)
    return response

@rt_login.route("/logout")
def logout():
    return logout_user()
