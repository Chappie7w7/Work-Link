from flask import Blueprint, render_template

DesarrolladoresRoute = Blueprint("DesarrolladoresRoute", __name__)

@DesarrolladoresRoute.route("/desarrolladores")
def desarrolladores():
    return render_template("desarrolladores.jinja2")
