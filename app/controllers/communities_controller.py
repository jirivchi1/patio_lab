"""Controlador de comunidades y feed.

Mezcla dos tipos de rutas:
  - Rutas que devuelven HTML (listar, ver, unirse, publicar) -> render/redirect.
  - Rutas que devuelven JSON (like, comentar) -> las llama el JavaScript con fetch
    para actualizar la página sin recargarla.

Como siempre, el controlador es fino: valida, delega en los servicios y responde.
"""

from flask import (
    Blueprint,
    abort,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required

from app.forms.community_forms import PostForm
from app.services import community_service, feed_service

communities_bp = Blueprint("communities", __name__)


# --- Rutas HTML -------------------------------------------------------------

@communities_bp.route("/comunidades")
def list_communities():
    """Listado público de todas las comunidades."""
    communities = community_service.list_communities()
    return render_template("communities/list.html", communities=communities)


@communities_bp.route("/comunidades/<slug>")
def detail(slug: str):
    """Ficha de una comunidad: descripción, miembros y feed."""
    community = community_service.get_community_by_slug(slug)
    if community is None:
        abort(404)  # comunidad inexistente -> página 404

    posts = feed_service.list_posts(community)

    # ¿El visitante actual es miembro? Solo los miembros ven el formulario de
    # publicar y los controles de like/comentar.
    member = current_user.is_authenticated and community_service.is_member(
        current_user.id, community.id
    )
    # Qué posts ha likeado ya, para pintar esos botones "encendidos".
    liked_ids = (
        feed_service.liked_post_ids(current_user.id, posts)
        if current_user.is_authenticated
        else set()
    )

    return render_template(
        "communities/detail.html",
        community=community,
        posts=posts,
        is_member=member,
        liked_post_ids=liked_ids,
        form=PostForm(),
    )


@communities_bp.route("/comunidades/<slug>/unirse", methods=["POST"])
@login_required
def join(slug: str):
    """Une al usuario actual a la comunidad."""
    community = community_service.get_community_by_slug(slug)
    if community is None:
        abort(404)
    community_service.join_community(current_user, community)
    flash(f"Te has unido a {community.name}.", "success")
    return redirect(url_for("communities.detail", slug=slug))


@communities_bp.route("/comunidades/<slug>/publicar", methods=["POST"])
@login_required
def create_post(slug: str):
    """Crea una publicación. Solo miembros."""
    community = community_service.get_community_by_slug(slug)
    if community is None:
        abort(404)
    if not community_service.is_member(current_user.id, community.id):
        abort(403)  # no eres miembro -> prohibido

    form = PostForm()
    if form.validate_on_submit():
        feed_service.create_post(community, current_user, form.body.data)
        flash("Publicación creada.", "success")
    else:
        flash("La publicación no puede estar vacía.", "error")
    return redirect(url_for("communities.detail", slug=slug))


# --- Endpoints JSON (los llama el JavaScript) -------------------------------

@communities_bp.route("/posts/<int:post_id>/like", methods=["POST"])
@login_required
def toggle_like(post_id: int):
    """Da/quita like. Devuelve JSON con el nuevo estado y total."""
    post = feed_service.get_post(post_id)
    if post is None:
        return jsonify(error="La publicación no existe."), 404
    if not community_service.is_member(current_user.id, post.community_id):
        return jsonify(error="No eres miembro de esta comunidad."), 403

    liked, count = feed_service.toggle_like(post, current_user)
    return jsonify(liked=liked, count=count)


@communities_bp.route("/posts/<int:post_id>/comentarios", methods=["POST"])
@login_required
def add_comment(post_id: int):
    """Añade un comentario. Recibe JSON {body: ...} y devuelve el comentario creado."""
    post = feed_service.get_post(post_id)
    if post is None:
        return jsonify(error="La publicación no existe."), 404
    if not community_service.is_member(current_user.id, post.community_id):
        return jsonify(error="No eres miembro de esta comunidad."), 403

    # request.get_json(silent=True) devuelve None si el cuerpo no es JSON válido,
    # en vez de lanzar un error. Así controlamos nosotros la respuesta.
    data = request.get_json(silent=True) or {}
    body = (data.get("body") or "").strip()
    if not body:
        return jsonify(error="El comentario está vacío."), 400

    comment = feed_service.add_comment(post, current_user, body)
    # 201 = "Created", el código HTTP correcto cuando se crea un recurso nuevo.
    return jsonify(id=comment.id, author=current_user.name, body=comment.body), 201
