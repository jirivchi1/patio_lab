"""Modelo Community: un grupo temático (permacultura, impresión 3D, drones...).

Cada comunidad tiene su descripción, sus miembros (vía Membership) y su feed
(vía Post). Puede ser gratuita o de pago recurrente.
"""

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db

if TYPE_CHECKING:
    from .event import Event
    from .membership import Membership
    from .post import Post


class Community(db.Model):
    __tablename__ = "communities"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(120), nullable=False)

    # El slug es la versión "para URL" del nombre: "Economía Regenerativa" ->
    # "economia-regenerativa". Único e indexado porque las URLs serán /c/<slug>.
    slug: Mapped[str] = mapped_column(String(140), unique=True, index=True, nullable=False)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    cover_image: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # ¿Es de pago? Y si lo es, cuánto cuesta la membresía.
    is_paid: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # DINERO EN CÉNTIMOS (entero), nunca float: 12,00 € se guarda como 1200.
    # Los float dan errores de redondeo; los céntimos enteros son exactos.
    price_cents: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    # --- Relaciones ---
    memberships: Mapped[list["Membership"]] = relationship(
        back_populates="community", cascade="all, delete-orphan"
    )
    posts: Mapped[list["Post"]] = relationship(
        back_populates="community", cascade="all, delete-orphan"
    )
    events: Mapped[list["Event"]] = relationship(
        back_populates="community", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Community {self.slug}>"
