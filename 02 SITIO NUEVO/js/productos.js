const productos = [
  // ECO AGUA (nueva, primera categoría)
  {
    capacidad: 500,
    medida: "cc",
    imagen: "assets/botellas/ecoagua500.webp",
    popupImage: "assets/popups/ecoagua500.jpg",
    descripcion: "Eco Agua mineral natural 500cc - Sin gas, baja en sodio, botella reciclada",
    categoria: "ecoagua",
    tamano: 1,
  },
  // AGUAS
  {
    capacidad: 500,
    medida: "cc",
    imagen: "assets/botellas/agua500.png",
    popupImage: "assets/popups/agua500.png",
    descripcion: "Agua mineral natural 500cc",
    categoria: "aguas",
    tamano: 1,
  },
  {
    capacidad: 1,
    medida: "Litro",
    imagen: "assets/botellas/agua1.png",
    popupImage: "assets/popups/agua1l.png",
    descripcion: "Agua mineral natural 1 Litro",
    categoria: "aguas",
    tamano: 1.2,
  },
  {
    capacidad: 2,
    medida: "Litros",
    imagen: "assets/botellas/agua2.png",
    popupImage: "assets/popups/agua2l.png",
    descripcion: "Agua mineral natural 2 Litros",
    categoria: "aguas",
    tamano: 1.4,
  },
  {
    capacidad: 6,
    medida: "Litros",
    imagen: "assets/botellas/agua6.png",
    popupImage: "assets/popups/agua6l.png",
    descripcion: "Agua mineral natural 6 Litros",
    categoria: "aguas",
    tamano: 1.6,
  },
  // SODAS
  {
    capacidad: 500,
    medida: "cc",
    imagen: "assets/botellas/soda500.png",
    popupImage: "assets/popups/soda500.png",
    descripcion: "Soda 500cc",
    categoria: "sodas",
    tamano: 1,
  },
  {
    capacidad: 1,
    medida: "Litro",
    imagen: "assets/botellas/soda1.png",
    popupImage: "assets/popups/soda1l.png",
    descripcion: "Soda 1 Litro",
    categoria: "sodas",
    tamano: 1.2,
  },
  {
    capacidad: 2,
    medida: "Litros",
    imagen: "assets/botellas/soda2.png",
    popupImage: "assets/popups/soda2l.png",
    descripcion: "Soda 2 Litros",
    categoria: "sodas",
    tamano: 1.4,
  },
  {
    capacidad: 2.25,
    medida: "Litros",
    imagen: "assets/botellas/soda225.png",
    popupImage: "assets/popups/soda225.png",
    descripcion: "Soda 2.25 Litros",
    categoria: "sodas",
    tamano: 1.4,
  },
  // PREMIUM
  {
    capacidad: 500,
    medida: "cc",
    imagen: "assets/botellas/aguapremium.png",
    popupImage: "assets/popups/aguapremium500.png",
    descripcion: "Agua premium mineral 500cc",
    categoria: "premium",
    tamano: 1,
  },
  {
    capacidad: 500,
    medida: "cc",
    imagen: "assets/botellas/sodapremium.png",
    popupImage: "assets/popups/sodapremium500.png",
    descripcion: "Soda premium 500cc",
    categoria: "premium",
    tamano: 1,
  },
  // AMARGOS
  {
    capacidad: 1.5,
    medida: "Litros",
    imagen: "assets/botellas/amargocitrus.png",
    popupImage: "assets/popups/amargocitrus.png",
    descripcion: "Agua saborizada Citrus 500cc",
    categoria: "amargos",
    tamano: 1.2,
  },
  {
    capacidad: 1.5,
    medida: "Litros",
    imagen: "assets/botellas/amargocordillerano.png",
    popupImage: "assets/popups/amargocordillerano.png",
    descripcion: "Amargo Cordillerano 1.5 Litros",
    categoria: "amargos",
    tamano: 1.2,
  },
  {
    capacidad: 1.5,
    medida: "Litros",
    imagen: "assets/botellas/amargolimon.png",
    popupImage: "assets/popups/amargolimon.png",
    descripcion: "Amargo Limon 1.5 Litros",
    categoria: "amargos",
    tamano: 1.2,
  },
  {
    capacidad: 1.5,
    medida: "Litros",
    imagen: "assets/botellas/amargopomelo.png",
    popupImage: "assets/popups/amargopomelo.png",
    descripcion: "Amargo Pomelo 1.5 Litros",
    categoria: "amargos",
    tamano: 1.2,
  },
  {
    capacidad: 1.5,
    medida: "Litros",
    imagen: "assets/botellas/amargoserrano.png",
    popupImage: "assets/popups/amargoserrano.png",
    descripcion: "Amargo Serrano 1.5 Litros",
    categoria: "amargos",
    tamano: 1.2,
  },
  // SABORIZADAS
  {
    capacidad: 500,
    medida: "cc",
    imagen: "assets/botellas/manzana.png",
    popupImage: "assets/popups/manzana.png",
    descripcion: "Agua saborizada Manzana 500cc",
    categoria: "saborizadas",
    tamano: 1,
  },
  {
    capacidad: 500,
    medida: "cc",
    imagen: "assets/botellas/naranja.png",
    popupImage: "assets/popups/naranja.png",
    descripcion: "Agua saborizada Naranja 500cc",
    categoria: "saborizadas",
    tamano: 1,
  },
  {
    capacidad: 500,
    medida: "cc",
    imagen: "assets/botellas/pomelo.png",
    popupImage: "assets/popups/pomelo.png",
    descripcion: "Agua saborizada Pomelo 500cc",
    categoria: "saborizadas",
    tamano: 1,
  },
  {
    capacidad: 2,
    medida: "Litros",
    imagen: "assets/botellas/saborizada2l-naranja.webp",
    popupImage: "assets/popups/saborizada2l-naranja.jpg",
    descripcion: "Agua saborizada Naranja 2 Litros",
    categoria: "saborizadas",
    tamano: 1.4,
  },
  {
    capacidad: 2,
    medida: "Litros",
    imagen: "assets/botellas/saborizada2l-manzana.webp",
    popupImage: "assets/popups/saborizada2l-manzana.jpg",
    descripcion: "Agua saborizada Manzana 2 Litros",
    categoria: "saborizadas",
    tamano: 1.4,
  },
  {
    capacidad: 2,
    medida: "Litros",
    imagen: "assets/botellas/saborizada2l-pomelo.webp",
    popupImage: "assets/popups/saborizada2l-pomelo.jpg",
    descripcion: "Agua saborizada Pomelo 2 Litros",
    categoria: "saborizadas",
    tamano: 1.4,
  },
]

// productos.js
class ProductShowcase {
  constructor() {
    this.currentIndex = 0
    this.productos = productos
    this.track = document.querySelector(".product-showcase-track")
    this.container = document.querySelector(".product-showcase-container")
    this.showcase = document.querySelector(".product-showcase")
    this.setupEventListeners()
    this.setupTouchEvents()
    this.renderProductos()
    this.updateCarrusel()
    this.calcularIndicesCategorias()

    window.addEventListener("resize", () => {
      this.updateCarrusel()
    })
  }

  calcularIndicesCategorias() {
    this.categoryIndices = {}
    this.productos.forEach((producto, index) => {
      if (!(producto.categoria in this.categoryIndices)) {
        this.categoryIndices[producto.categoria] = index
      }
    })
  }

  setupEventListeners() {
    document.querySelector(".prev").addEventListener("click", () => this.prev())
    document.querySelector(".next").addEventListener("click", () => this.next())

    document.querySelectorAll(".categorias a").forEach((link) => {
      link.addEventListener("click", (e) => {
        e.preventDefault()
        const categoria = e.target.closest("a").dataset.categoria
        this.scrollToCategory(categoria)
        this.updateCategoriasActive(e.target.closest("a"))
      })
    })

    document.querySelector(".close-popup").addEventListener("click", () => {
      document.getElementById("popup").style.display = "none"
    })

    document.getElementById("popup").addEventListener("click", (e) => {
      if (e.target.id === "popup") {
        document.getElementById("popup").style.display = "none"
      }
    })

    document.addEventListener("keydown", (e) => {
      if (e.key === "ArrowLeft") this.prev()
      if (e.key === "ArrowRight") this.next()
      if (e.key === "Escape") document.getElementById("popup").style.display = "none"
    })

    this.track.addEventListener("click", (e) => {
      const producto = e.target.closest(".producto")
      if (!producto) return
      if (e.target.classList.contains("ver-mas")) return

      const productos = Array.from(this.track.querySelectorAll(".producto"))
      const index = productos.indexOf(producto)
      if (index !== -1) {
        this.currentIndex = (index - 3 + this.productos.length) % this.productos.length
        this.updateCarrusel()
      }
    })
  }

  setupTouchEvents() {
    let touchStartX = 0
    let touchEndX = 0
    let isDragging = false
    let startTime = 0
    let initialIndex = 0

    this.track.addEventListener(
      "touchstart",
      (e) => {
        touchStartX = e.touches[0].clientX
        startTime = Date.now()
        isDragging = true
        initialIndex = this.currentIndex
        this.track.style.transition = "none"
      },
      { passive: true },
    )

    this.track.addEventListener(
      "touchmove",
      (e) => {
        if (!isDragging) return

        touchEndX = e.touches[0].clientX
        const diff = touchEndX - touchStartX

        const productoWidth = Number.parseInt(
          getComputedStyle(document.documentElement).getPropertyValue("--producto-width"),
        )
        const spacing = this.getSpacing()
        const totalItemWidth = productoWidth + spacing
        const windowCenter = window.innerWidth / 2
        const baseOffset = -(this.currentIndex + 3) * totalItemWidth + (windowCenter - productoWidth / 2)

        this.track.style.transform = `translateX(${baseOffset + diff}px)`
      },
      { passive: true },
    )

    this.track.addEventListener("touchend", (e) => {
      if (!isDragging) return
      isDragging = false

      this.track.style.transition = "transform 0.5s cubic-bezier(0.4, 0, 0.2, 1)"

      touchEndX = e.changedTouches[0].clientX
      const diff = touchEndX - touchStartX
      const duration = Date.now() - startTime

      const isQuickSwipe = duration < 300 && Math.abs(diff) > 30
      const isLongSwipe = Math.abs(diff) > 100

      if (isQuickSwipe || isLongSwipe) {
        if (diff > 0) {
          this.prev()
        } else {
          this.next()
        }
      } else {
        this.currentIndex = initialIndex
        this.updateCarrusel()
      }
    })

    this.track.addEventListener(
      "touchmove",
      (e) => {
        if (Math.abs(touchEndX - touchStartX) > 10) {
          e.preventDefault()
        }
      },
      { passive: false },
    )
  }

  getSpacing() {
    return Number.parseInt(getComputedStyle(document.documentElement).getPropertyValue("--producto-spacing"))
  }

  scrollToCategory(categoria) {
    const index = this.categoryIndices[categoria]
    if (index !== undefined) {
      this.currentIndex = index
      this.updateCarrusel()
    }
  }

  renderProductos() {
    const productosInfinitos = [...this.productos.slice(-3), ...this.productos, ...this.productos.slice(0, 3)]

    this.track.innerHTML = productosInfinitos
      .map(
        (producto, index) => `
        <div class="producto ${index === this.currentIndex + 3 ? "active" : ""}" 
             data-categoria="${producto.categoria}"
             style="--producto-tamano: ${producto.tamano}">
          <div class="producto-imagen">
            <img src="${producto.imagen}" alt="Producto">
          </div>
          <div class="producto-info">
            <div class="producto-capacidad-container">
              <div class="producto-capacidad">${producto.capacidad}</div>
              <div class="producto-medida">${producto.medida}</div>
            </div>
            <button class="ver-mas" data-index="${(index - 3 + this.productos.length) % this.productos.length}">Ver +</button>
          </div>
        </div>
      `,
      )
      .join("")

    this.track.querySelectorAll(".ver-mas").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        const index = Number.parseInt(e.target.dataset.index)
        this.showPopup(this.productos[index])
      })
    })
  }

  updateCarrusel() {
    const productos = this.track.querySelectorAll(".producto")
    productos.forEach((producto, index) => {
      producto.classList.toggle("active", index === this.currentIndex + 3)
    })

    const productoWidth = Number.parseInt(
      getComputedStyle(document.documentElement).getPropertyValue("--producto-width"),
    )
    const spacing = this.getSpacing()
    const totalItemWidth = productoWidth + spacing

    // Calcular el ancho del contenedor y el centro
    const containerWidth = this.container.offsetWidth
    const containerCenter = containerWidth / 2

    // Ajustar el offset para mantener centrado el producto activo
    const offset = -((this.currentIndex + 3) * totalItemWidth) + (containerCenter - productoWidth / 2)

    this.track.style.transform = `translateX(${offset}px)`

    // Asegurar que solo se muestren 3 productos
    productos.forEach((producto, index) => {
      const distanceFromActive = Math.abs(index - (this.currentIndex + 3))
      if (distanceFromActive > 1) {
        producto.style.visibility = "hidden"
      } else {
        producto.style.visibility = "visible"
      }
    })

    const realIndex = ((this.currentIndex % this.productos.length) + this.productos.length) % this.productos.length
    const categoriaActual = this.productos[realIndex].categoria
    this.updateCategoriasActive(document.querySelector(`[data-categoria="${categoriaActual}"]`))
  }

  prev() {
    this.currentIndex--
    if (this.currentIndex < 0) {
      this.track.style.transition = "none"
      this.currentIndex = this.productos.length - 1
      this.updateCarrusel()
      requestAnimationFrame(() => {
        this.track.style.transition = "transform 0.5s cubic-bezier(0.4, 0, 0.2, 1)"
      })
    } else {
      this.track.style.transition = "transform 0.5s cubic-bezier(0.4, 0, 0.2, 1)"
      this.updateCarrusel()
    }
  }

  next() {
    this.currentIndex++
    if (this.currentIndex >= this.productos.length) {
      this.track.style.transition = "none"
      this.currentIndex = 0
      this.updateCarrusel()
      requestAnimationFrame(() => {
        this.track.style.transition = "transform 0.5s cubic-bezier(0.4, 0, 0.2, 1)"
      })
    } else {
      this.track.style.transition = "transform 0.5s cubic-bezier(0.4, 0, 0.2, 1)"
      this.updateCarrusel()
    }
  }

  updateCategoriasActive(activeLink) {
    if (!activeLink) return
    document.querySelectorAll(".categorias a").forEach((link) => {
      link.classList.remove("active")
    })
    activeLink.classList.add("active")
  }

  showPopup(producto) {
    const popup = document.getElementById("popup")
    const popupInfo = popup.querySelector(".popup-info")
    const imagenPopup = producto.popupImage || producto.imagen
    popupInfo.innerHTML = `
      <img src="${imagenPopup}" alt="${producto.descripcion}">
    `
    popup.style.display = "block"
  }
}

document.addEventListener("DOMContentLoaded", () => {
  new ProductShowcase()
})





