"""Lógica de negocio del feed: posts, comentarios y likes."""

from app.extensions import db
from app.models import Comment, Community, Like, Post, User


def list_posts(community: Community) -> list[Post]:
    """Publicaciones de una comunidad, las más recientes primero."""
    return list(
        db.session.scalars(
            db.select(Post)
            .filter_by(community_id=community.id)
            .order_by(Post.created_at.desc())
        )
    )


def get_post(post_id: int) -> Post | None:
    """Una publicación por su id (búsqueda por clave primaria)."""
    return db.session.get(Post, post_id)


def create_post(community: Community, author: User, body: str) -> Post:
    """Crea una publicación en el feed de la comunidad."""
    post = Post(community_id=community.id, author_id=author.id, body=body.strip())
    db.session.add(post)
    db.session.commit()
    return post


def add_comment(post: Post, author: User, body: str) -> Comment:
    """Añade un comentario a una publicación."""
    comment = Comment(post_id=post.id, author_id=author.id, body=body.strip())
    db.session.add(comment)
    db.session.commit()
    return comment


def like_count(post_id: int) -> int:
    """Cuántos likes tiene una publicación (consulta de conteo)."""
    return db.session.scalar(
        db.select(db.func.count()).select_from(Like).where(Like.post_id == post_id)
    )


def toggle_like(post: Post, user: User) -> tuple[bool, int]:
    """Da o quita el like de un usuario (interruptor) y devuelve (estado, total).

    Si ya existía un like de este usuario en este post, lo borra (quitar like).
    Si no existía, lo crea (dar like). Devuelve si AHORA está marcado y el total
    actualizado, que es justo lo que el JavaScript necesita para refrescar el botón.
    """
    existing = db.session.scalar(
        db.select(Like).filter_by(post_id=post.id, user_id=user.id)
    )
    if existing is not None:
        db.session.delete(existing)
        liked = False
    else:
        db.session.add(Like(post_id=post.id, user_id=user.id))
        liked = True
    db.session.commit()
    return liked, like_count(post.id)


def liked_post_ids(user_id: int, posts: list[Post]) -> set[int]:
    """De entre estos posts, cuáles ha likeado el usuario (en UNA sola consulta).

    Lo usamos al pintar el feed para saber qué botones de like deben salir ya
    'encendidos'. Hacerlo de una vez evita una consulta por cada post (problema
    conocido como "N+1").
    """
    if not user_id or not posts:
        return set()
    post_ids = [p.id for p in posts]
    rows = db.session.scalars(
        db.select(Like.post_id).where(
            Like.user_id == user_id, Like.post_id.in_(post_ids)
        )
    )
    return set(rows)
