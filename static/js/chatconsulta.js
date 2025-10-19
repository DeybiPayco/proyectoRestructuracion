document.addEventListener("DOMContentLoaded", () => {
  const mensajes = document.getElementById("chat-mensajes");
  const cerrarBtn = document.getElementById("cerrar-chat");

  const respuestas = {
    horario: "Atendemos de lunes a sábado, de 9:00 a.m. a 7:00 p.m. 🕒",
    ubicacion: "Estamos San vicente cañete 📍",
    caro: "Nuestro pastel más exclusivo es el 'Encanto de Frambuesa Real' 🎂, cuesta S/ 120.",
    recomendacion: "Para cumpleaños, recomendamos el 'Sueño de Vainilla con fresas' 🍓🎉",
    entregas: "Sí, hacemos entregas en todo San vicente, Imperial 🚚",
    promociones: "¡Sí! Si juegas el juego de memoria, puedes ganar un 10% de descuento 🎮✨",
    personalizados: "Claro que sí, puedes personalizar tu pastel desde la sección 'Haz tu pedido' 🎂🖌️"
  };

  document.querySelectorAll(".opcion-chat").forEach(btn => {
    btn.addEventListener("click", () => {
      const clave = btn.dataset.pregunta;
      const preguntaVisible = btn.textContent.trim();
      mostrarMensaje("usuario", preguntaVisible);
      mostrarEscribiendo();

      setTimeout(() => {
        eliminarEscribiendo();
        mostrarMensaje("bot", respuestas[clave] || "Lo siento, no entendí esa consulta 😔");
      }, 1000);
    });
  });

  cerrarBtn.addEventListener("click", () => {
    mensajes.innerHTML = "";
  });

  function mostrarMensaje(tipo, texto) {
    const burbuja = document.createElement("div");
    burbuja.className = tipo === "usuario"
      ? "bg-pink-300 text-purple-900 px-4 py-2 rounded-xl text-left text-sm font-medium w-fit self-end shadow-md"
      : "bg-purple-200 border border-pink-300 text-purple-900 px-4 py-2 rounded-xl text-left text-sm font-medium w-fit self-start shadow-md";
    burbuja.textContent = texto;
    mensajes.appendChild(burbuja);
    mensajes.scrollTop = mensajes.scrollHeight;
  }

  function mostrarEscribiendo() {
    const escribiendo = document.createElement("div");
    escribiendo.id = "escribiendo";
    escribiendo.className = "text-sm text-purple-500 italic";
    escribiendo.textContent = "Escribiendo...";
    mensajes.appendChild(escribiendo);
    mensajes.scrollTop = mensajes.scrollHeight;
  }

  function eliminarEscribiendo() {
    const burbuja = document.getElementById("escribiendo");
    if (burbuja) burbuja.remove();
  }
});
