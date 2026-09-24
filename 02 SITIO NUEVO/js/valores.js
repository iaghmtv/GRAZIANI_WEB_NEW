document.addEventListener('DOMContentLoaded', function() {
    const valoresGrid = document.querySelector('.valores-grid');
    const dots = document.querySelectorAll('.carousel-dot');
    const columns = document.querySelectorAll('.valores-column');

    if (!valoresGrid || !dots.length || !columns.length) return;

    // Observar cambios en el scroll del grid
    valoresGrid.addEventListener('scroll', function() {
        const scrollPosition = valoresGrid.scrollLeft;
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
            valoresGrid.scrollTo({
                left: columnWidth * index,
                behavior: 'smooth'
            });
        });
    });
}); 