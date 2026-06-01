"""Controlador del panel de administración (solo para el rol admin).

Todas las rutas van protegidas con @admin_required. El prefijo /admin (definido al
registrar el blueprint en la factory) hace que todas cuelguen de /admin/...
"""

from datetime import UTC, datetime

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from app.extensions import db
from app.forms.admin_forms import STATUS_LABELS, CommunityForm, EventForm
from app.models import Community, Event, Registration, User
from app.models.enums import EventStatus
from app.services import admin_service, community_service, registration_service
from app.utils.decorators import admin_required

admin_bp = Blueprint("admin", __name__)


# --- Helpers ----------------------------------------------------------------

def _euros_to_cents(value) -> int:
    """Convierte el precio en euros del formulario a céntimos enteros."""
    return int(round(float(value or 0) * 100))


def _as_utc(value: datetime | None) -> datetime | None:
    """Marca como UTC la fecha naive que devuelve el selector del navegador.

    El control datetime-local da una fecha SIN zona horaria. Nosotros guardamos
    todo en UTC, así que le añadimos esa zona antes de persistir.
    """
    return value.replace(tzinfo=UTC) if value is not None else None


def _populate_event_choices(form: EventForm) -> None:
    """Rellena las listas desplegables del formulario de evento."""
    form.community.choices = [
        (c.id, c.name) for c in community_service.list_communities()
    ]
    form.speaker.choices = [(0, "— Sin ponente —")] + [
        (u.id, u.name) for u in admin_service.list_possible_speakers()
    ]
    form.status.choices = [(s.value, STATUS_LABELS[s]) for s in EventStatus]


# --- Dashboard --------------------------------------------------------------

@admin_bp.route("/")
@admin_required
def dashboard():
    """Resumen con contadores y accesos rápidos."""

    def count(model):
        return db.session.scalar(db.select(db.func.count()).select_from(model))

    stats = {
        "communities": count(Community),
        "events": count(Event),
        "users": count(User),
        "registrations": count(Registration),
    }
    return render_template("admin/dashboard.html", stats=stats)


# --- Comunidades ------------------------------------------------------------

@admin_bp.route("/comunidades")
@admin_required
def communities_list():
    communities = community_service.list_communities()
    return render_template("admin/communities_list.html", communities=communities)


@admin_bp.route("/comunidades/nueva", methods=["GET", "POST"])
@admin_required
def community_new():
    form = CommunityForm()
    if form.validate_on_submit():
        admin_service.create_community(
            name=form.name.data,
            description=form.description.data,
            cover_image=form.cover_image.data,
            is_paid=form.is_paid.data,
            price_cents=_euros_to_cents(form.price.data),
        )
        flash("Comunidad creada.", "success")
        return redirect(url_for("admin.communities_list"))
    return render_template("admin/community_form.html", form=form, title="Nueva comunidad")


@admin_bp.route("/comunidades/<int:community_id>/editar", methods=["GET", "POST"])
@admin_required
def community_edit(community_id: int):
    community = db.session.get(Community, community_id)
    if community is None:
        abort(404)

    # obj=community precarga los campos cuyo nombre coincide con un atributo.
    form = CommunityForm(obj=community)
    if request.method == "GET":
        # price no existe como atributo (guardamos price_cents): lo ponemos a mano.
        form.price.data = community.price_cents / 100

    if form.validate_on_submit():
        admin_service.update_community(
            community,
            name=form.name.data,
            description=form.description.data,
            cover_image=form.cover_image.data,
            is_paid=form.is_paid.data,
            price_cents=_euros_to_cents(form.price.data),
        )
        flash("Comunidad actualizada.", "success")
        return redirect(url_for("admin.communities_list"))
    return render_template("admin/community_form.html", form=form, title="Editar comunidad")


# --- Eventos ----------------------------------------------------------------

@admin_bp.route("/eventos")
@admin_required
def events_list():
    events = list(db.session.scalars(db.select(Event).order_by(Event.starts_at.desc())))
    return render_template("admin/events_list.html", events=events)


@admin_bp.route("/eventos/nuevo", methods=["GET", "POST"])
@admin_required
def event_new():
    form = EventForm()
    _populate_event_choices(form)
    if form.validate_on_submit():
        admin_service.create_event(
            community_id=form.community.data,
            speaker_id=form.speaker.data or None,  # 0 -> None (sin ponente)
            title=form.title.data,
            description=form.description.data,
            starts_at=_as_utc(form.starts_at.data),
            ends_at=_as_utc(form.ends_at.data),
            capacity=form.capacity.data,
            price_cents=_euros_to_cents(form.price.data),
            includes_bbq=form.includes_bbq.data,
            lodging_available=form.lodging_available.data,
            location=form.location.data,
            status=EventStatus(form.status.data),
        )
        flash("Evento creado.", "success")
        return redirect(url_for("admin.events_list"))
    return render_template("admin/event_form.html", form=form, title="Nuevo evento")


@admin_bp.route("/eventos/<int:event_id>/editar", methods=["GET", "POST"])
@admin_required
def event_edit(event_id: int):
    event = db.session.get(Event, event_id)
    if event is None:
        abort(404)

    form = EventForm(obj=event)
    _populate_event_choices(form)
    if request.method == "GET":
        # Precargamos a mano los campos que no casan 1:1 con un atributo.
        form.community.data = event.community_id
        form.speaker.data = event.speaker_id or 0
        form.status.data = event.status.value
        form.price.data = event.price_cents / 100

    if form.validate_on_submit():
        admin_service.update_event(
            event,
            community_id=form.community.data,
            speaker_id=form.speaker.data or None,
            title=form.title.data,
            description=form.description.data,
            starts_at=_as_utc(form.starts_at.data),
            ends_at=_as_utc(form.ends_at.data),
            capacity=form.capacity.data,
            price_cents=_euros_to_cents(form.price.data),
            includes_bbq=form.includes_bbq.data,
            lodging_available=form.lodging_available.data,
            location=form.location.data,
            status=EventStatus(form.status.data),
        )
        flash("Evento actualizado.", "success")
        return redirect(url_for("admin.events_list"))
    return render_template("admin/event_form.html", form=form, title="Editar evento")


@admin_bp.route("/eventos/<int:event_id>/inscripciones")
@admin_required
def event_registrations(event_id: int):
    event = db.session.get(Event, event_id)
    if event is None:
        abort(404)
    registrations = admin_service.list_event_registrations(event)
    return render_template(
        "admin/registrations.html",
        event=event,
        registrations=registrations,
        spots_left=registration_service.spots_left(event),
    )
