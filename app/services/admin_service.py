"""Lógica del panel de administración: crear y editar comunidades y eventos.

Decisión de diseño: el SLUG se genera al CREAR y luego NO cambia, aunque edites
el nombre. ¿Por qué? Porque el slug está en la URL (/comunidades/permacultura);
si cambiara al editar, romperíamos enlaces guardados y posiciones en buscadores.
"""

from datetime import datetime

from sqlalchemy.orm import DeclarativeBase

from app.extensions import db
from app.models import Community, Event, Registration, User
from app.models.enums import EventStatus, UserRole
from app.utils.slugs import slugify


def _unique_slug(text: str, model: type[DeclarativeBase]) -> str:
    """Genera un slug único para `model` a partir de `text`.

    Si "taller-3d" ya existe, prueba "taller-3d-2", "taller-3d-3"... hasta dar con
    uno libre. Así nunca chocan dos slugs (la columna slug es UNIQUE).
    """
    base = slugify(text) or "item"
    slug = base
    counter = 2
    while db.session.scalar(db.select(model).filter_by(slug=slug)) is not None:
        slug = f"{base}-{counter}"
        counter += 1
    return slug


def list_possible_speakers() -> list[User]:
    """Usuarios que pueden figurar como ponentes (rol speaker o admin)."""
    return list(
        db.session.scalars(
            db.select(User)
            .where(User.role.in_([UserRole.speaker, UserRole.admin]))
            .order_by(User.name)
        )
    )


# --- Comunidades ------------------------------------------------------------

def create_community(
    *, name: str, description: str | None, cover_image: str | None, is_paid: bool, price_cents: int
) -> Community:
    community = Community(
        name=name,
        slug=_unique_slug(name, Community),
        description=description or None,
        cover_image=cover_image or None,
        is_paid=is_paid,
        price_cents=price_cents,
    )
    db.session.add(community)
    db.session.commit()
    return community


def update_community(
    community: Community,
    *,
    name: str,
    description: str | None,
    cover_image: str | None,
    is_paid: bool,
    price_cents: int,
) -> None:
    # Nota: NO tocamos community.slug a propósito (ver explicación arriba).
    community.name = name
    community.description = description or None
    community.cover_image = cover_image or None
    community.is_paid = is_paid
    community.price_cents = price_cents
    db.session.commit()


# --- Eventos ----------------------------------------------------------------

def create_event(
    *,
    community_id: int,
    speaker_id: int | None,
    title: str,
    description: str | None,
    starts_at: datetime,
    ends_at: datetime | None,
    capacity: int,
    price_cents: int,
    includes_bbq: bool,
    lodging_available: bool,
    location: str,
    status: EventStatus,
) -> Event:
    event = Event(
        community_id=community_id,
        speaker_id=speaker_id,
        title=title,
        slug=_unique_slug(title, Event),
        description=description or None,
        starts_at=starts_at,
        ends_at=ends_at,
        capacity=capacity,
        price_cents=price_cents,
        includes_bbq=includes_bbq,
        lodging_available=lodging_available,
        location=location,
        status=status,
    )
    db.session.add(event)
    db.session.commit()
    return event


def update_event(
    event: Event,
    *,
    community_id: int,
    speaker_id: int | None,
    title: str,
    description: str | None,
    starts_at: datetime,
    ends_at: datetime | None,
    capacity: int,
    price_cents: int,
    includes_bbq: bool,
    lodging_available: bool,
    location: str,
    status: EventStatus,
) -> None:
    event.community_id = community_id
    event.speaker_id = speaker_id
    event.title = title
    event.description = description or None
    event.starts_at = starts_at
    event.ends_at = ends_at
    event.capacity = capacity
    event.price_cents = price_cents
    event.includes_bbq = includes_bbq
    event.lodging_available = lodging_available
    event.location = location
    event.status = status
    db.session.commit()


def list_event_registrations(event: Event) -> list[Registration]:
    """Todas las inscripciones de un evento, las más recientes primero."""
    return list(
        db.session.scalars(
            db.select(Registration)
            .filter_by(event_id=event.id)
            .order_by(Registration.created_at.desc())
        )
    )
