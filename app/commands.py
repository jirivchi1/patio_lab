"""Comandos personalizados de la CLI de Flask.

Se ejecutan con `flask <nombre>`. De momento solo `seed-demo`, que rellena la
base de datos con datos de ejemplo para poder ver y probar la app sin tener que
crear todo a mano. Es IDEMPOTENTE: si los datos ya existen, no los duplica, así
que puedes ejecutarlo las veces que quieras sin miedo.
"""

import click
from flask import Flask

from app.extensions import db
from app.models import Community, Like, Membership, Post, User


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

        db.session.commit()
        click.echo("Datos de ejemplo listos.")
