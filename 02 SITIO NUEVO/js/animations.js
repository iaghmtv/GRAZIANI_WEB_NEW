document.addEventListener('DOMContentLoaded', function() {
    // Configuración del Intersection Observer para animaciones
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                // Una vez que el elemento es visible, dejamos de observarlo
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observar todos los elementos con la clase fade-in
    document.querySelectorAll('.fade-in').forEach(element => {
        observer.observe(element);
    });
}); 