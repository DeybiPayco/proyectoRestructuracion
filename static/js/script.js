// Contenido de static/js/script.js

document.addEventListener('DOMContentLoaded', () => {

    // LÓGICA DEL CARRUSEL DE IMÁGENES (Inicio de la Página)
    // ----------------------------------------------------
    const carouselItems = document.querySelectorAll('.carousel-item');
    let currentCarouselIndex = 0;

    /**
     * Muestra la imagen en el índice especificado, usando las clases de opacidad de Tailwind
     * para la animación de transición (fade).
     */
    function showCarouselItem(index) {
        // Validación básica
        if (carouselItems.length === 0) return;

        // Oculta todos los elementos
        carouselItems.forEach(item => {
            // Se usa requestAnimationFrame para asegurar que el navegador actualiza el DOM
            // antes de aplicar la siguiente opacidad.
            requestAnimationFrame(() => {
                item.classList.add('opacity-0');
                item.classList.remove('opacity-100');
            });
        });

        // Muestra el elemento actual (activando la transición de Tailwind)
        requestAnimationFrame(() => {
            if (carouselItems[index]) {
                carouselItems[index].classList.remove('opacity-0');
                carouselItems[index].classList.add('opacity-100');
            }
        });
    }

    /**
     * Pasa a la siguiente imagen.
     */
    function nextCarouselItem() {
        currentCarouselIndex = (currentCarouselIndex + 1) % carouselItems.length;
        showCarouselItem(currentCarouselIndex);
    }

    // Inicializa: Muestra la primera imagen y establece la rotación
    if (carouselItems.length > 0) {
        showCarouselItem(currentCarouselIndex); 
        // Cambia cada 5 segundos (5000 ms).
        setInterval(nextCarouselItem, 5000); 
    }
    // ----------------------------------------------------


    // CÓDIGO EXISTENTE: Lógica del Formulario
    // ----------------------------------------------------------------
    
    // Elementos del DOM para el formulario y animaciones
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
    
    // Lógica para enviar el formulario (AJAX con Fetch)
    // Se asume que FORM_URL se define globalmente en el HTML si es necesario.
    if (formulario && typeof FORM_URL !== 'undefined') {
        formulario.addEventListener('submit', function(event) {
            event.preventDefault();

            const formData = new FormData(formulario);

            fetch(FORM_URL, {
                method: 'POST',
                body: formData
            })
            .then(response => response.json()) 
            .then(data => {
                if (data.status === 'success') {
                    formulario.classList.add('hidden');
                    mensajeRespuesta.textContent = data.message;
                    mensajeRespuesta.classList.remove('hidden');
                    mensajeRespuesta.classList.add('animate-on-scroll', 'is-visible');
                    mensajeRespuesta.scrollIntoView({ behavior: 'smooth', block: 'center' });
                } else {
                    alert('Error: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error de red al intentar contactar con el servidor:', error);
                alert('No se pudo conectar con el servidor. Inténtalo de nuevo más tarde.');
            });
        });
    }

    // Lógica de animación de scroll (EXISTENTE)
    // ----------------------------------------------------------------
    const animatedElements = document.querySelectorAll('.animate-on-scroll');
    
    // Hace que el contenido del carrusel se anime inmediatamente (is-visible)
    const heroContent = document.querySelector('#hero-carousel .animate-on-scroll');
    if (heroContent) {
        heroContent.classList.add('is-visible');
    }
    
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