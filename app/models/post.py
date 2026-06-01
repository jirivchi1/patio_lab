"""Modelos del feed de una comunidad: Post, Comment y Like.

Van en el mismo archivo porque forman una unidad: un post tiene comentarios y
likes, y unos no tienen sentido sin el otro.
"""

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db

if TYPE_CHECKING:
    from .community import Community
    from .user import User


class Post(db.Model):
    """Una publicación en el feed de una comunidad."""

    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    community_id: Mapped[int] = mapped_column(ForeignKey("communities.id"), nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    # onupdate: SQLAlchemy actualiza esta fecha automáticamente cada vez que se
    # modifica la fila, para saber cuándo se editó por última vez.
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # --- Relaciones ---
    community: Mapped["Community"] = relationship(back_populates="posts")
    author: Mapped["User"] = relationship(back_populates="posts")
    # Si se borra el post, se borran sus comentarios y likes (delete-orphan).
    comments: Mapped[list["Comment"]] = relationship(
        back_populates="post", cascade="all, delete-orphan"
    )
    likes: Mapped[list["Like"]] = relationship(
        back_populates="post", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Post {self.id} by user={self.author_id}>"


class Comment(db.Model):
    """Un comentario dentro de un post."""

    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    post: Mapped["Post"] = relationship(back_populates="comments")
    author: Mapped["User"] = relationship(back_populates="comments")

    def __repr__(self) -> str:
        return f"<Comment {self.id} on post={self.post_id}>"


class Like(db.Model):
    """Un "me gusta" de un usuario a un post."""

    __tablename__ = "likes"

    # Un usuario solo puede dar UN like por post. Esta unicidad sobre el par de
    # columnas convierte el botón en un interruptor (dar/quitar), sin duplicados.
    __table_args__ = (UniqueConstraint("post_id", "user_id", name="uq_post_user_like"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    post: Mapped["Post"] = relationship(back_populates="likes")
    user: Mapped["User"] = relationship(back_populates="likes")

    def __repr__(self) -> str:
        return f"<Like post={self.post_id} user={self.user_id}>"
