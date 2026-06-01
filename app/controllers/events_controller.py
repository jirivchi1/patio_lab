"""Controlador de eventos e inscripciones.

Fino, como siempre: lista/muestra eventos y delega en registration_service el
trabajo difícil (aforo y pago).
"""

from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.services import event_service, registration_service

events_bp = Blueprint("events", __name__)


@events_bp.route("/eventos")
def list_events():
    """Listado público de próximos eventos publicados."""
    events = event_service.list_upcoming_events()
    # Calculamos las plazas libres de cada uno para pintarlas en las tarjetas.
    events_info = [
        {"event": event, "spots_left": registration_service.spots_left(event)}
        for event in events
    ]
    return render_template("events/list.html", events_info=events_info)


@events_bp.route("/eventos/<slug>")
def detail(slug: str):
    """Ficha de un evento: toda la info + inscribirse / cancelar."""
    event = event_service.get_event_by_slug(slug)
    if event is None:
        abort(404)

    spots = registration_service.spots_left(event)
    # ¿El visitante actual ya está inscrito? (None si no, o no está logueado).
    registration = (
        registration_service.get_active_registration(current_user.id, event.id)
        if current_user.is_authenticated
        else None
    )
    return render_template(
        "events/detail.html", event=event, spots_left=spots, registration=registration
    )


@events_bp.route("/eventos/<slug>/inscribirse", methods=["POST"])
@login_required
def register(slug: str):
    """Inscribe al usuario actual. La lógica de aforo/pago está en el servicio."""
    event = event_service.get_event_by_slug(slug)
    if event is None:
        abort(404)

    result = registration_service.register_for_event(current_user, event.id)
    flash(result.message, "success" if result.ok else "error")
    return redirect(url_for("events.detail", slug=slug))


@events_bp.route("/eventos/<slug>/cancelar", methods=["POST"])
@login_required
def cancel(slug: str):
    """Cancela la inscripción del usuario actual."""
    event = event_service.get_event_by_slug(slug)
    if event is None:
        abort(404)

    result = registration_service.cancel_registration(current_user, event.id)
    flash(result.message, "success" if result.ok else "error")
    return redirect(url_for("events.detail", slug=slug))
