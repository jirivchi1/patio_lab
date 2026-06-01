"""Application factory de Patio Lab.

Una "application factory" es simplemente una FUNCIÓN que construye y devuelve la
aplicación Flask ya configurada. En vez de crear `app = Flask(...)` como variable
global, lo hacemos dentro de `create_app()`.

Ventajas (y por qué el brief lo pide):
  - Tests: cada test puede pedir una app fresca con config de testing.
  - Claridad: todo el "montaje" (config, extensiones, blueprints) ocurre en un
    único sitio, en orden y a la vista.
  - Sin estado global escondido: nada se inicializa por el mero hecho de importar.
"""

import os

from flask import Flask

from config import config_by_name

from .extensions import csrf, db, login_manager, migrate


def create_app(config_name: str | None = None) -> Flask:
    """Construye la aplicación y devuelve la instancia lista para usar.

    :param config_name: "development" | "testing" | "production". Si es None,
        se lee de la variable de entorno FLASK_CONFIG (por defecto development).
    """
    # 1) Decidir qué configuración usar.
    if config_name is None:
        config_name = os.environ.get("FLASK_CONFIG", "development")

    # 2) Crear la app Flask. instance_relative_config permite, más adelante,
    #    tener una carpeta "instance/" para datos locales si hiciera falta.
    app = Flask(__name__, instance_relative_config=True)

    # 3) Cargar la clase de configuración elegida (Development/Testing/Production)
    #    y ejecutar su hook init_app (validaciones propias de ese entorno).
    config_class = config_by_name[config_name]
    app.config.from_object(config_class)
    config_class.init_app(app)

    # 4) Enchufar las extensiones a ESTA app (el patrón init_app de extensions.py).
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    login_manager.init_app(app)

    # Importamos el paquete de modelos para que SQLAlchemy y Flask-Migrate los
    # registren. Sin esta línea, Alembic no "vería" las tablas al migrar.
    from app import models  # noqa: F401

    # user_loader: Flask-Login guarda en la sesión solo el id del usuario. Esta
    # función le enseña a recuperar el objeto User completo a partir de ese id en
    # cada petición. db.session.get() busca por clave primaria (rápido).
    @login_manager.user_loader
    def load_user(user_id: str):
        return db.session.get(models.User, int(user_id))

    # 5) Registrar los controladores (los módulos de rutas). Cada uno expone un
    #    Blueprint que aquí "montamos" en la app. Iremos sumando communities,
    #    events, admin... por fases.
    from .controllers.admin_controller import admin_bp
    from .controllers.auth_controller import auth_bp
    from .controllers.communities_controller import communities_bp
    from .controllers.events_controller import events_bp
    from .controllers.profile_controller import profile_bp
    from .controllers.public_controller import public_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(communities_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(profile_bp)
    # url_prefix hace que TODAS las rutas del admin cuelguen de /admin/...
    app.register_blueprint(admin_bp, url_prefix="/admin")

    # Filtro de plantilla "eur": en Jinja podremos escribir {{ precio_cents|eur }}
    # para mostrar "15,00 €". Registrar el filtro aquí lo deja disponible en TODAS
    # las plantillas sin importar nada en cada una.
    from .utils.formatting import format_price

    app.add_template_filter(format_price, "eur")

    # 6) Registrar los comandos personalizados de la CLI (flask seed-demo, etc.).
    from .commands import register_commands

    register_commands(app)

    return app
