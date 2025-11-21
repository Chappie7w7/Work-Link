# rt_index.py
import os, json, requests
from types import SimpleNamespace
from flask import Blueprint, render_template, session, send_from_directory, current_app, jsonify

from app.models.md_vacantes import VacanteModel
from sqlalchemy.orm import joinedload

rt_index = Blueprint('IndexRoute', __name__)
CACHE_FILE = "cache_vacantes.json"


def get_obj_dict(obj):
    """Convert SimpleNamespace or similar objects to dictionary for JSON serialization"""
    if hasattr(obj, '__dict__'):
        return obj.__dict__
    elif isinstance(obj, dict):
        return obj
    else:
        return str(obj)


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
            cache_jobs = (
                VacanteModel.query
                .options(joinedload(VacanteModel.empresa))
                .filter_by(estado='publicada', eliminada=False)
                .order_by(VacanteModel.fecha_publicacion.desc())
                .limit(30)
                .all()
            )
            data = []
            for v in cache_jobs:
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
            with open(os.path.join(current_app.root_path, CACHE_FILE), "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            offline_jobs_json = json.dumps(data, ensure_ascii=False)
        except Exception as e:
            print("⚠️ No se pudo guardar cache:", e)
            offline_jobs_json = json.dumps([], ensure_ascii=False)

    else:
        # 🔹 Si no hay internet, leo caché
        if os.path.exists(os.path.join(current_app.root_path, CACHE_FILE)):
            try:
                with open(os.path.join(current_app.root_path, CACHE_FILE), "r", encoding="utf-8") as f:
                    data = json.load(f)
                jobs = [SimpleNamespace(**v) for v in data]
                offline_jobs_json = json.dumps(data, ensure_ascii=False)
            except Exception as e:
                print("⚠️ Error leyendo cache:", e)
                offline_jobs_json = json.dumps([], ensure_ascii=False)
        else:
            jobs = []  # No hay internet ni cache
            offline_jobs_json = json.dumps([], ensure_ascii=False)

    # Convertir jobs a JSON para pasar al template
    jobs_json = json.dumps(jobs, default=get_obj_dict)
    return render_template('index.jinja2', current_user=current_user, jobs=jobs, jobs_json=jobs_json, offline_jobs_json=offline_jobs_json)


@rt_index.route('/offline')
def offline():
    """Página offline que muestra los trabajos cacheados"""
    jobs = []
    
    # Leer datos del cache
    if os.path.exists(os.path.join(current_app.root_path, CACHE_FILE)):
        try:
            with open(os.path.join(current_app.root_path, CACHE_FILE), "r", encoding="utf-8") as f:
                data = json.load(f)
            jobs = [SimpleNamespace(**v) for v in data]
        except Exception as e:
            print("⚠️ Error leyendo cache en offline:", e)
    
    return render_template('offline.html', jobs=jobs)


@rt_index.route('/service-worker.js')
def service_worker():
    """Servir el Service Worker desde la raíz para que tenga scope global."""
    return send_from_directory(current_app.static_folder, 'service-worker.js', mimetype='application/javascript')


@rt_index.route('/api/offline_jobs')
def api_offline_jobs():
    """Devuelve las últimas 30 vacantes publicadas para cacheo rápido en el cliente."""
    try:
        cache_jobs = (
            VacanteModel.query
            .options(joinedload(VacanteModel.empresa))
            .filter_by(estado='publicada', eliminada=False)
            .order_by(VacanteModel.fecha_publicacion.desc())
            .limit(30)
            .all()
        )
        data = []
        for v in cache_jobs:
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
        return jsonify(data)
    except Exception as e:
        print("⚠️ Error en api_offline_jobs:", e)
        return jsonify([])