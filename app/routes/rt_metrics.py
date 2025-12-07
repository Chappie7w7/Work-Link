from flask import Blueprint, Response, request
from prometheus_client import Counter, Histogram, generate_latest
import time

rt_metrics = Blueprint('rt_metrics', __name__)

# Métricas
REQUEST_COUNT = Counter(
    'worklink_requests_total',
    'Total de solicitudes recibidas',
    ['method', 'endpoint']
)

REQUEST_LATENCY = Histogram(
    'worklink_request_latency_seconds',
    'Latencia de las solicitudes',
    ['endpoint']
)

@rt_metrics.before_app_request
def before_request():
    request.start_time = time.time()

@rt_metrics.after_app_request
def after_request(response):
    try:
        latency = time.time() - request.start_time
        REQUEST_COUNT.labels(method=request.method, endpoint=request.path).inc()
        REQUEST_LATENCY.labels(endpoint=request.path).observe(latency)
    except Exception:
        pass
    return response

@rt_metrics.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype="text/plain")