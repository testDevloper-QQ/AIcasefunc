const CACHE = "cai-jiu-duo-lian-v7";
const ASSETS = ["/", "/index.html", "/manifest.json"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(ASSETS)));
  self.skipWaiting();
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (e) => {
  const url = new URL(e.request.url);
  if (url.pathname.startsWith("/api/")) return;
  if (url.pathname.startsWith("/skill-assets/")) {
    e.respondWith(
      fetch(e.request).then((resp) => resp).catch(() => caches.match(e.request))
    );
    return;
  }
  if (url.pathname === "/app.js" || url.pathname === "/styles.css") {
    e.respondWith(fetch(e.request).then((resp) => resp));
    return;
  }
  e.respondWith(
    caches.match(e.request).then((cached) => cached || fetch(e.request))
  );
});
