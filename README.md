# Web Graziani / Hidra Embotelladora

Rediseño del sitio [hidraembotelladora.com](https://hidraembotelladora.com) (marca Graziani, San Juan).
Sitio estático (HTML, CSS y JS sin framework), pensado para subir tal cual por FTP a `public_html`.

## Carpetas

| Carpeta | Qué hay |
| --- | --- |
| `02 SITIO NUEVO/` | El sitio en desarrollo. `index.html` es la página completa con el hero animado nuevo integrado y todas las secciones (productos nuevos incluidos); `hero.html` es el prototipo aislado del hero; `pagina-anterior.html` es la home con el hero viejo, solo como referencia; `origen.html` y `sustentabilidad.html` son las páginas interiores actuales. |
| `03 BLENDER GIRO BOTELLA/` | Escena de Blender (script + `.blend`) que renderiza la botella girando y convirtiéndose en Eco Agua. Los frames exportados viven en `02 SITIO NUEVO/assets/hero/giro/`. |
| `04 COMFYUI CORDILLERA/` | Workflow de ComfyUI (Wan 2.2 I2V) que genera el clip de la cámara bajando por la cordillera. Frames en `02 SITIO NUEVO/assets/hero/cordillera/`. |
| `00 HERRAMIENTAS/` | Scripts de inventario y respaldo por FTP (leen las credenciales de un archivo local que no está en el repo). |
| `LEEME - sitio Graziani.txt` | Bitácora completa: hallazgos del sitio original, decisiones, pendientes. |

No están en el repo (solo en local): el respaldo del servidor, los insumos de 6000 px, los renders PNG, las salidas de ComfyUI y el archivo con las claves del hosting.

## Ver el sitio

- Publicado con GitHub Pages desde la carpeta `02 SITIO NUEVO` (workflow en `.github/workflows/pages.yml`): la raíz es la página completa; `/hero.html` es el prototipo del hero.
- En local: cualquier servidor estático sobre `02 SITIO NUEVO`, por ejemplo `python -m http.server 8765` y abrir `http://localhost:8765/hero.html`.

## Hero animado

Sección pineada con GSAP ScrollTrigger y snap a tres encuadres: la botella gira y se convierte en Eco Agua, después la cámara baja por la cordillera y la botella se va con el paisaje. Las dos animaciones son secuencias de frames WebP dibujadas en `<canvas>`; la cantidad de frames se configura al inicio de `02 SITIO NUEVO/js/hero.js`.
