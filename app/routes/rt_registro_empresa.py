from flask import Blueprint, render_template

rt_registro_empresa = Blueprint("RegistroEmpresaRoute", __name__)

@rt_registro_empresa.route("/registro/empresa", methods=["GET"])
def registro_empresa():
    # Solo muestra el formulario
    return render_template("empresa/registro_empresa.jinja2")
