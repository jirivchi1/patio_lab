"""Modelo Membership: la tabla INTERMEDIA entre User y Community.

Un usuario puede estar en muchas comunidades, y una comunidad tiene muchos
usuarios: es una relación "muchos a muchos". En SQL eso se modela con una tabla
intermedia. La hacemos un modelo propio (en vez de una tabla anónima) porque
guarda datos extra de la relación: el rol del usuario en ESA comunidad y cuándo
se unió.
"""

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db

from .enums import CommunityRole

if TYPE_CHECKING:
    from .community import Community
    from .user import User


class Membership(db.Model):
    __tablename__ = "memberships"

    # Una persona no puede estar dos veces en la misma comunidad. Esta restricción
    # de unicidad sobre el PAR de columnas lo impide a nivel de base de datos
    # (la garantía más fuerte: no depende de que el código se acuerde de mirar).
    __table_args__ = (UniqueConstraint("user_id", "community_id", name="uq_user_community"),)

    id: Mapped[int] = mapped_column(primary_key=True)

    # ForeignKey enlaza esta fila con una de la tabla destino. "users.id" usa el
    # nombre de tabla (__tablename__), no el de la clase.
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    community_id: Mapped[int] = mapped_column(ForeignKey("communities.id"), nullable=False)

    role_in_community: Mapped[CommunityRole] = mapped_column(
        Enum(CommunityRole, native_enum=False), default=CommunityRole.member, nullable=False
    )

    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    # --- Relaciones (los dos lados de la tabla intermedia) ---
    user: Mapped["User"] = relationship(back_populates="memberships")
    community: Mapped["Community"] = relationship(back_populates="memberships")

    def __repr__(self) -> str:
        return f"<Membership user={self.user_id} community={self.community_id}>"
