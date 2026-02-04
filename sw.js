const CACHE = "escape-math-v2";

const ASSETS = [
  "/",
  "/index.html",
  "/styles.css",
  "/app.js",
  "/manifest.json",

  "/assets/game_Intro.mp4",
  "/assets/game_exit.png",
  "/assets/bgm.mp3",

  "/assets/bg_1.png",
  "/assets/bg_2.png",
  "/assets/bg_3.png",
  "/assets/bg_4.png",
  "/assets/bg_5.png",
  "/assets/bg_6.png",
  "/assets/bg_7.png",
  "/assets/bg_8.png",
  "/assets/bg_9.png"
];

self.addEventListener("install", (e) => {
  self.skipWaiting();
  e.waitUntil(
    caches.open(CACHE).then((cache) => cache.addAll(ASSETS))
  );
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys.map((key) => {
          if (key !== CACHE) return caches.delete(key);
        })
      )
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (e) => {
  if (e.request.method !== "GET") return;

  e.respondWith(
    caches.match(e.request).then((cached) => {
      if (cached) return cached;

      return fetch(e.request)
        .then((response) => {
          const copy = response.clone();
          caches.open(CACHE).then((cache) => cache.put(e.request, copy));
          return response;
        })
        .catch(() => cached);
    })
  );
});