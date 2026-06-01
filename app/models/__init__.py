"""Paquete MODELS — la "M" de MVC: los DATOS y sus reglas.

Aquí viven las clases SQLAlchemy que se mapean a tablas. No saben nada de HTML ni
de peticiones web: solo representan datos y las reglas básicas sobre ellos.

Importamos TODOS los modelos en este __init__ por una razón concreta: Flask-Migrate
(Alembic) genera las migraciones comparando los modelos que conoce contra la base
de datos. Si un modelo no se ha importado, Python no lo ha "visto" y Alembic no
crearía su tabla. Reexportarlos aquí garantiza que con importar el paquete `models`
queden todos registrados.

`__all__` declara qué nombres se exponen al hacer `from app.models import *`.
"""

from .community import Community
from .event import Event
from .membership import Membership
from .post import Comment, Like, Post
from .registration import Registration
from .user import User

__all__ = [
    "Comment",
    "Community",
    "Event",
    "Like",
    "Membership",
    "Post",
    "Registration",
    "User",
]
