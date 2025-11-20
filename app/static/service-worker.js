self.addEventListener("install", (event) => {
  console.log("Service Worker instalado");
  event.waitUntil(
    caches.open("worklink-cache-v2").then((cache) => {
      return cache.addAll([
        "/", 
        "/static/css/style_index.css",
        "/static/css/style_login.css",
        "/static/icons/icon-192x192.png",
        "/static/icons/icon-512x512.png",
        "/static/manifest.json",
        "/offline",
        "/static/js/jquery-3.6.0.min.js"

      ]);
    })
  );
});

self.addEventListener("fetch", (event) => {
  event.respondWith(
    caches.match(event.request).then((resp) => {
      // Si está en caché, retornarlo
      if (resp) {
        return resp;
      }
      
      // Si no está en caché, intentar fetch
      return fetch(event.request).catch(() => {
        // Si falla el fetch (offline), retornar página offline para solicitudes de navegación
        if (event.request.destination === 'document' || 
            event.request.mode === 'navigate') {
          return caches.match('/offline');
        }
        
        // Para otros recursos, retornar un error básico
        return new Response('Sin conexión', {
          status: 503,
          statusText: 'Service Unavailable'
        });
      });
    })
  );
});
