document.addEventListener("DOMContentLoaded", () => {
    // Intersection Observer para las animaciones fade-in
    const observerOptions = {
      root: null,
      rootMargin: "0px",
      threshold: 0.1,
    }
  
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("visible")
          observer.unobserve(entry.target)
        }
      })
    }, observerOptions)
  
    document.querySelectorAll(".fade-in").forEach((element) => {
      observer.observe(element)
    })
  
    // Funcionalidad del menú hamburguesa
    const hamburger = document.querySelector(".hamburger")
    const navLinks = document.querySelector(".nav-links")
    const links = document.querySelectorAll(".nav-links a")
    const body = document.body
  
    if (hamburger && navLinks) {
      hamburger.addEventListener("click", () => {
        hamburger.classList.toggle("active")
        navLinks.classList.toggle("active")
        // Prevent scrolling when menu is open
        body.style.overflow = navLinks.classList.contains("active") ? "hidden" : ""
      })
  
      // Cerrar el menú cuando se hace clic en un enlace
      links.forEach((link) => {
        link.addEventListener("click", () => {
          hamburger.classList.remove("active")
          navLinks.classList.remove("active")
          body.style.overflow = ""
        })
      })
  
      // Cerrar el menú cuando se hace clic fuera de él
      document.addEventListener("click", (e) => {
        if (!hamburger.contains(e.target) && !navLinks.contains(e.target) && navLinks.classList.contains("active")) {
          hamburger.classList.remove("active")
          navLinks.classList.remove("active")
          body.style.overflow = ""
        }
      })
    }
  
    // Funcionalidad del botón Ver más+
    const verMasBtn = document.querySelector(".ver-mas-historia")
    const rightColumn = document.querySelector(".right-column")
  
    if (verMasBtn && rightColumn) {
      verMasBtn.addEventListener("click", () => {
        rightColumn.classList.toggle("show")
  
        if (rightColumn.classList.contains("show")) {
          verMasBtn.textContent = "Ver menos -"
        } else {
          verMasBtn.textContent = "Ver más +"
        }
      })
    }
  })
  
  
  