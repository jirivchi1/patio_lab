"""Controlador de autenticación: registro, login y logout.

Recuerda: el controlador es FINO. Aquí solo validamos el formulario, llamamos al
servicio y decidimos a dónde redirigir o qué plantilla mostrar. Cero lógica de
negocio (esa está en auth_service.py).
"""

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.forms.auth_forms import LoginForm, RegistrationForm
from app.services.auth_service import get_user_by_email, register_user

auth_bp = Blueprint("auth", __name__)


def _safe_redirect_target(target: str | None) -> str | None:
    """Evita "open redirects": solo permitimos rutas internas (que empiezan por /).

    Tras el login, Flask-Login pasa un parámetro ?next=... con la página a la que
    el usuario quería ir. Si lo redirigiéramos a ciegas, un atacante podría poner
    ?next=http://sitio-malo.com. Aceptamos solo rutas relativas del propio sitio.
    """
    if target and target.startswith("/") and not target.startswith("//"):
        return target
    return None


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    # Si ya estás logueado, no tiene sentido registrarse: a la landing.
    if current_user.is_authenticated:
        return redirect(url_for("public.landing"))

    form = RegistrationForm()
    # validate_on_submit() es True solo si (a) la petición es POST y (b) todos los
    # validadores pasan. En GET o si hay errores, devuelve False y caemos al render.
    if form.validate_on_submit():
        user = register_user(form.name.data, form.email.data, form.password.data)
        login_user(user)  # inicia sesión automáticamente tras registrarse
        flash(f"¡Bienvenido a Patio Lab, {user.name}!", "success")
        return redirect(url_for("public.landing"))

    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("public.landing"))

    form = LoginForm()
    if form.validate_on_submit():
        user = get_user_by_email(form.email.data)
        # Mismo mensaje genérico si el email no existe o la contraseña falla: así
        # no revelamos a un atacante qué emails están registrados.
        if user is None or not user.check_password(form.password.data):
            flash("Email o contraseña incorrectos.", "error")
            return render_template("auth/login.html", form=form)

        login_user(user, remember=form.remember.data)
        flash(f"Hola de nuevo, {user.name}.", "success")
        next_page = _safe_redirect_target(request.args.get("next"))
        return redirect(next_page or url_for("public.landing"))

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required  # solo puede cerrar sesión quien la tiene iniciada
def logout():
    logout_user()
    flash("Has cerrado sesión.", "success")
    return redirect(url_for("public.landing"))
