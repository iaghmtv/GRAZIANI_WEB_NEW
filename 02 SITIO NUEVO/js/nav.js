/* ==========================================================================
   GRAZIANI — menú móvil (hamburguesa + cajón lateral). No depende de GSAP.
   Abre y cierra con el botón; cierra al tocar un link, el fondo oscuro o Escape,
   y al pasar a escritorio. Mientras está abierto bloquea el scroll de la página.
   ========================================================================== */
(() => {
  const nav = document.querySelector(".nav");
  const btn = nav && nav.querySelector(".nav__burger");
  const panel = nav && nav.querySelector(".nav__links");
  const scrim = nav && nav.querySelector(".nav__scrim");
  if (!nav || !btn || !panel) return;

  const movil = window.matchMedia("(max-width: 768px)");
  const abierto = () => nav.classList.contains("is-open");

  function abrir(si) {
    nav.classList.toggle("is-open", si);
    btn.setAttribute("aria-expanded", String(si));
    btn.setAttribute("aria-label", si ? "Cerrar menú" : "Abrir menú");
    document.documentElement.classList.toggle("menu-abierto", si);
    if (si) {
      const primero = panel.querySelector("a");
      if (primero) primero.focus({ preventScroll: true });
    }
  }

  btn.addEventListener("click", () => abrir(!abierto()));
  if (scrim) scrim.addEventListener("click", () => abrir(false));
  panel.addEventListener("click", (e) => { if (e.target.closest("a")) abrir(false); });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && abierto()) { abrir(false); btn.focus(); }
  });
  const alCambiar = (e) => { if (!e.matches && abierto()) abrir(false); };
  if (movil.addEventListener) movil.addEventListener("change", alCambiar);
  else if (movil.addListener) movil.addListener(alCambiar);   // Safari viejo
})();
