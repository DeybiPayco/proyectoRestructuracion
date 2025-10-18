document.addEventListener("DOMContentLoaded", () => {
  const tablero = document.getElementById("tablero");
  const tiempo = document.getElementById("tiempo");
  const mensajeFinal = document.getElementById("mensaje-final");
  const reiniciar = document.getElementById("reiniciar");
  const iniciar = document.getElementById("iniciar");
  const temporizador = document.getElementById("temporizador");

  const emojis = ["🍓", "🧁", "🎂", "🌸", "🍫", "🍒", "🍪", "🍭"];
  let cartas = [];
  let primera = null;
  let segunda = null;
  let aciertos = 0;
  let tiempoRestante = 30;
  let intervalo;
  let juegoActivo = false;

  function crearTablero() {
    tablero.innerHTML = "";
    mensajeFinal.classList.add("hidden");
    reiniciar.classList.add("hidden");
    temporizador.classList.remove("hidden");
    iniciar.classList.add("hidden");
    aciertos = 0;
    primera = null;
    segunda = null;
    tiempoRestante = 30;
    tiempo.textContent = tiempoRestante;
    juegoActivo = true;
    cartas = [];
    tablero.classList.remove("tablero-bloqueado");

    const pares = [...emojis, ...emojis].sort(() => Math.random() - 0.5);

    pares.forEach((emoji, index) => {
      const tarjeta = document.createElement("button");
      tarjeta.className =
        "memory-card w-[80px] h-[80px] bg-pink-100 text-3xl rounded-xl shadow-lg flex items-center justify-center font-bold transition duration-300 transform hover:scale-105 animate-fade-in";
      tarjeta.dataset.valor = emoji;
      tarjeta.dataset.index = index;
      tarjeta.textContent = "❓";
      tarjeta.addEventListener("click", () => voltear(tarjeta));
      tablero.appendChild(tarjeta);
      cartas.push(tarjeta);
    });

    intervalo = setInterval(() => {
      tiempoRestante--;
      tiempo.textContent = tiempoRestante;
      if (tiempoRestante === 0) {
        terminarJuego(false);
      }
    }, 1000);
  }

  function voltear(tarjeta) {
    if (!juegoActivo || tarjeta.textContent !== "❓" || segunda) return;

    tarjeta.textContent = tarjeta.dataset.valor;

    if (!primera) {
      primera = tarjeta;
    } else {
      segunda = tarjeta;
      if (primera.dataset.valor === segunda.dataset.valor) {
        aciertos++;
        primera = null;
        segunda = null;
        if (aciertos === 8 && tiempoRestante > 0) {
          terminarJuego(true);
        }
      } else {
        setTimeout(() => {
          primera.textContent = "❓";
          segunda.textContent = "❓";
          primera = null;
          segunda = null;
        }, 800);
      }
    }
  }

  function terminarJuego(gano) {
    clearInterval(intervalo);
    juegoActivo = false;
    tablero.classList.add("tablero-bloqueado");
    mensajeFinal.classList.remove("hidden");
    reiniciar.classList.remove("hidden");
    mensajeFinal.textContent = gano
      ? "🎉 ¡Felicidades! Has ganado un 10% de descuento encantado 💖"
      : "⏳ ¡Ups! El tiempo se acabó. Inténtalo de nuevo.";
    mensajeFinal.classList.add("is-visible");
  }

  reiniciar.addEventListener("click", () => {
    crearTablero();
  });

  iniciar.addEventListener("click", () => {
    crearTablero();
  });
});
