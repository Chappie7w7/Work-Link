self.addEventListener("install", (event) => {
  console.log("Service Worker instalado");
  event.waitUntil(
    caches.open("worklink-cache-v3").then((cache) => {
      return cache.addAll([
        "/offline",
        "/static/css/style_index.css",
        "/static/css/style_login.css",
        "/static/icons/icon-192x192.png",
        "/static/icons/icon-512x512.png",
        "/static/manifest.json"
      ]);
    })
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys
          .filter((key) => key.startsWith("worklink-cache-") && key !== "worklink-cache-v3")
          .map((key) => caches.delete(key))
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (event) => {
  const req = event.request;
  const NAV_TIMEOUT_MS = 1200;

  async function fetchWithTimeout(request, ms) {
    if (typeof AbortController === 'undefined') {
      // Sin AbortController, intentar fetch normal
      return fetch(request);
    }
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), ms);
    try {
      const resp = await fetch(request, { signal: controller.signal });
      return resp;
    } finally {
      clearTimeout(timer);
    }
  }
  // 1) Estrategia: Network First para navegaciones (documentos/HTML) con fallback forzado a /offline
  if (req.mode === 'navigate' || req.destination === 'document') {
    event.respondWith(
      fetchWithTimeout(req, NAV_TIMEOUT_MS)
        .then(async (networkResp) => {
          // No cacheamos HTML de navegación para evitar mostrar páginas viejas
          return networkResp;
        })
        .catch(async () => {
          // Siempre ir a la vista offline en caso de fallo/timeout
          return caches.match('/offline');
        })
    );
    return;
  }

  // 2) API: nunca cachear (network-first con timeout). Evita respuestas obsoletas de /api/offline_jobs
  if (req.url.includes('/api/')) {
    event.respondWith(
      fetchWithTimeout(req, NAV_TIMEOUT_MS)
        .catch(async () => {
          // Intentar devolver algo del cache si existiera (aunque no lo almacenamos), de lo contrario, vacío
          const cached = await caches.match(req);
          if (cached) return cached;
          if (req.headers.get('accept')?.includes('application/json')) {
            return new Response('[]', { status: 200, headers: { 'Content-Type': 'application/json' } });
          }
          return new Response('Service Unavailable', { status: 503 });
        })
    );
    return;
  }

  // 3) Assets estáticos: Cache First
  event.respondWith(
    caches.match(req).then((cached) => {
      if (cached) return cached;
      return fetch(req)
        .then(async (resp) => {
          try {
            const cache = await caches.open('worklink-cache-v3');
            cache.put(req, resp.clone());
          } catch (e) {}
          return resp;
        })
        .catch(() => new Response('Sin conexión', { status: 503, statusText: 'Service Unavailable' }));
    })
  );
});
