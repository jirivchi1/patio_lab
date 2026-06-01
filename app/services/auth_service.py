"""Lógica de negocio de autenticación.

El controlador (auth_controller) solo coordina; la lógica de crear usuarios y
buscarlos vive aquí. Así se puede testear sin pasar por HTTP.
"""

from app.extensions import db
from app.models import User


def normalize_email(email: str) -> str:
    """Email en minúsculas y sin espacios alrededor.

    Guardamos los emails normalizados para que 'Ana@Mail.com ' y 'ana@mail.com'
    se traten como el mismo, y para que la comprobación de unicidad funcione.
    """
    return email.strip().lower()


def get_user_by_email(email: str) -> User | None:
    """Devuelve el usuario con ese email, o None si no existe."""
    return db.session.scalar(db.select(User).filter_by(email=normalize_email(email)))


def register_user(name: str, email: str, password: str) -> User:
    """Crea un usuario nuevo con la contraseña ya hasheada y lo guarda."""
    user = User(name=name.strip(), email=normalize_email(email))
    user.set_password(password)  # hashea; nunca guardamos la contraseña en claro
    db.session.add(user)
    db.session.commit()
    return user
