"""Lógica de inscripciones a eventos: control de aforo y pago.

Esta es la parte más delicada del proyecto, por las CONDICIONES DE CARRERA:
imagina un evento con 1 plaza libre y dos personas pulsando "Inscribirme" en el
mismo instante. Si ambas leen "queda 1 plaza" antes de que ninguna guarde, las
dos pasarían el control y tendríamos un sobrecupo (2 inscritos para 1 plaza).

Cómo lo evitamos:
  - Bloqueamos la fila del evento con SELECT ... FOR UPDATE (with_for_update).
    En PostgreSQL (producción) eso obliga a las dos peticiones a hacer la
    comprobación de aforo EN FILA, una después de otra, no a la vez.
  - En SQLite (desarrollo) no existe ese bloqueo de fila, pero SQLite ya
    serializa todas las escrituras (solo un escritor a la vez), así que la
    cláusula se ignora sin error y el resultado es igualmente correcto.
"""

from dataclasses import dataclass

from app.extensions import db
from app.models import Event, Registration
from app.models.enums import EventStatus, PaymentStatus, RegistrationStatus
from app.models.user import User
from app.services.payments import get_payment_provider


@dataclass
class RegistrationResult:
    """Resultado de intentar inscribirse o cancelar.

    `code` permite al controlador reaccionar distinto si hace falta; `message` es
    el texto ya listo para mostrar al usuario.
    """

    ok: bool
    code: str  # "ok" | "not_found" | "closed" | "already" | "full" | "payment_failed"
    message: str
    registration: Registration | None = None


def confirmed_count(event_id: int) -> int:
    """Cuántas inscripciones CONFIRMADAS tiene el evento (las que ocupan plaza)."""
    return db.session.scalar(
        db.select(db.func.count())
        .select_from(Registration)
        .where(
            Registration.event_id == event_id,
            Registration.status == RegistrationStatus.confirmed,
        )
    )


def spots_left(event: Event) -> int:
    """Plazas libres = aforo - confirmadas (nunca por debajo de 0)."""
    return max(event.capacity - confirmed_count(event.id), 0)


def get_active_registration(user_id: int, event_id: int) -> Registration | None:
    """La inscripción NO cancelada del usuario en el evento, o None."""
    reg = db.session.scalar(
        db.select(Registration).filter_by(user_id=user_id, event_id=event_id)
    )
    if reg is None or reg.status == RegistrationStatus.cancelled:
        return None
    return reg


def list_user_registrations(user: User) -> list[Registration]:
    """Inscripciones confirmadas del usuario, ordenadas por fecha del evento."""
    return list(
        db.session.scalars(
            db.select(Registration)
            .join(Event)
            .where(
                Registration.user_id == user.id,
                Registration.status == RegistrationStatus.confirmed,
            )
            .order_by(Event.starts_at)
        )
    )


def register_for_event(user: User, event_id: int) -> RegistrationResult:
    """Inscribe al usuario en el evento, con control de aforo y cobro.

    Todo ocurre dentro de UNA transacción que se confirma (commit) al final, para
    que el control de aforo y la creación de la inscripción sean atómicos.
    """
    # Bloqueamos la fila del evento durante esta transacción (ver explicación
    # arriba). Si el evento no existe, salimos.
    event = db.session.scalar(
        db.select(Event).where(Event.id == event_id).with_for_update()
    )
    if event is None:
        return RegistrationResult(False, "not_found", "El evento no existe.")

    # Solo se puede uno inscribir a eventos PUBLICADOS (no borradores, ni
    # cancelados, ni ya celebrados).
    if event.status != EventStatus.published:
        return RegistrationResult(
            False, "closed", "Las inscripciones para este evento no están abiertas."
        )

    # ¿Ya tenía una inscripción? (puede estar cancelada y querer volver).
    existing = db.session.scalar(
        db.select(Registration).filter_by(user_id=user.id, event_id=event.id)
    )
    if existing is not None and existing.status != RegistrationStatus.cancelled:
        return RegistrationResult(
            False, "already", "Ya estás inscrito en este evento.", existing
        )

    # CONTROL DE AFORO: si las plazas confirmadas llegan al aforo, está completo.
    if confirmed_count(event.id) >= event.capacity:
        return RegistrationResult(False, "full", "El evento está completo.")

    # COBRO: si el evento es de pago, pasamos por el proveedor (hoy, el falso).
    # Si es gratis, no hay nada que cobrar.
    if event.price_cents > 0:
        provider = get_payment_provider()
        payment = provider.charge(
            amount_cents=event.price_cents,
            description=f"Inscripción: {event.title}",
            user=user,
        )
        if not payment.success:
            return RegistrationResult(
                False, "payment_failed", "No se pudo procesar el pago. Inténtalo de nuevo."
            )

    # Marcamos como pagada: en el evento gratis no se debe nada; en el de pago, el
    # proveedor (falso) confirmó el cobro.
    if existing is not None:
        # Reutilizamos la inscripción cancelada en vez de crear otra (respeta la
        # unicidad user+event y conserva el id).
        existing.status = RegistrationStatus.confirmed
        existing.payment_status = PaymentStatus.paid
        registration = existing
    else:
        registration = Registration(
            user_id=user.id,
            event_id=event.id,
            status=RegistrationStatus.confirmed,
            payment_status=PaymentStatus.paid,
        )
        db.session.add(registration)

    db.session.commit()
    return RegistrationResult(True, "ok", "¡Inscripción confirmada!", registration)


def cancel_registration(user: User, event_id: int) -> RegistrationResult:
    """Cancela la inscripción del usuario. La plaza queda libre al instante."""
    reg = get_active_registration(user.id, event_id)
    if reg is None:
        return RegistrationResult(False, "not_found", "No tienes una inscripción activa.")

    reg.status = RegistrationStatus.cancelled
    # Si había pago, lo marcamos como reembolsado (el proveedor falso no mueve
    # dinero; con uno real, aquí dispararíamos el reembolso).
    if reg.payment_status == PaymentStatus.paid:
        reg.payment_status = PaymentStatus.refunded
    db.session.commit()
    return RegistrationResult(True, "ok", "Has cancelado tu inscripción.", reg)
