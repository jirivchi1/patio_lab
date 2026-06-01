"""Paquete de pagos.

Expone `get_payment_provider()`: el ÚNICO sitio donde se decide qué proveedor de
pago usa la app. Hoy devuelve siempre el falso. El día que integremos Stripe,
cambiaremos solo esta función (p. ej. leyendo una variable de config para elegir),
y ni los servicios ni los controladores tendrán que cambiar.
"""

from .base import PaymentProvider, PaymentResult
from .fake import FakePaymentProvider


def get_payment_provider() -> PaymentProvider:
    """Devuelve el proveedor de pago configurado."""
    return FakePaymentProvider()


__all__ = [
    "FakePaymentProvider",
    "PaymentProvider",
    "PaymentResult",
    "get_payment_provider",
]
