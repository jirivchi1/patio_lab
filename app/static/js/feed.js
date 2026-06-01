/* ===========================================================================
   feed.js — interactividad del feed SIN recargar la página.

   Dos cosas:
     1) Dar/quitar like a una publicación.
     2) Enviar un comentario y verlo aparecer al instante.

   Ambas usan fetch(), la función del navegador para hablar con el servidor en
   segundo plano. El servidor responde JSON, y nosotros actualizamos el HTML a
   mano. Es JavaScript "vanilla" (sin librerías): cada paso está a la vista.
   =========================================================================== */

// --- Utilidad: leer el token CSRF -------------------------------------------
// El servidor protege TODAS las peticiones POST contra CSRF. Para que acepte las
// nuestras, debemos enviarle el token que dejó en el <meta> de base.html.
function getCsrfToken() {
  const meta = document.querySelector('meta[name="csrf-token"]');
  return meta ? meta.getAttribute("content") : "";
}

// document es la página. "DOMContentLoaded" se dispara cuando el HTML ya está
// cargado y podemos buscar elementos con seguridad. Todo el código va dentro.
document.addEventListener("DOMContentLoaded", function () {
  configurarLikes();
  configurarComentarios();
});

// --- 1) LIKES ---------------------------------------------------------------
function configurarLikes() {
  // querySelectorAll devuelve TODOS los botones de like de la página.
  const botones = document.querySelectorAll(".like-btn");

  botones.forEach(function (boton) {
    // A cada botón le decimos: "cuando te hagan click, ejecuta esta función".
    boton.addEventListener("click", async function () {
      // dataset.postId lee el atributo data-post-id="..." del HTML.
      const postId = boton.dataset.postId;

      try {
        // Enviamos la petición. await espera la respuesta sin congelar la página.
        const respuesta = await fetch("/posts/" + postId + "/like", {
          method: "POST",
          headers: { "X-CSRFToken": getCsrfToken() },
        });
        if (!respuesta.ok) {
          return; // si el servidor responde error (403, 404...), no hacemos nada
        }

        // El servidor devuelve { liked: true/false, count: N }.
        const datos = await respuesta.json();

        // Actualizamos el número de likes que se ve en el botón...
        boton.querySelector(".like-count").textContent = datos.count;
        // ...y encendemos/apagamos el botón según el nuevo estado. El segundo
        // argumento de toggle fuerza añadir (true) o quitar (false) la clase.
        boton.classList.toggle("liked", datos.liked);
      } catch (error) {
        console.error("Error al dar like:", error);
      }
    });
  });
}

// --- 2) COMENTARIOS ---------------------------------------------------------
function configurarComentarios() {
  const formularios = document.querySelectorAll(".comment-form");

  formularios.forEach(function (formulario) {
    formulario.addEventListener("submit", async function (evento) {
      // Por defecto, enviar un formulario recarga la página. preventDefault lo
      // impide: queremos manejarlo nosotros con fetch.
      evento.preventDefault();

      const postId = formulario.dataset.postId;
      const textarea = formulario.querySelector("textarea");
      const texto = textarea.value.trim();
      if (texto === "") {
        return; // no enviamos comentarios vacíos
      }

      try {
        const respuesta = await fetch("/posts/" + postId + "/comentarios", {
          method: "POST",
          headers: {
            "Content-Type": "application/json", // avisamos: enviamos JSON
            "X-CSRFToken": getCsrfToken(),
          },
          body: JSON.stringify({ body: texto }), // convertimos a texto JSON
        });
        if (!respuesta.ok) {
          return;
        }

        // El servidor devuelve { id, author, body } del comentario creado.
        const datos = await respuesta.json();

        // Construimos el nuevo <li> y lo añadimos a la lista de este post.
        // closest(".post-card") sube hasta la tarjeta que contiene este formulario.
        const lista = formulario.closest(".post-card").querySelector(".comment-list");
        const item = document.createElement("li");
        item.className = "comment";

        const autor = document.createElement("strong");
        autor.textContent = datos.author;
        item.appendChild(autor);
        // Añadimos un espacio y el texto. Usamos createTextNode (no innerHTML)
        // para que, si el comentario trae < o >, se muestren como texto y no se
        // interpreten como HTML (eso evita inyecciones de código).
        item.appendChild(document.createTextNode(" " + datos.body));

        lista.appendChild(item);
        textarea.value = ""; // limpiamos el campo para el siguiente comentario
      } catch (error) {
        console.error("Error al comentar:", error);
      }
    });
  });
}
