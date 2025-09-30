document.addEventListener('DOMContentLoaded', () => {
  const navbar = document.querySelector('.navbar');
  if (!navbar) return;

  // Cambia aquí el selector si quieres otra sección como trigger:
  const triggerSelector = '#informacion'; // ejemplo: '#informacion' o '.hero'
  const triggerElement = document.querySelector(triggerSelector) || document.querySelector('#informacion') || document.body;

  let canHide = false;              // sólo permitimos ocultar después de pasar trigger
  let lastScrollTop = 0;
  const scrollThreshold = 30;       // píxeles que deben acumularse para ocultar
  let lastKnownScrollY = 0;
  let ticking = false;

  // Si tenemos un elemento trigger distinto de body, observamos su intersección
  if (triggerElement && triggerElement !== document.body) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        // cuando el trigger está **fuera** de la vista (isIntersecting=false) permitimos ocultar
        canHide = !entry.isIntersecting;
        if (!canHide) {
          navbar.classList.remove('hidden'); // aseguramos que sea visible antes del trigger
        }
      });
    }, { root: null, threshold: 0, rootMargin: '0px' });

    io.observe(triggerElement);
  } else {
    // si no se encontró ninguna sección, permitimos ocultar (o ajusta a false si prefieres)
    canHide = true;
  }

  // Throttled scroll handler con requestAnimationFrame
  window.addEventListener('scroll', () => {
    lastKnownScrollY = window.scrollY;
    if (!ticking) {
      window.requestAnimationFrame(() => {
        const currentScroll = lastKnownScrollY;

        // efecto shrink
        if (currentScroll > 50) {
          navbar.classList.add('shrink');
        } else {
          navbar.classList.remove('shrink');
        }

        // sólo ocultamos si ya pasamos la sección trigger
        if (canHide) {
          if (currentScroll > lastScrollTop + scrollThreshold) {
            // baja lo suficiente → ocultar
            navbar.classList.add('hidden');
          } else if (currentScroll < lastScrollTop) {
            // sube → mostrar inmediatamente
            navbar.classList.remove('hidden');
          }
        } else {
          // antes del trigger, forzamos visible
          navbar.classList.remove('hidden');
        }

        lastScrollTop = Math.max(0, currentScroll);
        ticking = false;
      });
      ticking = true;
    }
  }, { passive: true });
});