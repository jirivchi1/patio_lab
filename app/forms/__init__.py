# Paquete FORMS — definición y validación de formularios (Flask-WTF).
#
# Cada formulario es una clase que declara sus campos y sus reglas de validación
# (ej. "el email es obligatorio y debe tener formato de email"). El controlador
# crea el formulario, comprueba si es válido y, si lo es, llama a un servicio.
#
# Mantener la validación aquí evita ensuciar los controladores con comprobaciones
# y nos da gratis la protección CSRF. Se empieza a llenar en la Fase (c), auth.
