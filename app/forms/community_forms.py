"""Formularios del área de comunidades."""

from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class PostForm(FlaskForm):
    """Formulario para crear una publicación en el feed.

    Los comentarios NO usan un FlaskForm: se envían por JavaScript (fetch) con el
    token CSRF en una cabecera. Las publicaciones, en cambio, se crean con un
    envío normal de formulario (recargando), así que sí aprovechan WTForms + CSRF.
    """

    body = TextAreaField("Mensaje", validators=[DataRequired(), Length(max=5000)])
    submit = SubmitField("Publicar")
