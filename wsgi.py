"""Punto de entrada de la aplicación.

El comando `flask run` (gracias a FLASK_APP=wsgi.py en .flaskenv) importa este
archivo y busca una variable llamada `app`. Aquí simplemente llamamos a la
factory para construirla.

El mismo archivo lo usará en el futuro un servidor de producción como gunicorn:
  gunicorn "wsgi:app"
"""

from app import create_app

app = create_app()
