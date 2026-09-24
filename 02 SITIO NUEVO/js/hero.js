/* ==========================================================================
   GRAZIANI — Hero animado por scroll (GSAP ScrollTrigger) — v3

   Coreografía:
     CARGA      la botella entra con un pequeño giro (últimos frames al revés) y el título aparece.
     SCROLL 1   sección pineada, scrub + snap: la botella gira 360° y se convierte en Eco Agua
                (frames de Blender), el copy cambia. FASE A.
     SCROLL 2   el hero se va hacia arriba mientras la cámara baja por la cordillera (clip ComfyUI
                + paneo) y la botella se adelanta con paralaje; el snap aterriza de lleno en la
                pantalla siguiente. FASE B.
   El logo del nav cambia de blanco a azul según el fondo que tenga debajo (data-nav en las secciones).

   Assets animados (secuencias de frames dibujadas en <canvas>):
     GIRO       assets/hero/giro/giro_###.webp        render Blender (03 BLENDER GIRO BOTELLA)
     CORDILLERA assets/hero/cordillera/cord_###.webp  clip ComfyUI (04 COMFYUI CORDILLERA)
   Con frames = 0 se usa el fallback CSS (flip 3D / paneo de la foto fija).
   Reduced motion / sin GSAP: .is-static, el hero muestra el estado final.
   ========================================================================== */
(() => {
  const HERO = {
    pinLength: "+=120%",     // scroll pineado de la fase A (giro)
    giro: {
      frames: 120,           // render Blender (0 = flip CSS). Numerados desde 000.
      path: (i) => `assets/hero/giro/giro_${String(i).padStart(3, "0")}.webp`,
      introFrames: 30,       // cuántos frames "desanda" la botella al entrar (el giro arranca suave: 30 frames son ~23°)
    },
    cordillera: {
      frames: 81,            // clip ComfyUI (0 = solo paneo CSS sobre la foto fija)
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
  const nav = document.querySelector(".nav");

  const useGiro = HERO.giro.frames > 0 && !!stageSeq;
  const useCord = HERO.cordillera.frames > 0 && !!bgSeq;
  hero.classList.toggle("has-giro", useGiro);
  hero.classList.toggle("has-cord", useCord);

  /* ---------- Nav: blanco sobre fondos oscuros, azul sobre claros (según lo que pasa bajo el logo) ---------- */
  const setNavTheme = (t) => nav && nav.classList.toggle("nav--light", t === "light");
  const themed = document.querySelectorAll("[data-nav]");
  if (nav && themed.length && "IntersectionObserver" in window) {
    // observa una franja de 1 px a la altura del logo (48 px del borde superior)
    const io = new IntersectionObserver((entries) => {
      entries.forEach((e) => { if (e.isIntersecting) setNavTheme(e.target.dataset.nav); });
    }, { rootMargin: "-48px 0px -98% 0px", threshold: 0 });
    themed.forEach((el) => io.observe(el));
  }

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
    if (window.ResizeObserver) new ResizeObserver(resize).observe(canvas);
    resize();
    return { seek, load, loadAll, resize, n };
  }

  const giroSeq = useGiro
    ? createSequence(HERO.giro, stageSeq, "contain", (img) => {
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
  ScrollTrigger.config({ ignoreMobileResize: true });

  if (giroSeq) { giroSeq.seek(0); giroSeq.loadAll(); }
  if (cordSeq) { cordSeq.seek(0); cordSeq.loadAll(); }

  const params = new URLSearchParams(location.search);
  const debug = params.has("debug");
  // Ganchos de depuración: ?frame=0.25 (fase A a mitad), 0.5 (fin de A), 0.75 (fase B a mitad), 1 (pantalla siguiente)
  const frameParam = params.has("frame") ? parseFloat(params.get("frame")) : null;
  const noSnap = params.has("nosnap") || frameParam !== null;
  const snapCfg = (min, max) => noSnap ? undefined : {
    snapTo: [0, 1], duration: { min, max }, delay: 0.05, ease: "power2.inOut", directional: true,
  };

  const proxy = { giro: 0, cord: 0 };
  let intro = null;
  const killIntro = () => { if (intro) { intro.kill(); intro = null; } };

  /* ---------- FASE A (pineada): la botella gira y se convierte ---------- */
  const tlA = gsap.timeline({
    defaults: { ease: "none" },
    scrollTrigger: {
      id: "heroA",
      trigger: hero,
      start: "top top",
      end: HERO.pinLength,
      pin: true,
      anticipatePin: 1,
      scrub: 0.6,
      markers: debug,
      snap: snapCfg(0.4, 1.0),
    },
  });
  tlA.to(hint, { autoAlpha: 0, duration: 0.15 }, 0)
     .to(copyA, { autoAlpha: 0, y: -18, filter: "blur(4px)", duration: 0.35, ease: "power1.in" }, 0);
  if (useGiro) {
    tlA.to(proxy, { giro: 1, duration: 1, onUpdate: () => { if (proxy.giro > 0.002) killIntro(); giroSeq.seek(proxy.giro); } }, 0);
  } else {
    tlA.to(flip, { rotateY: 180, duration: 1, ease: "power1.inOut", onUpdate: killIntro }, 0)
       .to(faces, { filter: "blur(4px)", duration: 0.5, ease: "power1.in" }, 0)
       .to(faces, { filter: "blur(0px)", duration: 0.5, ease: "power1.out" }, 0.5);
  }
  tlA.fromTo(copyB,
    { autoAlpha: 0, y: 18, filter: "blur(4px)" },
    { autoAlpha: 1, y: 0, filter: "blur(0px)", duration: 0.4, ease: "power2.out" }, 0.6);

  /* ---------- FASE B (el hero se va): baja la toma y aterriza en la pantalla siguiente ---------- */
  const stA = tlA.scrollTrigger;
  const tlB = gsap.timeline({
    defaults: { ease: "none" },
    scrollTrigger: {
      id: "heroB",
      trigger: hero,
      start: () => stA.end,                          // justo cuando termina el pin
      end: () => stA.end + window.innerHeight,       // hasta que el hero salió entero
      scrub: 0.6,
      markers: debug,
      snap: snapCfg(0.35, 0.8),
    },
  });
  tlB.to(bg, { yPercent: useCord ? -12 : -23, scale: useCord ? 1.04 : 1.08, duration: 1 }, 0);
  if (useCord) tlB.to(proxy, { cord: 1, duration: 1, onUpdate: () => cordSeq.seek(proxy.cord) }, 0);
  tlB.to(stage, { yPercent: -110, duration: 1 }, 0)              // la botella, más cerca, se adelanta al paisaje
     .to(copyB, { autoAlpha: 0, y: -40, duration: 0.5, ease: "power1.in" }, 0);

  /* ---------- Llegada al cargar: la botella entra con un pequeño giro ---------- */
  if (frameParam === null) {
    const st0 = { f: HERO.giro.introFrames };
    intro = gsap.timeline({ defaults: { ease: "power3.out" } });
    if (useGiro) {
      intro.to(st0, { f: 0, duration: 1.5, ease: "power2.out", onUpdate: () => giroSeq.seek(st0.f / (giroSeq.n - 1)) }, 0);
    } else {
      intro.fromTo(flip, { rotateY: -28 }, { rotateY: 0, duration: 1.5, ease: "power2.out" }, 0);
    }
    intro.fromTo(stage, { autoAlpha: 0, y: 48 }, { autoAlpha: 1, y: 0, duration: 1.1 }, 0)
         .fromTo(copyA, { autoAlpha: 0, y: 22, filter: "blur(6px)" }, { autoAlpha: 1, y: 0, filter: "blur(0px)", duration: 0.9 }, 0.25)
         .fromTo(hint, { autoAlpha: 0 }, { autoAlpha: 0.7, duration: 0.6 }, 0.9);
  }

  if (frameParam !== null) {
    // Solo para capturas: desengancha el scroll y fija el estado (0..0.5 fase A, 0.5..1 fase B)
    const jump = () => {
      stA.kill(); tlB.scrollTrigger.kill();
      const f = Math.min(Math.max(frameParam, 0), 1);
      tlA.progress(Math.min(f * 2, 1));
      if (f > 0.5) {
        const b = (f - 0.5) * 2;
        tlB.progress(b);
        // simula el scroll del hero saliendo (mueve las secciones, no el html, para que el nav fijo no se desplace)
        gsap.set([hero, ...document.querySelectorAll(".section")], { y: -b * window.innerHeight });
      }
    };
    if (document.readyState === "complete") jump(); else window.addEventListener("load", jump);
  }

  if (params.has("snaptest")) {
    // Prueba automática del snap (navegador headless, donde no corre requestAnimationFrame):
    // se empuja el reloj de GSAP y el ScrollTrigger a mano; tres scrolls cortos, el resultado va al <title>
    gsap.ticker.lagSmoothing(0);
    setInterval(() => { ScrollTrigger.update(); gsap.ticker.tick(); }, 16);
    const pasos = [120, 100, -90];
    const res = [];
    let i = 0;
    const paso = () => {
      if (i >= pasos.length) { document.title = "SNAPTEST " + res.join(" | "); return; }
      window.scrollBy(0, pasos[i]);
      setTimeout(() => {
        res.push(`d${pasos[i]}>y${Math.round(window.scrollY)} A${stA.progress.toFixed(2)} B${tlB.scrollTrigger.progress.toFixed(2)} ${nav ? nav.className : ""}`);
        i++; paso();
      }, 2600);
    };
    window.addEventListener("load", () => setTimeout(paso, 1800));
  }

  window.addEventListener("load", () => ScrollTrigger.refresh());
})();
