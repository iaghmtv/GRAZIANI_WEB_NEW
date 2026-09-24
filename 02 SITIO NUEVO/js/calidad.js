document.addEventListener('DOMContentLoaded', function() {
    const calidadGrid = document.querySelector('.calidad-grid');
    const dots = document.querySelectorAll('.carro-punto');
    const columns = document.querySelectorAll('.calidad-column');

    if (!calidadGrid || !dots.length || !columns.length) return;

    // Observar cambios en el scroll del grid
    calidadGrid.addEventListener('scroll', function() {
        const scrollPosition = calidadGrid.scrollLeft;
        const columnWidth = columns[0].offsetWidth;
        const currentIndex = Math.round(scrollPosition / columnWidth);

        // Actualizar los dots
        dots.forEach((dot, index) => {
            dot.classList.toggle('active', index === currentIndex);
        });
    });

    // Hacer que los dots sean clickeables
    dots.forEach((dot, index) => {
        dot.addEventListener('click', function() {
            const columnWidth = columns[0].offsetWidth;
            calidadGrid.scrollTo({
                left: columnWidth * index,
                behavior: 'smooth'
            });
        });
    });
}); 