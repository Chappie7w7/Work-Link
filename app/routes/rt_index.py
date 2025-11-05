# rt_index.py
import os, json, requests
from types import SimpleNamespace
from flask import Blueprint, render_template, session
from app.models.md_vacantes import VacanteModel
from sqlalchemy.orm import joinedload

rt_index = Blueprint('IndexRoute', __name__)
CACHE_FILE = "cache_vacantes.json"


def hay_internet():
    try:
        requests.get("https://www.google.com", timeout=3)
        return True
    except:
        return False


@rt_index.route('/')
def index():
    usuario_session = session.get("usuario")

    if isinstance(usuario_session, dict):
        current_user = SimpleNamespace(**usuario_session)
    else:
        current_user = None

    jobs = []

    if hay_internet():
        # Si hay internet, consulto DB
        jobs = (
            VacanteModel.query
            .options(joinedload(VacanteModel.empresa))
            .filter_by(destacada=True, estado='publicada', eliminada=False)
            .order_by(VacanteModel.fecha_publicacion.desc())
            .limit(6)
            .all()
        )

        # Guardar en caché para usarse sin internet
        try:
            data = []
            for v in jobs:
                data.append({
                    "id": v.id,
                    "titulo": v.titulo,
                    "descripcion": v.descripcion,
                    "ubicacion": v.ubicacion,
                    "modalidad": v.modalidad,
                    "estado": v.estado,
                    "salario_aprox": float(v.salario_aprox) if v.salario_aprox else None,
                    "empresa": v.empresa.nombre_empresa if v.empresa else None
                })
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("⚠️ No se pudo guardar cache:", e)

    else:
        # 🔹 Si no hay internet, leo caché
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                jobs = [SimpleNamespace(**v) for v in data]
            except Exception as e:
                print("⚠️ Error leyendo cache:", e)
        else:
            jobs = []  # No hay internet ni cache

    return render_template('index.jinja2', current_user=current_user, jobs=jobs)



