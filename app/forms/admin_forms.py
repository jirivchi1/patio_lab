"""Formularios del panel de administración: crear/editar comunidades y eventos."""

from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DecimalField,
    IntegerField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.fields import DateTimeLocalField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

from app.forms.auth_forms import strip_whitespace
from app.models.enums import EventStatus

# Etiquetas en español para los estados del evento (el SelectField mostrará esto,
# pero guardará el valor interno: "draft", "published"...).
STATUS_LABELS = {
    EventStatus.draft: "Borrador",
    EventStatus.published: "Publicado",
    EventStatus.cancelled: "Cancelado",
    EventStatus.completed: "Celebrado",
}


class CommunityForm(FlaskForm):
    """Crear o editar una comunidad."""

    name = StringField(
        "Nombre", validators=[DataRequired(), Length(max=120)], filters=[strip_whitespace]
    )
    description = TextAreaField("Descripción", validators=[Optional(), Length(max=5000)])
    cover_image = StringField(
        "URL de imagen de portada", validators=[Optional(), Length(max=255)]
    )
    is_paid = BooleanField("Es de pago")
    # El precio se introduce en EUROS (más cómodo), pero lo guardaremos en
    # céntimos. La conversión la hace el controlador.
    price = DecimalField(
        "Precio (€)", validators=[Optional(), NumberRange(min=0)], places=2, default=0
    )
    submit = SubmitField("Guardar")


class EventForm(FlaskForm):
    """Crear o editar un evento.

    Las opciones de `community`, `speaker` y `status` (las listas desplegables)
    se rellenan en el controlador, porque dependen de los datos actuales de la BD.
    """

    # coerce=int convierte el valor enviado (texto) a entero, para casarlo con los
    # ids de la base de datos.
    community = SelectField("Comunidad", coerce=int, validators=[DataRequired()])
    speaker = SelectField("Ponente", coerce=int, validators=[Optional()])

    title = StringField(
        "Título", validators=[DataRequired(), Length(max=200)], filters=[strip_whitespace]
    )
    description = TextAreaField("Descripción", validators=[Optional(), Length(max=5000)])

    # DateTimeLocalField pinta un selector de fecha+hora del navegador. El format
    # debe coincidir con lo que envía ese control (ISO sin segundos).
    starts_at = DateTimeLocalField(
        "Fecha y hora", format="%Y-%m-%dT%H:%M", validators=[DataRequired()]
    )
    ends_at = DateTimeLocalField(
        "Fin (opcional)", format="%Y-%m-%dT%H:%M", validators=[Optional()]
    )

    capacity = IntegerField("Aforo (plazas)", validators=[DataRequired(), NumberRange(min=1)])
    price = DecimalField(
        "Precio (€)", validators=[Optional(), NumberRange(min=0)], places=2, default=0
    )

    includes_bbq = BooleanField("Incluye barbacoa")
    lodging_available = BooleanField("Pernocta disponible")

    location = StringField(
        "Ubicación",
        validators=[DataRequired(), Length(max=255)],
        default="Finca en Daimés, Elche (Alicante)",
    )
    status = SelectField("Estado", validators=[DataRequired()])
    submit = SubmitField("Guardar")
