const navbars = document.querySelectorAll('.navbar');
if (navbars.length) {
  // Delegación de eventos para el botón hamburguesa
  document.addEventListener('click', (event) => {
    const toggleBtn = event.target.closest('.nav-toggle');
    if (!toggleBtn) return;

    const navbar = toggleBtn.closest('.navbar');
    if (!navbar) return;

    const navLinks = navbar.querySelector('.nav-links');
    if (!navLinks) return;

    const isOpen = navLinks.classList.toggle('open');
    toggleBtn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');

    if (isOpen) {
      navLinks.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
          if (navLinks.classList.contains('open')) {
            navLinks.classList.remove('open');
            toggleBtn.setAttribute('aria-expanded', 'false');
          }
        }, { once: true });
      });
    }
  });

  // Selector de sección que dispara el comportamiento de ocultar/mostrar
  const triggerElement = document.querySelector('#informacion') || document.body;

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
          navbars.forEach(nb => nb.classList.remove('hidden'));
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
        navbars.forEach(nb => {
          if (currentScroll > 50) {
            nb.classList.add('shrink');
          } else {
            nb.classList.remove('shrink');
          }
        });

        // sólo ocultamos si ya pasamos la sección trigger
        if (canHide) {
          if (currentScroll > lastScrollTop + scrollThreshold) {
            navbars.forEach(nb => nb.classList.add('hidden'));
          } else if (currentScroll < lastScrollTop) {
            navbars.forEach(nb => nb.classList.remove('hidden'));
          }
        } else {
          navbars.forEach(nb => nb.classList.remove('hidden'));
        }

        lastScrollTop = Math.max(0, currentScroll);
        ticking = false;
      });
      ticking = true;
    }
  }, { passive: true });
}