// Contenido de static/js/script.js

document.addEventListener('DOMContentLoaded', () => {

    // IMPORTANT: FORM_URL es una variable global definida en el index.html
    // Si esta variable no existe, el script fallará.
    
    // Elementos del DOM
    const btnMostrar = document.getElementById('btn-mostrar');
    const formulario = document.getElementById('formulario-oculto');
    const contenedorBoton = document.getElementById('boton-mostrar-form');
    const mensajeRespuesta = document.getElementById('mensaje-respuesta');

    // Lógica para mostrar/ocultar el formulario 
    if (btnMostrar && formulario) {
        btnMostrar.addEventListener('click', () => {
            contenedorBoton.classList.add('hidden'); 
            formulario.classList.remove('hidden'); 
            formulario.classList.add('is-visible');
            formulario.scrollIntoView({ behavior: 'smooth', block: 'start' });
        });
    }
    
    // Lógica para enviar el formulario sin recargar la página (AJAX con Fetch)
    if (formulario && typeof FORM_URL !== 'undefined') {
        formulario.addEventListener('submit', function(event) {
            event.preventDefault(); // Evita la recarga.

            const formData = new FormData(formulario);

            // Fetch utiliza la URL procesada por Flask en el HTML
            fetch(FORM_URL, {
                method: 'POST',
                body: formData
            })
            .then(response => response.json()) 
            .then(data => {
                if (data.status === 'success') {
                    // Ocultamos el formulario y mostramos el mensaje de éxito
                    formulario.classList.add('hidden');
                    mensajeRespuesta.textContent = data.message;
                    mensajeRespuesta.classList.remove('hidden');
                    mensajeRespuesta.classList.add('animate-on-scroll', 'is-visible');
                    mensajeRespuesta.scrollIntoView({ behavior: 'smooth', block: 'center' });
                } else {
                    // Muestra el mensaje de error de la DB (si el servidor devuelve status: error)
                    alert('Error: ' + data.message);
                }
            })
            .catch(error => {
                // Muestra la alerta si falla la conexión de red completamente
                console.error('Error de red al intentar contactar con el servidor:', error);
                alert('No se pudo conectar con el servidor. Inténtalo de nuevo más tarde.');
            });
        });
    }

    // Lógica de animación de scroll
    const animatedElements = document.querySelectorAll('.animate-on-scroll');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                if (!entry.target.classList.contains('hidden')) {
                     entry.target.classList.add('is-visible');
                     observer.unobserve(entry.target); 
                }
            }
        });
    }, {
        threshold: 0.1
    });
    animatedElements.forEach(element => {
        observer.observe(element);
    });
});