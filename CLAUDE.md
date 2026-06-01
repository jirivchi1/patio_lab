# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Patio Lab: a self-hosted "simplified Skool" — an online community platform (groups,
feed/forum, likes, comments) fused with **in-person paid events** held at a rural venue
near Elche, Spain. The defining feature vs. Skool is the physical layer: events have real
capacity limits, a speaker, BBQ/lodging flags, and registrations with payment state.

The codebase is built **in phases**, pausing after each for the owner's review. Track the
roadmap in `README.md`. Current state: Phase (a) done — app boots and serves a landing.

## Working conventions (important)

- **Audience:** the owner is strong in Python/backend/data, weak in frontend. Explain the
  *why* of decisions. When touching HTML/CSS/JS, teach it block by block. Backend can move
  faster. Respond in **Spanish**; code identifiers in **English**, UI text in **Spanish**.
- **Few dependencies, all understood.** No frontend frameworks, no Tailwind/Bootstrap, no
  build step, no npm. Plain hand-written CSS (with custom properties for the palette) and
  vanilla JS (`fetch`) only where interactivity is needed. Comment CSS/JS generously.
- **Phased delivery:** do not jump ahead. After each phase, explain what was built and why,
  and give exact verification commands. Keep `README.md` and the phase checklist current.
- Environment is **Windows + PowerShell**.

## Commands

Run from the project root with the virtualenv active (`.\.venv\Scripts\Activate.ps1`).
The `flask` CLI auto-loads `.flaskenv` (sets `FLASK_APP=wsgi.py`, debug on).

```powershell
pip install -r requirements.txt   # install deps
flask run                         # dev server at http://127.0.0.1:5000
ruff check .                      # lint
ruff format .                     # format
pytest                            # run all tests (Phase g onward)
pytest tests/test_x.py::test_name # run a single test
```

DB migrations (Flask-Migrate / Alembic), from Phase (b) onward:

```powershell
flask db init      # once, creates migrations/
flask db migrate -m "message"   # autogenerate a migration from model changes
flask db upgrade   # apply migrations to the DB
```

Quick boot check without a browser: `GET /health` returns `ok`.

## Architecture: MVC + service layer

The app uses the **application factory** pattern with a strict layering that maps to MVC:

- **Model** — `app/models/` — SQLAlchemy classes (one file per aggregate; import them all in
  `app/models/__init__.py` so Alembic sees them).
- **Controller** — `app/controllers/` — one `*_controller.py` per area. Each defines a Flask
  `Blueprint` internally and registers its routes. **Keep controllers thin**: validate the
  form, call a service, pick a template. No business logic here.
  - Note: Flask calls these "view functions"; in MVC terms they are *controllers*. The MVC
    "view" is the Jinja template. A Blueprint is just Flask's tool for grouping controllers.
- **View** — `app/templates/` — Jinja2. `base.html` is the parent template; pages `extends`
  it and fill `{% block %}`s. Brand name comes from `config.BRAND_NAME`, never hardcoded.
- **Service** — `app/services/` — the real business logic (capacity control, payments,
  points). Flow is `Controller → Service → Model`. Services are tested directly, no HTTP.
- **Forms** — `app/forms/` — Flask-WTF classes (validation + CSRF).

### Wiring

- `app/__init__.py` `create_app(config_name)` is the only place that assembles the app:
  load config → `config_class.init_app(app)` → init extensions → register controllers.
- `app/extensions.py` holds extension singletons created **without** an app (`db`, `migrate`,
  `csrf`, `login_manager`), attached later via `init_app`. This avoids circular imports:
  models import `db` from here; this file imports nothing downstream.
- New controllers must be registered in `create_app` step 5 with `app.register_blueprint(...)`.
- `login_manager` is intentionally **not** initialized until Phase (c): without a `user_loader`
  (which needs the `User` model) Flask-Login crashes when rendering any template.

### Config (`config.py`)

`Development | Testing | Production` classes selected by `FLASK_CONFIG` env var. Secrets come
from the environment only. Production-only validation (required `SECRET_KEY`, `DATABASE_URL`)
lives in `ProductionConfig.init_app`, **not** in the class body — class bodies run on import in
every environment, so putting checks there would break local dev. DB URLs are normalized
`postgres://` → `postgresql://` so the SQLite→Postgres switch is env-only.

## Domain conventions

- **Money is stored as integer cents** (`price_cents`), never floats. Format to "12,00 €" in
  the template.
- **Enums** for roles and states (User.role, Membership.role_in_community, Event.status,
  Registration.status/payment_status) — not free text.
- **Event capacity is computed**, not a stored column: count `confirmed` registrations vs
  `capacity` inside a transaction in the registration service. A stored counter desyncs.
- Uniqueness constraints: `(user_id, community_id)`, `(post_id, user_id)` for likes,
  `(user_id, event_id)` for registrations.
- **Payments** sit behind a `PaymentProvider` interface with a `FakePaymentProvider` (marks
  paid without charging). No real keys. Stripe/PayPal later by swapping that piece only.
- `User.points` exists for Phase-2 gamification; the field is prepared, logic not implemented.
