import os
import pusher

# Inicializa el cliente de Pusher usando variables de entorno
# Requiere:
# - PUSHER_APP_ID
# - PUSHER_KEY
# - PUSHER_SECRET
# - PUSHER_CLUSTER

PUSHER_APP_ID = os.environ.get("PUSHER_APP_ID")
PUSHER_KEY = os.environ.get("PUSHER_KEY")
PUSHER_SECRET = os.environ.get("PUSHER_SECRET")
PUSHER_CLUSTER = os.environ.get("PUSHER_CLUSTER")

if not all([PUSHER_APP_ID, PUSHER_KEY, PUSHER_SECRET, PUSHER_CLUSTER]):
    # Evitar romper la app si las vars no están; dejarlo evidente en logs
    # El desarrollador debe configurar las variables de entorno.
    pass

pusher_client = pusher.Pusher(
    app_id=PUSHER_APP_ID,
    key=PUSHER_KEY,
    secret=PUSHER_SECRET,
    cluster=PUSHER_CLUSTER,
    ssl=True
)
