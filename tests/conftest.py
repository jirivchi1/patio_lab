"""Fixtures compartidas por todos los tests.

Una "fixture" de pytest es una pieza de preparación reutilizable: una función
decorada con @pytest.fixture que los tests piden simplemente poniéndola como
parámetro. pytest la ejecuta antes del test y, si usa yield, limpia después.

Estrategia de base de datos:
  - Usamos la config 'testing': SQLite EN MEMORIA (no toca tu BD de desarrollo).
  - La fixture `app` es de alcance "function" (por defecto): se crea una app y
    una BD nuevas para CADA test, y se destruyen al acabar. Así un test nunca
    contamina a otro: aislamiento total.
"""

import pytest

from app import create_app
from app.extensions import db as _db


@pytest.fixture
def app():
    """App de test con la BD creada; se limpia al terminar cada test."""
    app = create_app("testing")
    with app.app_context():
        _db.create_all()
        yield app  # aquí se ejecuta el test
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    """Cliente HTTP de prueba: simula peticiones sin levantar un servidor real."""
    return app.test_client()


@pytest.fixture
def make_user(app):
    """Fábrica para crear usuarios en la BD de test.

    Devuelve una FUNCIÓN, así cada test puede crear los usuarios que necesite con
    los datos que quiera: make_user(email="otro@mail.com", role=UserRole.admin).
    """
    from app.services.auth_service import register_user

    def _make(name="Ana", email="ana@mail.com", password="secreta123", role=None):
        user = register_user(name, email, password)
        if role is not None:
            user.role = role
            _db.session.commit()
        return user

    return _make


@pytest.fixture
def login(client):
    """Helper para iniciar sesión en el cliente de test (CSRF va desactivado)."""

    def _login(email="ana@mail.com", password="secreta123"):
        return client.post("/login", data={"email": email, "password": password})

    return _login


@pytest.fixture
def make_community(app):
    """Fábrica para crear comunidades de prueba."""
    from app.models import Community

    def _make(name="Permacultura", slug="permacultura", **kwargs):
        community = Community(name=name, slug=slug, **kwargs)
        _db.session.add(community)
        _db.session.commit()
        return community

    return _make


@pytest.fixture
def make_event(app, make_community):
    """Fábrica para crear eventos de prueba (publicados por defecto)."""
    from datetime import UTC, datetime, timedelta

    from app.models import Community, Event
    from app.models.enums import EventStatus

    def _make(*, community=None, capacity=2, price_cents=0,
              status=EventStatus.published, title="Evento", slug="evento"):
        if community is None:
            # Reutiliza la comunidad por defecto si ya existe, o la crea.
            community = _db.session.scalar(
                _db.select(Community).filter_by(slug="permacultura")
            ) or make_community()
        event = Event(
            community_id=community.id,
            title=title,
            slug=slug,
            starts_at=datetime.now(UTC) + timedelta(days=10),
            capacity=capacity,
            price_cents=price_cents,
            status=status,
        )
        _db.session.add(event)
        _db.session.commit()
        return event

    return _make
