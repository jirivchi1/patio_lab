"""Extensiones de Flask, creadas SIN aplicación todavía.

Patrón importante: las extensiones (base de datos, login, etc.) se crean aquí
como objetos "vacíos", sin conocer aún a la aplicación. Luego, dentro de la
factory (app/__init__.py), se "enchufan" a la app con `extension.init_app(app)`.

¿Por qué separarlo así? Porque permite:
  1. Crear varias apps con la misma config (p. ej. una para tests) sin choques.
  2. Evitar los temidos "imports circulares": los modelos importan `db` desde
     aquí, y este archivo no importa a los modelos. Flecha en un solo sentido.
"""

from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

# ORM: el objeto `db` será nuestra puerta a la base de datos. Los modelos
# (fase b) heredarán de db.Model.
db = SQLAlchemy()

# Migraciones: genera y aplica los cambios de esquema usando Alembic.
migrate = Migrate()

# Gestor de sesiones de usuario. Lo configuramos del todo en la fase de auth.
login_manager = LoginManager()
# A dónde redirigir si alguien intenta entrar a una página protegida sin login.
login_manager.login_view = "auth.login"
# Mensaje flash que se muestra en ese caso (en español, tono cercano).
login_manager.login_message = "Inicia sesión para acceder a esta página."

# Protección CSRF: añade un token oculto a los formularios para evitar que una
# web maliciosa envíe peticiones en tu nombre.
csrf = CSRFProtect()
