"""Comandos personalizados de la CLI de Flask.

Se ejecutan con `flask <nombre>`. De momento solo `seed-demo`, que rellena la
base de datos con datos de ejemplo para poder ver y probar la app sin tener que
crear todo a mano. Es IDEMPOTENTE: si los datos ya existen, no los duplica, así
que puedes ejecutarlo las veces que quieras sin miedo.
"""

from datetime import UTC, datetime, timedelta

import click
from flask import Flask

from app.extensions import db
from app.models import Community, Event, Like, Membership, Post, User
from app.models.enums import EventStatus, UserRole


def register_commands(app: Flask) -> None:
    """Engancha los comandos a la app. Se llama desde la factory."""

    @app.cli.command("seed-demo")
    def seed_demo() -> None:
        """Crea datos de ejemplo (un usuario demo, comunidades y un post)."""

        # 1) Usuario demo (para que puedas entrar sin registrarte).
        demo_email = "ana@patiolab.es"
        user = db.session.scalar(db.select(User).filter_by(email=demo_email))
        if user is None:
            user = User(name="Ana López", email=demo_email)
            user.set_password("demo1234")
            db.session.add(user)
            db.session.flush()  # flush para tener user.id disponible ya
            click.echo(f"Usuario demo creado: {demo_email} / demo1234")
        else:
            click.echo("Usuario demo ya existía (no se duplica).")

        # 2) Comunidades de ejemplo (name, slug, descripción).
        seed_communities = [
            ("Permacultura", "permacultura",
             "Diseño regenerativo, huertos y vida en el campo."),
            ("Impresión 3D", "impresion-3d",
             "Modelado, impresoras y proyectos para fabricar en casa."),
            ("Drones y FPV", "drones-fpv",
             "Vuelo en primera persona, montaje y carreras de drones."),
        ]
        communities: list[Community] = []
        for name, slug, description in seed_communities:
            community = db.session.scalar(db.select(Community).filter_by(slug=slug))
            if community is None:
                community = Community(name=name, slug=slug, description=description)
                db.session.add(community)
                db.session.flush()
                click.echo(f"Comunidad creada: {name}")
            communities.append(community)

        # 3) Hacemos a Ana miembro de la primera comunidad y le dejamos un post
        #    con un like, para que el feed no aparezca vacío.
        permacultura = communities[0]
        already_member = db.session.scalar(
            db.select(Membership).filter_by(user_id=user.id, community_id=permacultura.id)
        )
        if already_member is None:
            db.session.add(Membership(user_id=user.id, community_id=permacultura.id))

        has_posts = db.session.scalar(
            db.select(Post).filter_by(community_id=permacultura.id)
        )
        if has_posts is None:
            post = Post(
                community_id=permacultura.id,
                author_id=user.id,
                body="¡Bienvenidos a la comunidad! ¿Qué estáis cultivando esta temporada?",
            )
            db.session.add(post)
            db.session.flush()
            db.session.add(Like(post_id=post.id, user_id=user.id))
            click.echo("Publicación de ejemplo creada.")

        # 4) Un ponente (rol speaker) y un par de eventos publicados.
        speaker_email = "marta@patiolab.es"
        speaker = db.session.scalar(db.select(User).filter_by(email=speaker_email))
        if speaker is None:
            speaker = User(name="Marta Ríos", email=speaker_email, role=UserRole.speaker)
            speaker.set_password("demo1234")
            db.session.add(speaker)
            db.session.flush()
            click.echo(f"Ponente demo creado: {speaker_email}")

        impresion3d = communities[1]
        # (comunidad, título, slug, descripción, días_desde_hoy, aforo, precio_cents, bbq, pernocta)
        seed_events = [
            (permacultura, "Taller de compostaje y huerto de temporada", "taller-compostaje",
             "Monta un compostero y planifica el huerto. Termina en barbacoa.",
             14, 20, 1500, True, False),
            (impresion3d, "Monta tu primera impresora 3D", "monta-impresora-3d",
             "De las piezas al primer print. La cena la ponemos nosotros.",
             30, 12, 2500, True, True),
        ]
        for community, title, slug, description, days, capacity, price, bbq, lodging in seed_events:
            event = db.session.scalar(db.select(Event).filter_by(slug=slug))
            if event is None:
                event = Event(
                    community_id=community.id,
                    speaker_id=speaker.id,
                    title=title,
                    slug=slug,
                    description=description,
                    starts_at=datetime.now(UTC) + timedelta(days=days),
                    capacity=capacity,
                    price_cents=price,
                    includes_bbq=bbq,
                    lodging_available=lodging,
                    status=EventStatus.published,
                )
                db.session.add(event)
                click.echo(f"Evento creado: {title}")

        db.session.commit()
        click.echo("Datos de ejemplo listos.")
