"""Formularios de autenticación (Flask-WTF).

Un formulario WTForms es una clase donde cada atributo es un CAMPO con sus
VALIDADORES. Ventajas frente a leer request.form a mano en el controlador:
  - Validación declarativa: "este campo es obligatorio y debe ser un email".
  - Protección CSRF automática (el token oculto que añade form.hidden_tag()).
  - Errores listos para mostrar al lado de cada campo.
"""

from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

from app.services.auth_service import get_user_by_email


def strip_whitespace(value: str | None) -> str | None:
    """Filtro: recorta espacios alrededor antes de validar.

    Los 'filters' de WTForms transforman el dato ANTES de que corran los
    validadores. Así "  ana@mail.com " (copiada con espacios) se valida ya
    limpia y no la rechaza el validador Email().
    """
    return value.strip() if isinstance(value, str) else value


class RegistrationForm(FlaskForm):
    """Formulario de registro de una cuenta nueva."""

    name = StringField(
        "Nombre", validators=[DataRequired(), Length(min=2, max=120)], filters=[strip_whitespace]
    )
    email = StringField(
        "Email",
        validators=[DataRequired(), Email(), Length(max=255)],
        filters=[strip_whitespace],
    )
    password = PasswordField(
        "Contraseña",
        validators=[DataRequired(), Length(min=8, max=128)],
    )
    # EqualTo compara este campo con "password": deben coincidir.
    confirm = PasswordField(
        "Repite la contraseña",
        validators=[
            DataRequired(),
            EqualTo("password", message="Las contraseñas no coinciden."),
        ],
    )
    submit = SubmitField("Crear cuenta")

    def validate_email(self, field) -> None:
        """Validador personalizado: rechaza emails ya registrados.

        WTForms llama automáticamente a cualquier método llamado validate_<campo>.
        Si lanzamos ValidationError, el error aparece junto al campo email.
        """
        if get_user_by_email(field.data):
            raise ValidationError("Ya existe una cuenta con este email.")


class LoginForm(FlaskForm):
    """Formulario de inicio de sesión."""

    email = StringField("Email", validators=[DataRequired(), Email()], filters=[strip_whitespace])
    password = PasswordField("Contraseña", validators=[DataRequired()])
    # "Recuérdame": mantiene la sesión iniciada aunque cierres el navegador.
    remember = BooleanField("Mantener la sesión iniciada")
    submit = SubmitField("Entrar")
