"""Lógica de negocio de eventos (consultas y listados)."""

from datetime import UTC, datetime

from app.extensions import db
from app.models import Event
from app.models.enums import EventStatus


def get_event_by_slug(slug: str) -> Event | None:
    """El evento con ese slug (el de la URL), o None."""
    return db.session.scalar(db.select(Event).filter_by(slug=slug))


def list_upcoming_events(limit: int | None = None) -> list[Event]:
    """Eventos PUBLICADOS cuya fecha aún no ha pasado, del más próximo al más lejano.

    Filtramos por estado 'published' (los borradores no se muestran) y por fecha
    futura. El parámetro limit sirve para la landing, que solo enseña unos pocos.
    """
    query = (
        db.select(Event)
        .where(Event.status == EventStatus.published, Event.starts_at >= datetime.now(UTC))
        .order_by(Event.starts_at)
    )
    if limit is not None:
        query = query.limit(limit)
    return list(db.session.scalars(query))
