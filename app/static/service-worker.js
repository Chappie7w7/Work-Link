self.addEventListener("install", (event) => {
  console.log("Service Worker instalado");
  event.waitUntil(
    caches.open("worklink-cache").then((cache) => {
      return cache.addAll([
        "/", 
        "/static/css/style_index.css",
        "/static/css/style_login.css",
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
