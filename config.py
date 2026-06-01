"""Configuración de Patio Lab por entornos.

Idea central: la MISMA aplicación se comporta distinto según dónde corra
(tu portátil, los tests, o un servidor real). En vez de esparcir "if entorno ==
..." por el código, definimos una clase de configuración por entorno y la
aplicación elige una al arrancar (ver app/__init__.py).

Todo lo sensible (claves, URL de la base de datos) se lee de variables de
entorno, nunca se escribe aquí. Así el código se puede subir a un repositorio
público sin filtrar secretos.
"""

import os
from pathlib import Path

from sqlalchemy.pool import StaticPool

# Carpeta raíz del proyecto (donde está este archivo). La usamos para construir
# rutas absolutas y que SQLite no dependa de desde dónde lances el comando.
BASE_DIR = Path(__file__).resolve().parent


class BaseConfig:
    """Ajustes comunes a todos los entornos. Las demás clases heredan de esta."""

    # Marca: el nombre vive aquí, no incrustado en las plantillas. Cambiarlo
    # en el futuro es tocar una sola línea.
    BRAND_NAME = "Patio Lab"

    # Clave para firmar sesiones y tokens CSRF. Se lee del entorno; si no existe,
    # un valor de relleno SOLO válido para desarrollo (en producción lo exigimos
    # en init_app, ver más abajo).
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-inseguro-cambia-esto")

    # SQLAlchemy emite un aviso si no desactivamos este seguimiento, que además
    # consume memoria sin que lo usemos. Lo apagamos en todos los entornos.
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app(app) -> None:
        """Gancho que la factory llama tras cargar la config.

        Aquí no hace nada; existe para que los entornos que necesiten validar o
        ajustar algo (como Production) puedan sobrescribirlo. Es el patrón
        recomendado por la documentación de Flask.
        """


class DevelopmentConfig(BaseConfig):
    """Tu máquina mientras desarrollas."""

    DEBUG = True
    # Base de datos SQLite en un archivo local. Es un único fichero .db, sin
    # servidor que instalar: ideal para desarrollar. La ruta es absoluta para
    # que funcione lances el comando desde donde lo lances.
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{BASE_DIR / 'patiolab-dev.db'}"


class TestingConfig(BaseConfig):
    """Configuración para ejecutar los tests (pytest)."""

    TESTING = True
    # Base de datos en MEMORIA: se crea al empezar el test y desaparece al
    # terminar. Rápida y nunca ensucia tu base de datos de desarrollo.
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

    # OJO con SQLite en memoria: por defecto cada conexión abre una base de datos
    # NUEVA y vacía. Con varias peticiones (como en los tests) eso significa que
    # los datos "desaparecen" entre una y otra. StaticPool fuerza a usar UNA sola
    # conexión compartida, así la BD en memoria persiste durante todo el test.
    # check_same_thread=False permite usar esa conexión desde el hilo del test.
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {"check_same_thread": False},
        "poolclass": StaticPool,
    }

    # Desactivamos CSRF en tests para poder enviar formularios sin el token.
    WTF_CSRF_ENABLED = False


def _normalize_db_url(url: str) -> str:
    """Corrige un detalle típico de los proveedores de hosting.

    Algunos dan la URL con el prefijo "postgres://", pero SQLAlchemy exige
    "postgresql://". Lo arreglamos en un solo sitio para que el cambio
    SQLite -> Postgres no requiera tocar el resto del código.
    """
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


class ProductionConfig(BaseConfig):
    """Servidor real. Aquí somos estrictos con la seguridad."""

    DEBUG = False

    # La URL de la base de datos viene del entorno (será PostgreSQL). Leerla aquí
    # con .get() no rompe nada al importar; la validación dura está en init_app.
    SQLALCHEMY_DATABASE_URI = _normalize_db_url(os.environ.get("DATABASE_URL", ""))

    @staticmethod
    def init_app(app) -> None:
        """Validaciones que SOLO deben fallar al arrancar de verdad en producción.

        Las hacemos aquí, no en el cuerpo de la clase, porque el cuerpo se ejecuta
        al IMPORTAR config.py (siempre, incluso en desarrollo). Si exigiéramos los
        secretos ahí, no podrías ni arrancar en local. En cambio, init_app solo se
        ejecuta cuando la factory elige de verdad la config de producción.
        """
        if app.config["SECRET_KEY"] == "dev-inseguro-cambia-esto":
            raise RuntimeError(
                "Falta SECRET_KEY: define una clave segura en el entorno antes "
                "de arrancar en producción."
            )
        if not app.config["SQLALCHEMY_DATABASE_URI"]:
            raise RuntimeError(
                "Falta DATABASE_URL: define la URL de la base de datos de "
                "producción en el entorno."
            )


# Diccionario que traduce el nombre del entorno (texto de la variable
# FLASK_CONFIG) a la clase correspondiente. La factory lo usa para elegir.
config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
