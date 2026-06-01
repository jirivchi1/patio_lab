"""Funciones de formato para mostrar datos al usuario."""


def format_price(cents: int) -> str:
    """Convierte céntimos (entero) a un precio en euros legible.

    Recuerda que guardamos el dinero en céntimos para evitar errores de redondeo.
    Aquí lo pasamos a euros solo para MOSTRARLO. Un precio de 0 lo enseñamos como
    "Gratis", que es lo que el usuario espera leer.

    Ejemplos: 0 -> "Gratis", 1500 -> "15,00 €", 2599 -> "25,99 €".
    """
    if not cents:
        return "Gratis"
    euros = cents / 100
    # En español el separador decimal es la coma, no el punto.
    return f"{euros:.2f}".replace(".", ",") + " €"
