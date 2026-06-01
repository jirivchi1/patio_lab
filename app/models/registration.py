"""Modelo Registration: la inscripción de un usuario a un evento.

Conecta User con Event y guarda el estado de la inscripción y del pago. Es la
tabla donde se cruza la comunidad online con el evento físico.
"""

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db

from .enums import PaymentStatus, RegistrationStatus

if TYPE_CHECKING:
    from .event import Event
    from .user import User


class Registration(db.Model):
    __tablename__ = "registrations"

    # Un usuario no puede inscribirse dos veces al mismo evento. La unicidad sobre
    # el par (user, event) lo garantiza en la base de datos.
    __table_args__ = (UniqueConstraint("user_id", "event_id", name="uq_user_event"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), nullable=False)

    status: Mapped[RegistrationStatus] = mapped_column(
        Enum(RegistrationStatus, native_enum=False),
        default=RegistrationStatus.confirmed,
        nullable=False,
    )
    payment_status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus, native_enum=False),
        default=PaymentStatus.unpaid,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    # --- Relaciones ---
    user: Mapped["User"] = relationship(back_populates="registrations")
    event: Mapped["Event"] = relationship(back_populates="registrations")

    def __repr__(self) -> str:
        return f"<Registration user={self.user_id} event={self.event_id}>"
