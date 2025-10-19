document.addEventListener("DOMContentLoaded", () => {
  const mensajes = document.getElementById("chat-mensajes");
  const cerrarBtn = document.getElementById("cerrar-chat");

  const respuestas = {
    "🕒 ¿Cuál es el horario de atención?": "Atendemos de lunes a sábado, de 9:00 a.m. a 7:00 p.m. 🕒",
    "📍 ¿Dónde se ubican?": "Estamos en Av. Principal 123, Ventanilla, Callao 📍",
    "💸 ¿Cuál es el pastel más caro?": "Nuestro pastel más exclusivo es el 'Encanto de Frambuesa Real' 🎂, cuesta S/ 120.",
    "🎂 ¿Qué pastel recomiendan?": "Para cumpleaños, recomendamos el 'Sueño de Vainilla con fresas' 🍓🎉",
    "🚚 ¿Hacen entregas?": "Sí, hacemos entregas en todo Callao y Lima Norte 🚚"
  };

  document.querySelectorAll(".opcion-chat").forEach(btn => {
    btn.addEventListener("click", () => {
      const pregunta = btn.textContent.trim();
      mostrarMensaje("usuario", pregunta);
      setTimeout(() => {
        mostrarMensaje("bot", respuestas[pregunta] || "Lo siento, no entendí esa consulta 😔");
      }, 500);
    });
  });

  cerrarBtn.addEventListener("click", () => {
    document.getElementById("chatbot-container").style.display = "none";
  });

  function mostrarMensaje(tipo, texto) {
    const burbuja = document.createElement("div");
    burbuja.className = tipo === "usuario"
      ? "bg-pink-200 text-pink-900 px-4 py-2 rounded-xl text-left text-sm font-medium w-fit self-end"
      : "bg-white border border-pink-300 text-pink-800 px-4 py-2 rounded-xl text-left text-sm font-medium w-fit self-start shadow";
    burbuja.textContent = texto;
    mensajes.appendChild(burbuja);
    mensajes.scrollTop = mensajes.scrollHeight;
  }
});
