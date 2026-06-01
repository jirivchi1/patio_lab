"""Decoradores reutilizables para los controladores."""

from functools import wraps

from flask import abort, redirect, request, url_for
from flask_login import current_user

from app.models.enums import UserRole


def admin_required(view):
    """Permite el acceso solo a usuarios con rol admin.

    Un "decorador" envuelve una función de ruta para ejecutar código ANTES que
    ella. Aquí comprobamos:
      - Si no hay sesión iniciada -> al login (recordando a dónde quería ir).
      - Si hay sesión pero NO es admin -> 403 (prohibido).
      - Si es admin -> dejamos pasar y ejecutamos la ruta.

    @wraps conserva el nombre y la docstring de la función original, para que
    Flask y las herramientas no se confundan.
    """

    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login", next=request.path))
        if current_user.role != UserRole.admin:
            abort(403)
        return view(*args, **kwargs)

    return wrapped
