# Paquete SERVICES — la lógica de negocio de verdad (la "capa de servicios").
#
# No es una de las tres letras de MVC, sino la madurez que se le añade en apps
# profesionales: la lógica gorda (control de aforo, marcar un pago, repartir
# puntos) no va ni en el controlador ni en el modelo, va aquí.
#
# Flujo: CONTROLADOR -> SERVICIO -> MODELO. El controlador solo coordina; el
# servicio decide. Ventaja: los tests prueban servicios directamente, sin pasar
# por HTTP ni el navegador. Se empieza a llenar en la Fase (d)/(e).
