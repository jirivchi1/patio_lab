"""Tests de inscripciones a eventos: aforo, pago, cancelación.

Probamos sobre todo el SERVICIO (registration_service) directamente, porque ahí
vive la lógica delicada del aforo y es donde más valor tiene blindarla.
"""

from app.models.enums import EventStatus, PaymentStatus
from app.services import registration_service as reg


def test_spots_left_starts_at_capacity(make_event):
    event = make_event(capacity=5)
    assert reg.spots_left(event) == 5


def test_register_confirms_and_marks_paid(make_user, make_event):
    user = make_user()
    event = make_event(capacity=2, price_cents=1500)
    result = reg.register_for_event(user, event.id)
    assert result.ok is True
    assert result.registration.payment_status == PaymentStatus.paid
    assert reg.spots_left(event) == 1


def test_capacity_full_blocks_second_user(make_user, make_event):
    # Evento con UNA sola plaza.
    event = make_event(capacity=1)
    ana = make_user(name="Ana", email="ana@mail.com")
    bob = make_user(name="Bob", email="bob@mail.com")

    assert reg.register_for_event(ana, event.id).ok is True
    second = reg.register_for_event(bob, event.id)
    assert second.ok is False
    assert second.code == "full"
    assert reg.spots_left(event) == 0


def test_double_registration_blocked(make_user, make_event):
    user = make_user()
    event = make_event(capacity=5)
    reg.register_for_event(user, event.id)
    again = reg.register_for_event(user, event.id)
    assert again.code == "already"


def test_cannot_register_to_draft(make_user, make_event):
    user = make_user()
    event = make_event(status=EventStatus.draft)
    result = reg.register_for_event(user, event.id)
    assert result.code == "closed"


def test_cancel_frees_spot(make_user, make_event):
    event = make_event(capacity=1, price_cents=1500)
    ana = make_user(name="Ana", email="ana@mail.com")
    bob = make_user(name="Bob", email="bob@mail.com")

    reg.register_for_event(ana, event.id)
    assert reg.register_for_event(bob, event.id).code == "full"  # lleno

    cancel = reg.cancel_registration(ana, event.id)
    assert cancel.ok is True
    assert cancel.registration.payment_status == PaymentStatus.refunded
    assert reg.spots_left(event) == 1

    # Ahora Bob sí entra.
    assert reg.register_for_event(bob, event.id).ok is True


def test_free_event_is_marked_paid(make_user, make_event):
    user = make_user()
    event = make_event(price_cents=0)
    result = reg.register_for_event(user, event.id)
    # Gratis: nada que cobrar, lo dejamos como "saldado" (paid).
    assert result.registration.payment_status == PaymentStatus.paid


def test_register_and_cancel_via_http(client, make_user, make_event, login):
    make_user()
    event = make_event(capacity=3, price_cents=1500)
    login()

    # Inscribirse por HTTP.
    response = client.post(f"/eventos/{event.slug}/inscribirse", follow_redirects=True)
    assert "inscrito" in response.get_data(as_text=True)

    # Aparece en el perfil.
    assert event.title in client.get("/perfil").get_data(as_text=True)

    # Cancelar por HTTP.
    response = client.post(f"/eventos/{event.slug}/cancelar", follow_redirects=True)
    assert "Inscribirme" in response.get_data(as_text=True)
