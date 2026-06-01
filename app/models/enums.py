"""Enumeraciones del dominio.

Un Enum es un tipo CERRADO: una variable solo puede tomar uno de un conjunto fijo
de valores. Lo usamos para roles y estados porque evita errores tontos: si en algún
sitio escribiéramos el texto "amdin" en vez de "admin", un campo de texto libre lo
aceptaría y los permisos se romperían en silencio. Con un Enum, eso ni cuela.

Heredamos de `enum.StrEnum` (Python 3.11+): cada miembro se comporta también como
una cadena, así que comparar `user.role == "admin"` funciona y en la base de datos
se guarda el texto legible ("admin", "published"...).
"""

from enum import StrEnum


class UserRole(StrEnum):
    """Rol GLOBAL del usuario en toda la plataforma."""

    visitor = "visitor"  # registrado pero sin pertenecer a nada todavía
    member = "member"  # usuario normal
    speaker = "speaker"  # ponente que imparte eventos
    admin = "admin"  # tú: control total


class CommunityRole(StrEnum):
    """Rol del usuario DENTRO de una comunidad concreta (en la tabla Membership)."""

    member = "member"
    moderator = "moderator"
    owner = "owner"


class EventStatus(StrEnum):
    """Ciclo de vida de un evento."""

    draft = "draft"  # se está preparando; no visible al público
    published = "published"  # publicado y abierto a inscripciones
    cancelled = "cancelled"  # anulado
    completed = "completed"  # ya celebrado


class RegistrationStatus(StrEnum):
    """Estado de una inscripción a un evento."""

    confirmed = "confirmed"  # ocupa plaza
    waitlist = "waitlist"  # en lista de espera (preparado; uso pleno en fase 2)
    cancelled = "cancelled"  # el usuario se dio de baja; libera plaza


class PaymentStatus(StrEnum):
    """Estado del pago de una inscripción (de momento lo gestiona FakePaymentProvider)."""

    unpaid = "unpaid"
    paid = "paid"
    refunded = "refunded"
