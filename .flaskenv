# =============================================================================
# Variables que lee automáticamente el comando `flask` (gracias a python-dotenv).
# A diferencia de .env (secretos), esto SÍ se sube al repo: solo dice a la CLI
# de Flask dónde está la app y que estamos en modo desarrollo.
# =============================================================================

# Dónde encontrar la aplicación. Apunta a wsgi.py, que expone create_app().
FLASK_APP=wsgi.py

# Modo desarrollo: recarga automática al guardar y página de errores detallada.
FLASK_DEBUG=1
