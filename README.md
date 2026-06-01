# Patio Lab

Plataforma de **comunidad online + eventos presenciales** en una finca cerca de
Elche (Alicante). Charlas y talleres temáticos (acuarios, impresión 3D, drones,
permacultura, fermentación…) que terminan en barbacoa, con un foro/feed estilo
Skool por debajo. Lema: **"Comunidad, no clientes"**.

Este repositorio se construye **por fases**. Estado actual: **Fase (a)** — la
aplicación arranca y se ve en el navegador.

---

## Stack

- **Backend:** Python 3.11+ y Flask (patrón *application factory* + blueprints).
- **ORM / migraciones:** Flask-SQLAlchemy + Flask-Migrate (Alembic).
- **Auth:** Flask-Login + hashing de werkzeug *(próxima fase)*.
- **Formularios:** Flask-WTF con CSRF activado.
- **Plantillas:** Jinja2 (renderizado en servidor).
- **Frontend:** HTML, CSS y JS planos. Sin frameworks, sin build, sin npm.
- **Base de datos:** SQLite en desarrollo; preparado para PostgreSQL en producción.
- **Tests / calidad:** pytest + ruff.

---

## Dependencias y para qué sirve cada una

| Paquete | Para qué sirve |
|---|---|
| Flask | Framework web: enruta peticiones y devuelve HTML. |
| Flask-SQLAlchemy | ORM: clases Python ↔ tablas SQL. |
| Flask-Migrate | Migraciones con Alembic: versiona el esquema de la BD. |
| Flask-Login | Sesiones: saber quién está logueado y proteger rutas. |
| Flask-WTF | Formularios con validación y protección CSRF. |
| email-validator | Validar que un email es válido en los formularios. |
| python-dotenv | Cargar variables de entorno desde `.env`. |
| pytest | Framework de tests. |
| ruff | Lint + formato del código. |

---

## Instalación (paso a paso)

Pensado para **Windows + PowerShell** (que es tu entorno). Desde la carpeta del
proyecto:

```powershell
# 1) Crear un entorno virtual (una carpeta .venv con un Python aislado para
#    este proyecto, para no mezclar dependencias con el resto del sistema).
python -m venv .venv

# 2) Activarlo. Verás "(.venv)" al principio de la línea cuando esté activo.
.\.venv\Scripts\Activate.ps1

# 3) Instalar las dependencias.
pip install -r requirements.txt

# 4) Crear tu archivo .env a partir de la plantilla.
Copy-Item .env.example .env
```

> Si PowerShell se queja al activar el entorno con un error de "scripts
> deshabilitados", ejecuta una vez:
> `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`
> y vuelve a intentar el paso 2.

---

## Arrancar la aplicación

```powershell
# Con el entorno virtual activado:
flask run
```

Luego abre en el navegador: **http://127.0.0.1:5000**

Deberías ver la landing de Patio Lab. Para comprobar que el servidor responde
sin abrir el navegador, también existe **http://127.0.0.1:5000/health** (devuelve
`ok`).

Para parar el servidor: `Ctrl + C` en la terminal.

### Datos de ejemplo (opcional, recomendado)

Para ver comunidades y un feed con contenido sin crearlo a mano:

```powershell
flask seed-demo
```

Crea un usuario demo, un admin, tres comunidades, un ponente y dos eventos.
Puedes entrar con:

- **Usuario normal:** `ana@patiolab.es` / `demo1234`
- **Administrador:** `admin@patiolab.es` / `admin1234` (ve el panel en `/admin`)

El comando es idempotente: ejecutarlo varias veces no duplica nada.

Para dar permisos de admin a tu propia cuenta real:

```powershell
flask make-admin tucorreo@ejemplo.com
```

---

## Arquitectura: MVC + capa de servicios

El proyecto sigue **Modelo-Vista-Controlador**, el patrón clásico para diseñar
webs, con una **capa de servicios** añadida (lo que hacen las apps profesionales):

| Capa | Carpeta | Responsabilidad |
|---|---|---|
| **Modelo** | `app/models/` | Los datos: clases SQLAlchemy ↔ tablas SQL. |
| **Controlador** | `app/controllers/` | Reciben la petición, coordinan, eligen la vista. Finos. |
| **Vista** | `app/templates/` | Lo que ve el usuario: plantillas Jinja (HTML). |
| **Servicios** | `app/services/` | La lógica de negocio de verdad (aforo, pagos, puntos). |
| Formularios | `app/forms/` | Validación de entradas con Flask-WTF. |

> Nota de vocabulario: Flask llama "view function" a lo que en MVC es el
> **controlador**. La "vista" de MVC (la presentación) en Flask es el *template*.
> Un **Blueprint** es solo la herramienta de Flask para agrupar controladores por
> área (auth, eventos…) en módulos separados.

Flujo de una petición: `Controlador → Servicio → Modelo`, y de vuelta el
controlador elige una `Vista` que genera el HTML.

## Estructura del proyecto (Fase a)

```
12_Patio_Lab/
├─ .env.example        # plantilla de variables de entorno
├─ .flaskenv           # le dice a `flask` dónde está la app
├─ requirements.txt    # dependencias
├─ pyproject.toml      # configuración de ruff
├─ config.py           # configuración por entornos (dev/test/prod)
├─ wsgi.py             # punto de entrada: crea la app con la factory
└─ app/
   ├─ __init__.py            # create_app(): la application factory
   ├─ extensions.py          # db, migrate, login_manager, csrf (sin app aún)
   ├─ models/                # MODELO  (vacío hasta la Fase b)
   ├─ controllers/           # CONTROLADOR
   │  └─ public_controller.py  # landing + endpoint /health
   ├─ services/              # lógica de negocio (vacío hasta Fase d/e)
   ├─ forms/                 # formularios Flask-WTF (vacío hasta Fase c)
   ├─ templates/             # VISTA: base.html + public/landing.html (Jinja2)
   └─ static/
      └─ css/                # variables.css (paleta) + main.css (estilos)
```

---

## Roadmap de fases

- [x] **(a)** Factory + config + extensiones + landing que arranca.
- [x] **(b)** Modelos + migración inicial.
- [x] **(c)** Auth (registro/login/logout) + plantilla base con el CSS de marca.
- [x] **(d)** Comunidades + feed (likes/comentarios con JS vanilla).
- [x] **(e)** Eventos + inscripciones con control de aforo.
- [x] **(f)** Panel de administración.
- [ ] **(g)** Tests.
