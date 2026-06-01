"""Modelo User: las personas registradas en Patio Lab.

Notas de estilo (SQLAlchemy 2.0, el moderno y "profesional"):
  - `Mapped[tipo]` + `mapped_column(...)` declara cada columna con su tipo Python.
    El tipo ya nos da type hints gratis (Mapped[str | None] = puede ser nulo).
  - Las relaciones se declaran con `relationship(...)`; SQLAlchemy deduce la tabla
    destino a partir del tipo anotado (Mapped[list["Post"]]).
"""

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from flask_login import UserMixin
from sqlalchemy import DateTime, Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db

from .enums import UserRole

# Imports SOLO para los chequeos de tipos / el linter, no en runtime. Así las
# referencias en Mapped[list["Post"]] tienen un nombre conocido, pero NO se
# ejecutan al importar (evitando imports circulares entre modelos). SQLAlchemy
# resuelve las relaciones por su registro interno, no por estos imports.
if TYPE_CHECKING:
    from .community import Community  # noqa: F401
    from .event import Event
    from .membership import Membership
    from .post import Comment, Like, Post
    from .registration import Registration


class User(UserMixin, db.Model):
    # UserMixin (de Flask-Login) añade gratis propiedades como is_authenticated,
    # is_active y el método get_id(). Las usará la auth en la Fase (c); ponerlo
    # ahora no estorba.
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Email único e indexado: lo buscaremos en cada login, y el índice hace
    # esa búsqueda rápida además de impedir duplicados.
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)

    # NUNCA guardamos la contraseña en claro: solo su hash (ver set_password).
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    name: Mapped[str] = mapped_column(String(120), nullable=False)

    # Rol global. native_enum=False guarda el valor como texto + un CHECK, en vez
    # de crear un tipo ENUM nativo. Es más portable entre SQLite y PostgreSQL y
    # hace las migraciones más sencillas.
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, native_enum=False), default=UserRole.member, nullable=False
    )

    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    avatar: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Gamificación de la Fase 2: el campo existe y arranca a 0, pero la lógica que
    # suma puntos todavía no está implementada.
    points: Mapped[int] = mapped_column(default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    # --- Relaciones (el "otro lado" se define en cada modelo con back_populates) ---
    # cascade="all, delete-orphan": si se borra el usuario, se borran sus filas
    # dependientes (membresías, posts...). No aplica a events_as_speaker: borrar
    # un ponente no debe borrar los eventos.
    memberships: Mapped[list["Membership"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    posts: Mapped[list["Post"]] = relationship(
        back_populates="author", cascade="all, delete-orphan"
    )
    comments: Mapped[list["Comment"]] = relationship(
        back_populates="author", cascade="all, delete-orphan"
    )
    likes: Mapped[list["Like"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    events_as_speaker: Mapped[list["Event"]] = relationship(back_populates="speaker")
    registrations: Mapped[list["Registration"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    # --- Contraseñas ---
    def set_password(self, raw_password: str) -> None:
        """Genera y guarda el hash de la contraseña (con sal, vía werkzeug)."""
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        """Comprueba una contraseña contra el hash guardado, sin descifrar nada."""
        return check_password_hash(self.password_hash, raw_password)

    def __repr__(self) -> str:
        return f"<User {self.email}>"
