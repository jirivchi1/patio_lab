"""Proveedor de pago FALSO para desarrollo.

No cobra nada y siempre da el pago por bueno. Permite construir y probar todo el
flujo de inscripciones sin tener cuentas de Stripe/PayPal ni mover dinero real.
Cuando llegue el momento, crearemos un StripePaymentProvider con la misma firma y
lo seleccionaremos en payments/__init__.py; el resto del código no se entera.
"""

import uuid

from app.models import User

from .base import PaymentProvider, PaymentResult


class FakePaymentProvider(PaymentProvider):
    def charge(self, *, amount_cents: int, description: str, user: User) -> PaymentResult:
        # Generamos una referencia ficticia para imitar a un proveedor real.
        reference = f"FAKE-{uuid.uuid4().hex[:12]}"
        return PaymentResult(
            success=True,
            reference=reference,
            message=f"Pago simulado de {amount_cents} céntimos (sin cobro real).",
        )
