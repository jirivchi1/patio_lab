"""Controlador del perfil del usuario.

Página privada (login_required) que reúne lo "mío": las comunidades a las que
pertenezco y los eventos a los que me he inscrito.
"""

from flask import Blueprint, render_template
from flask_login import current_user, login_required

from app.services import registration_service

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/perfil")
@login_required
def profile():
    registrations = registration_service.list_user_registrations(current_user)
    # current_user.memberships viene de la relación del modelo User: las usamos
    # directamente para listar las comunidades del usuario.
    return render_template(
        "profile/profile.html",
        registrations=registrations,
        memberships=current_user.memberships,
    )
