"""Tests del panel de administración: gating por rol, slugs y CRUD."""

from datetime import UTC, datetime, timedelta

from app.extensions import db
from app.models import Community, Event
from app.models.enums import UserRole


def test_admin_redirects_anonymous(client):
    # Sin sesión: redirige (302) al login.
    response = client.get("/admin/")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_admin_forbidden_for_normal_user(client, make_user, login):
    make_user(email="bob@mail.com")  # rol por defecto: member
    login(email="bob@mail.com")
    assert client.get("/admin/").status_code == 403


def test_admin_accessible_for_admin(client, make_user, login):
    make_user(email="admin@mail.com", role=UserRole.admin)
    login(email="admin@mail.com")
    assert client.get("/admin/").status_code == 200


def test_create_community_generates_slug_and_cents(client, make_user, login):
    make_user(email="admin@mail.com", role=UserRole.admin)
    login(email="admin@mail.com")
    client.post(
        "/admin/comunidades/nueva",
        data={"name": "Impresión 3D", "description": "3D", "is_paid": "y", "price": "9.99"},
        follow_redirects=True,
    )
    community = db.session.scalar(db.select(Community).filter_by(name="Impresión 3D"))
    assert community.slug == "impresion-3d"
    assert community.price_cents == 999  # 9,99 € -> céntimos
    assert community.is_paid is True


def test_slug_uniqueness(client, make_user, login):
    make_user(email="admin@mail.com", role=UserRole.admin)
    login(email="admin@mail.com")
    for _ in range(2):
        client.post(
            "/admin/comunidades/nueva",
            data={"name": "Impresión 3D", "price": "0"},
            follow_redirects=True,
        )
    slugs = sorted(
        c.slug for c in db.session.scalars(db.select(Community).filter_by(name="Impresión 3D"))
    )
    assert slugs == ["impresion-3d", "impresion-3d-2"]


def test_edit_keeps_slug_stable(client, make_user, make_community, login):
    make_user(email="admin@mail.com", role=UserRole.admin)
    community = make_community(name="Permacultura", slug="permacultura")
    login(email="admin@mail.com")
    client.post(
        f"/admin/comunidades/{community.id}/editar",
        data={"name": "Permacultura Avanzada", "price": "0"},
        follow_redirects=True,
    )
    db.session.refresh(community)
    assert community.name == "Permacultura Avanzada"
    assert community.slug == "permacultura"  # el slug NO cambia al editar


def test_create_event(client, make_user, make_community, login):
    make_user(email="admin@mail.com", role=UserRole.admin)
    community = make_community()
    login(email="admin@mail.com")

    starts = (datetime.now(UTC) + timedelta(days=20)).strftime("%Y-%m-%dT%H:%M")
    client.post(
        "/admin/eventos/nuevo",
        data={
            "community": community.id, "speaker": 0, "title": "Taller FPV",
            "description": "drones", "starts_at": starts, "capacity": "10",
            "price": "12.50", "includes_bbq": "y", "location": "Finca", "status": "published",
        },
        follow_redirects=True,
    )
    event = db.session.scalar(db.select(Event).filter_by(title="Taller FPV"))
    assert event is not None
    assert event.slug == "taller-fpv"
    assert event.price_cents == 1250
    assert event.includes_bbq is True
    assert event.speaker_id is None  # "— Sin ponente —"
