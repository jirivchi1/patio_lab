"""Interfaz de pagos: el "contrato" que cumple cualquier proveedor de pago.

La idea (patrón Strategy): el resto de la app NUNCA habla con Stripe o PayPal
directamente. Habla con esta interfaz abstracta `PaymentProvider`. Hoy detrás hay
un proveedor FALSO; mañana habrá uno real. Como ambos cumplen el mismo contrato,
cambiar de uno a otro no obliga a tocar la lógica de inscripciones.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.models import User


@dataclass
class PaymentResult:
    """Lo que devuelve un intento de cobro.

    success: ¿se cobró correctamente?
    reference: identificador de la transacción (para guardarlo/auditar).
    message: texto explicativo (útil para mostrar o registrar).
    """

    success: bool
    reference: str
    message: str = ""


class PaymentProvider(ABC):
    """Contrato que todo proveedor de pago debe cumplir.

    ABC = Abstract Base Class. No se puede instanciar directamente; sirve para
    OBLIGAR a que las implementaciones (FakePaymentProvider, y en el futuro
    StripePaymentProvider) definan el método `charge`.
    """

    @abstractmethod
    def charge(self, *, amount_cents: int, description: str, user: User) -> PaymentResult:
        """Cobra `amount_cents` al usuario. Devuelve un PaymentResult.

        El asterisco (*) obliga a llamar a este método con argumentos NOMBRADOS
        (charge(amount_cents=.., description=.., user=..)), para que nunca se
        confunda el orden de los parámetros.
        """
        ...
