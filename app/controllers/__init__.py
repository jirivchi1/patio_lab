# Este archivo (vacío) convierte la carpeta "controllers" en un paquete de Python.
#
# Aquí viven los CONTROLADORES (la "C" de Modelo-Vista-Controlador): las funciones
# que reciben una petición del navegador, coordinan el trabajo (piden datos a un
# servicio o modelo) y eligen qué plantilla (la "V", la vista) devolver.
#
# Un archivo por área de la web: public_controller.py, auth_controller.py, etc.
# Cada uno usa por dentro un "Blueprint" de Flask, que no es más que la herramienta
# con la que Flask agrupa rutas relacionadas en un módulo. El nombre de la carpeta
# (controllers) te dice el ROL; el Blueprint es solo el detalle técnico de Flask.
