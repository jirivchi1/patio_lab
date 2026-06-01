"""Lógica de negocio de comunidades: listarlas, verlas y unirse."""

from app.extensions import db
from app.models import Community, Membership, User


def list_communities() -> list[Community]:
    """Todas las comunidades, ordenadas por nombre."""
    return list(db.session.scalars(db.select(Community).order_by(Community.name)))


def get_community_by_slug(slug: str) -> Community | None:
    """La comunidad con ese slug (el de la URL), o None si no existe."""
    return db.session.scalar(db.select(Community).filter_by(slug=slug))


def is_member(user_id: int, community_id: int) -> bool:
    """¿Pertenece este usuario a esta comunidad?"""
    membership = db.session.scalar(
        db.select(Membership).filter_by(user_id=user_id, community_id=community_id)
    )
    return membership is not None


def join_community(user: User, community: Community) -> Membership:
    """Une al usuario a la comunidad. Si ya era miembro, no duplica nada.

    Comprobamos primero en Python por comodidad, pero recuerda que aunque se nos
    colara un duplicado, la restricción UNIQUE (user_id, community_id) de la base
    de datos lo impediría igualmente. Cinturón y tirantes.
    """
    existing = db.session.scalar(
        db.select(Membership).filter_by(user_id=user.id, community_id=community.id)
    )
    if existing is not None:
        return existing

    membership = Membership(user_id=user.id, community_id=community.id)
    db.session.add(membership)
    db.session.commit()
    return membership
