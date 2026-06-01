"""Tests de comunidades y feed: unirse, publicar, likes y comentarios."""

from app.extensions import db
from app.models import Post
from app.services import community_service, feed_service


def test_list_communities_page(client, make_community):
    make_community(name="Permacultura", slug="permacultura")
    response = client.get("/comunidades")
    assert response.status_code == 200
    assert "Permacultura" in response.get_data(as_text=True)


def test_join_community(client, make_user, make_community, login):
    user = make_user()
    community = make_community()
    login()
    client.post(f"/comunidades/{community.slug}/unirse", follow_redirects=True)
    assert community_service.is_member(user.id, community.id) is True


def test_non_member_cannot_post(client, make_user, make_community, login):
    make_user()
    community = make_community()
    login()
    # Sin unirse, intentar publicar debe ser rechazado (403) y no crear nada.
    response = client.post(f"/comunidades/{community.slug}/publicar", data={"body": "hola"})
    assert response.status_code == 403
    assert db.session.scalar(db.select(db.func.count()).select_from(Post)) == 0


def test_member_can_post(client, make_user, make_community, login):
    user = make_user()
    community = make_community()
    community_service.join_community(user, community)
    login()
    client.post(
        f"/comunidades/{community.slug}/publicar",
        data={"body": "Mi primer post"},
        follow_redirects=True,
    )
    posts = feed_service.list_posts(community)
    assert len(posts) == 1
    assert posts[0].body == "Mi primer post"


def test_like_toggle_json(client, make_user, make_community, login):
    user = make_user()
    community = make_community()
    community_service.join_community(user, community)
    post = feed_service.create_post(community, user, "hola")
    login()

    # Primer clic: like (liked=True, count=1).
    response = client.post(f"/posts/{post.id}/like")
    assert response.get_json() == {"liked": True, "count": 1}

    # Segundo clic: se quita (toggle).
    response = client.post(f"/posts/{post.id}/like")
    assert response.get_json() == {"liked": False, "count": 0}


def test_comment_json(client, make_user, make_community, login):
    user = make_user()
    community = make_community()
    community_service.join_community(user, community)
    post = feed_service.create_post(community, user, "hola")
    login()

    response = client.post(f"/posts/{post.id}/comentarios", json={"body": "¡Buen post!"})
    assert response.status_code == 201
    data = response.get_json()
    assert data["author"] == "Ana"
    assert data["body"] == "¡Buen post!"


def test_empty_comment_rejected(client, make_user, make_community, login):
    user = make_user()
    community = make_community()
    community_service.join_community(user, community)
    post = feed_service.create_post(community, user, "hola")
    login()
    response = client.post(f"/posts/{post.id}/comentarios", json={"body": "   "})
    assert response.status_code == 400


def test_like_requires_membership(client, make_user, make_community, login):
    # El autor crea el post; otro usuario que NO es miembro intenta dar like.
    author = make_user(name="Autor", email="autor@mail.com")
    community = make_community()
    community_service.join_community(author, community)
    post = feed_service.create_post(community, author, "hola")

    make_user(name="Intruso", email="intruso@mail.com")
    login(email="intruso@mail.com")
    response = client.post(f"/posts/{post.id}/like")
    assert response.status_code == 403
