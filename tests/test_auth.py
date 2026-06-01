"""Tests del registro, login y logout.

Cada función test_* es un caso. pytest pasa las fixtures que pidamos por nombre
(client, make_user, login...). Un `assert` que falle marca el test como fallido.
"""

from app.extensions import db
from app.models import User


def _count_users() -> int:
    return db.session.scalar(db.select(db.func.count()).select_from(User))


def test_register_creates_user_and_logs_in(client):
    response = client.post(
        "/register",
        data={"name": "Ana", "email": "ana@mail.com",
              "password": "secreta123", "confirm": "secreta123"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    # Tras registrarse queda logueado: su nombre sale en la barra de navegación.
    assert "Hola, Ana" in response.get_data(as_text=True)
    assert _count_users() == 1


def test_register_normalizes_email(client):
    # Email con espacios y mayúsculas: debe guardarse limpio y en minúsculas.
    client.post(
        "/register",
        data={"name": "Ana", "email": "  Ana@Mail.com  ",
              "password": "secreta123", "confirm": "secreta123"},
        follow_redirects=True,
    )
    user = db.session.scalar(db.select(User))
    assert user.email == "ana@mail.com"


def test_register_duplicate_email_rejected(client, make_user):
    make_user(email="ana@mail.com")  # ya existe
    response = client.post(
        "/register",
        data={"name": "Otra", "email": "ana@mail.com",
              "password": "secreta123", "confirm": "secreta123"},
    )
    assert "Ya existe una cuenta" in response.get_data(as_text=True)
    assert _count_users() == 1  # no se creó un segundo usuario


def test_register_password_mismatch(client):
    response = client.post(
        "/register",
        data={"name": "Ana", "email": "ana@mail.com",
              "password": "secreta123", "confirm": "distinta"},
    )
    assert "no coinciden" in response.get_data(as_text=True)
    assert _count_users() == 0


def test_password_is_hashed_not_plaintext(client, make_user):
    user = make_user(password="secreta123")
    assert user.password_hash != "secreta123"
    assert user.check_password("secreta123") is True
    assert user.check_password("incorrecta") is False


def test_login_wrong_password(client, make_user, login):
    make_user(email="ana@mail.com", password="secreta123")
    response = login(email="ana@mail.com", password="mal")
    response = client.get("/")
    # Sigue sin sesión: la nav muestra "Entrar", no el saludo.
    assert ">Entrar<" in response.get_data(as_text=True)


def test_login_and_logout_flow(client, make_user, login):
    make_user(name="Ana", email="ana@mail.com", password="secreta123")
    login()
    assert "Hola, Ana" in client.get("/").get_data(as_text=True)
    client.get("/logout")
    assert ">Entrar<" in client.get("/").get_data(as_text=True)
