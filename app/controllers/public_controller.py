"""Controlador público: las páginas que ve cualquiera SIN iniciar sesión.

Este es un CONTROLADOR de MVC. Su trabajo:
  1. Recibir una petición del navegador (una URL).
  2. Coordinar: pedir datos a un servicio/modelo (cuando los haya).
  3. Elegir qué VISTA (plantilla Jinja) devolver.

Regla de oro del proyecto: los controladores son FINOS. Nada de lógica de negocio
aquí dentro; esa vivirá en app/services/. Aquí solo se coordina.

Por dentro usamos un "Blueprint": la pieza de Flask que agrupa rutas relacionadas
en un módulo, para no acabar con un único archivo gigante de rutas. Piensa en él
como "el departamento público" del ayuntamiento que es la web.
"""

from flask import Blueprint, render_template

from app.services import event_service

# Creamos el blueprint (el "departamento"). Argumentos:
#   "public"  -> nombre interno; se usa en url_for, p.ej. url_for("public.landing").
#   __name__  -> ayuda a Flask a localizar plantillas y archivos estáticos.
public_bp = Blueprint("public", __name__)


@public_bp.route("/")
def landing():
    """Página de inicio pública de Patio Lab.

    Muestra los próximos eventos (como mucho 3) para enganchar al visitante.
    """
    upcoming_events = event_service.list_upcoming_events(limit=3)
    return render_template("public/landing.html", upcoming_events=upcoming_events)


@public_bp.route("/health")
def health():
    """Endpoint de salud: responde 'ok' en texto plano.

    Sirve para comprobar de un vistazo (o desde un script) que el servidor está
    vivo, sin cargar ninguna plantilla. Útil ahora y en producción.
    """
    return "ok", 200
