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
        "/static/manifest.json"
      ]);
    })
  );
});

self.addEventListener("fetch", (event) => {
  event.respondWith(
    caches.match(event.request).then((resp) => {
      return resp || fetch(event.request);
    })
  );
});
