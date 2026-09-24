/* ==========================================================================
   GRAZIANI — Hero animado por scroll (GSAP ScrollTrigger) — v2: secuencias de frames

   Coreografía (sección pineada, scrub + snap a 3 encuadres):
     progreso 0.0 → encuadre 1: botella Clara 500, "El espíritu de Los Andes"
     progreso 0.5 → encuadre 2: la botella giró y es Eco Agua, copy nuevo
     progreso 1.0 → encuadre 3: la cámara "bajó la toma", la botella se fue con el paisaje
   Un scroll corto salta al siguiente encuadre (snap direccional), estilo Apple.

   Assets animados (se scrubean por scroll en <canvas>):
     GIRO      assets/hero/giro/giro_###.webp      render Blender de la botella girando y convirtiéndose
     CORDILLERA assets/hero/cordillera/cord_###.webp clip ComfyUI de la cámara bajando por la cordillera
   Si una secuencia tiene frames = 0 se usa el fallback CSS (flip 3D / paneo de la foto fija).

   Reduced motion / sin GSAP: .is-static y el hero muestra el estado final (Eco Agua).
   ========================================================================== */
(() => {
  const HERO = {
    scrollLength: "+=250%",   // alto de scroll pineado (2.5 viewports: 1.25 por fase)
    giro: {
      frames: 120,            // render Blender giro_botella_v001 (0 = usar flip CSS). Se numeran desde 000.
      path: (i) => `assets/hero/giro/giro_${String(i).padStart(3, "0")}.webp`,
    },
    cordillera: {
      frames: 81,             // clip ComfyUI Wan 2.2 (0 = paneo CSS sobre la foto fija)
      path: (i) => `assets/hero/cordillera/cord_${String(i).padStart(3, "0")}.webp`,
    },
  };

  const hero = document.querySelector(".hero");
  if (!hero) return;
  const $ = (s) => hero.querySelector(s);
  const bg = $(".hero__bg");
  const bgSeq = $(".hero__bgseq");
  const stage = $(".hero__stage");
  const stageSeq = $(".hero__seq");
  const flip = $(".flip");
  const faces = hero.querySelectorAll(".flip__face"); // el blur va en las caras: un filter en .flip aplanaría el 3D
  const copyA = $(".hero__copy--a");
  const copyB = $(".hero__copy--b");
  const hint = $(".hero__hint");

  const useGiro = HERO.giro.frames > 0 && !!stageSeq;
  const useCord = HERO.cordillera.frames > 0 && !!bgSeq;
  hero.classList.toggle("has-giro", useGiro);
  hero.classList.toggle("has-cord", useCord);

  /* ---------- Secuencia de frames dibujada en un canvas (contain o cover) ---------- */
  function createSequence(cfg, canvas, fit, onFirst) {
    const n = cfg.frames;
    const imgs = new Array(n);
    const ctx = canvas.getContext("2d");
    let current = 0;
    let lastDrawn = -1;
    let firstDone = false;

    const ok = (img) => img && img.complete && img.naturalWidth > 0;
    const nearestLoaded = (i) => {
      for (let d = 0; d < n; d++) {
        if (ok(imgs[i - d])) return i - d;
        if (ok(imgs[i + d])) return i + d;
      }
      return -1;
    };
    function paint(force) {
      const i = nearestLoaded(current);
      if (i < 0 || (i === lastDrawn && !force)) return;
      const img = imgs[i];
      const cw = canvas.width, ch = canvas.height;
      const s = fit === "cover"
        ? Math.max(cw / img.naturalWidth, ch / img.naturalHeight)
        : Math.min(cw / img.naturalWidth, ch / img.naturalHeight);
      const w = img.naturalWidth * s, h = img.naturalHeight * s;
      ctx.clearRect(0, 0, cw, ch);
      // cover: anclado arriba (igual que object-position 50% 0 de la foto fija); contain: centrado
      ctx.drawImage(img, (cw - w) / 2, fit === "cover" ? 0 : (ch - h) / 2, w, h);
      lastDrawn = i;
    }
    function resize() {
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      const w = Math.max(1, Math.round(canvas.clientWidth * dpr));
      const h = Math.max(1, Math.round(canvas.clientHeight * dpr));
      if (canvas.width !== w || canvas.height !== h) {
        canvas.width = w; canvas.height = h;
        paint(true);
      }
    }
    function load(i) {
      if (imgs[i]) return imgs[i];
      const img = new Image();
      img.decoding = "async";
      img.addEventListener("load", () => {
        if (!firstDone) { firstDone = true; onFirst && onFirst(img); resize(); }
        if (nearestLoaded(current) === i) paint(true);
      }, { once: true });
      img.src = cfg.path(i);
      imgs[i] = img;
      return img;
    }
    function loadAll() {
      let next = 0;
      const lane = () => {
        while (next < n) {
          const img = load(next++);
          if (!ok(img)) {
            img.addEventListener("load", lane, { once: true });
            img.addEventListener("error", lane, { once: true });
            return;
          }
        }
      };
      for (let k = 0; k < 6; k++) lane();   // 6 descargas en paralelo, en orden
    }
    function seek(t) {
      current = Math.max(0, Math.min(n - 1, Math.round(t * (n - 1))));
      if (!imgs[current]) load(current);
      paint(false);
    }
    window.addEventListener("resize", resize);
    // si la caja del canvas cambia (aspect-ratio del escenario, pestaña que pasa a visible), se redimensiona
    if (window.ResizeObserver) new ResizeObserver(resize).observe(canvas);
    resize();
    return { seek, load, loadAll, resize, n };
  }

  const giroSeq = useGiro
    ? createSequence(HERO.giro, stageSeq, "contain", (img) => {
        // el encuadre de la botella lo define el render: ajusta la caja del escenario a su proporción
        stage.style.aspectRatio = `${img.naturalWidth} / ${img.naturalHeight}`;
        if (window.ScrollTrigger) ScrollTrigger.refresh();
      })
    : null;
  const cordSeq = useCord ? createSequence(HERO.cordillera, bgSeq, "cover") : null;

  /* ---------- Estado estático (reduced motion o sin GSAP): resultado final ---------- */
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reduce || !window.gsap || !window.ScrollTrigger) {
    hero.classList.add("is-static");
    if (giroSeq) giroSeq.seek(1);
    return;
  }

  gsap.registerPlugin(ScrollTrigger);
  ScrollTrigger.config({ ignoreMobileResize: true }); // la barra del celular no dispara refresh (evita saltos del pin)

  // primer frame ya, el resto en orden
  if (giroSeq) { giroSeq.seek(0); giroSeq.loadAll(); }
  if (cordSeq) { cordSeq.seek(0); cordSeq.loadAll(); }

  const params = new URLSearchParams(location.search);
  const debug = params.has("debug");
  // Ganchos de depuración: ?frame=0.5 fija ese progreso del hero (capturas); ?nosnap desactiva el snap
  const frameParam = params.has("frame") ? parseFloat(params.get("frame")) : null;
  const noSnap = params.has("nosnap") || frameParam !== null;

  const proxy = { giro: 0, cord: 0 };

  const tl = gsap.timeline({
    defaults: { ease: "none" },
    scrollTrigger: {
      trigger: hero,
      start: "top top",
      end: HERO.scrollLength,
      pin: true,
      anticipatePin: 1,
      scrub: 0.6,
      markers: debug,
      snap: noSnap ? undefined : {
        snapTo: [0, 0.5, 1],          // los tres encuadres
        duration: { min: 0.35, max: 0.9 },
        delay: 0.05,
        ease: "power2.inOut",
        directional: true,            // un toque de rueda avanza al encuadre siguiente
      },
    },
  });

  /* ---------- Fase A (t = 0 → 1): la botella gira y se convierte ---------- */
  tl.to(hint, { autoAlpha: 0, duration: 0.15 }, 0)
    // salida más sutil que la entrada: poco desplazamiento, blur corto
    .to(copyA, { autoAlpha: 0, y: -18, filter: "blur(4px)", duration: 0.35, ease: "power1.in" }, 0);

  if (useGiro) {
    // secuencia renderizada (Blender): lineal, pegada al scroll
    tl.to(proxy, { giro: 1, duration: 1, onUpdate: () => giroSeq.seek(proxy.giro) }, 0);
  } else {
    // fallback: flip 3D de las dos fotos; el dorso es la botella Eco (backface-visibility)
    tl.to(flip, { rotateY: 180, duration: 1, ease: "power1.inOut" }, 0)
      // blur puente en el instante del canto (tapa la costura del intercambio)
      .to(faces, { filter: "blur(4px)", duration: 0.5, ease: "power1.in" }, 0)
      .to(faces, { filter: "blur(0px)", duration: 0.5, ease: "power1.out" }, 0.5);
  }

  // entrada: opacidad + translateY + blur (receta de entrada)
  tl.fromTo(
    copyB,
    { autoAlpha: 0, y: 18, filter: "blur(4px)" },
    { autoAlpha: 1, y: 0, filter: "blur(0px)", duration: 0.4, ease: "power2.out" },
    0.6
  );

  /* ---------- Fase B (t = 1 → 2): baja la toma, la botella se va con el paisaje ---------- */
  // el contenedor del fondo (foto fija + canvas del clip) baja la toma en lineal, pegado al scroll.
  // Con el clip de ComfyUI (que ya baja la cámara) el paneo es más corto: suma paralaje sin duplicar el movimiento.
  tl.to(bg, { yPercent: useCord ? -12 : -23, scale: useCord ? 1.04 : 1.08, duration: 1 }, 1);
  if (useCord) {
    // el clip de ComfyUI se scrubea a la vez: suma el movimiento propio del paisaje al paneo
    tl.to(proxy, { cord: 1, duration: 1, onUpdate: () => cordSeq.seek(proxy.cord) }, 1);
  }
  tl.to(stage, { yPercent: -150, duration: 1 }, 1)               // la botella, más cerca, se mueve más rápido
    .to(copyB, { autoAlpha: 0, y: -40, duration: 0.5, ease: "power1.in" }, 1);

  if (frameParam !== null) {
    // Solo para capturas: desengancha el scroll y fija el progreso de la timeline (0..1).
    const jump = () => {
      tl.scrollTrigger.kill();
      tl.progress(Math.min(Math.max(frameParam, 0), 1));
      if (frameParam > 1) window.scrollTo(0, (frameParam - 1) * window.innerHeight);
    };
    if (document.readyState === "complete") jump(); else window.addEventListener("load", jump);
  }

  window.addEventListener("load", () => ScrollTrigger.refresh());
})();
