"""Modelo Event: un evento presencial en la finca.

Es el objeto central del negocio y lo que distingue a Patio Lab de un Skool
puro: tiene mundo físico (aforo real, ubicación, barbacoa, pernocta).
"""

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db

from .enums import EventStatus

if TYPE_CHECKING:
    from .community import Community
    from .registration import Registration
    from .user import User


class Event(db.Model):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    community_id: Mapped[int] = mapped_column(ForeignKey("communities.id"), nullable=False)

    # El ponente es un User. Es nullable porque un evento en borrador puede no
    # tener ponente asignado todavía. ondelete no se define aquí: si se borrara
    # el ponente, preferimos que el evento quede sin ponente, no borrarlo.
    speaker_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(220), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Cuándo empieza (obligatorio) y cuándo acaba (opcional).
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Aforo (plazas totales) y precio en céntimos. El control de "cuántas plazas
    # quedan" NO se guarda aquí: se calcula contando inscripciones confirmadas en
    # el servicio (Fase e). Un contador almacenado se desincroniza con facilidad.
    capacity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    price_cents: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Los flags diferenciales de Patio Lab.
    includes_bbq: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    lodging_available: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    location: Mapped[str] = mapped_column(
        String(255), default="Finca en Daimés, Elche (Alicante)", nullable=False
    )

    status: Mapped[EventStatus] = mapped_column(
        Enum(EventStatus, native_enum=False), default=EventStatus.draft, nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    # --- Relaciones ---
    community: Mapped["Community"] = relationship(back_populates="events")
    speaker: Mapped["User | None"] = relationship(back_populates="events_as_speaker")
    registrations: Mapped[list["Registration"]] = relationship(
        back_populates="event", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Event {self.slug}>"
