self.addEventListener("install", (event) => {
  event.waitUntil(caches.open("rakit-static-v1").then((cache) => cache.addAll(["/", "/static/css/app.css"])));
});

self.addEventListener("fetch", (event) => {
  event.respondWith(fetch(event.request).catch(() => caches.match(event.request)));
});

