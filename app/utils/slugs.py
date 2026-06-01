"""Generación de slugs: convertir un texto en una versión apta para URLs.

Ejemplo: "Economía Regenerativa" -> "economia-regenerativa".

Lo hacemos a mano (sin dependencias extra) para cumplir el "pocas dependencias":
  1. Quitamos los acentos (í -> i) descomponiendo los caracteres Unicode.
  2. Pasamos a minúsculas.
  3. Sustituimos cualquier cosa que no sea letra/número por guiones.
"""

import re
import unicodedata


def slugify(text: str) -> str:
    """Devuelve el slug de un texto."""
    # NFKD separa cada letra acentuada en (letra base + acento). Al codificar a
    # ASCII e ignorar lo que no cabe, el acento desaparece y queda la letra base.
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii").lower().strip()
    # Cualquier grupo de caracteres no alfanuméricos -> un solo guion.
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text)
    # Quitamos guiones sobrantes al principio y al final.
    return slug.strip("-")
