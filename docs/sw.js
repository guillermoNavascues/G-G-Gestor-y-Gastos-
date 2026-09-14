/* G&G - service worker.
   Sube el numero de VERSION cada vez que cambies index.html. */
const VERSION = "v4";
const CACHE = "gyg-" + VERSION;

const ESQUELETO = [
  "./",
  "./index.html",
  "./manifest.webmanifest",
  "./iconos/icono-192.png",
  "./iconos/icono-512.png",
  "./iconos/icono-maskable-512.png",
  "./iconos/apple-touch-icon.png",
  "./iconos/favicon-32.png"
];

const FUENTES = /^https:\/\/fonts\.(googleapis|gstatic)\.com\//;

self.addEventListener("install", (ev) => {
  // {cache: "reload"} es imprescindible: sin el, addAll puede servirse de la
  // cache HTTP del navegador y guardar una copia vieja del index.html. La
  // version nueva quedaria cacheada como si fuese la actual y no llegaria.
  ev.waitUntil(
    caches.open(CACHE)
      .then((c) => c.addAll(ESQUELETO.map((u) => new Request(u, { cache: "reload" }))))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (ev) => {
  ev.waitUntil(
    caches.keys()
      .then((claves) => Promise.all(
        claves.filter((k) => k !== CACHE).map((k) => caches.delete(k))
      ))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (ev) => {
  const req = ev.request;
  if (req.method !== "GET") return;

  // Navegacion: cache primero y actualizacion en segundo plano.
  //
  // Abrir la app NUNCA debe esperar a la red. Con "red primero", una
  // conexion mala (una barra, portal cautivo del metro) deja la pantalla
  // en blanco hasta que la peticion agota su tiempo. Servimos lo que ya
  // esta en el movil al instante y buscamos version nueva por detras:
  // aparece en la siguiente apertura.
  if (req.mode === "navigate") {
    const actualizar = fetch(req)
      .then((res) => {
        const copia = res.clone();
        return caches.open(CACHE).then((c) => c.put("./index.html", copia)).then(() => res);
      })
      .catch(() => null);

    ev.waitUntil(actualizar);   // sincrono: mantiene vivo el worker hasta guardar
    ev.respondWith(
      caches.match("./index.html")
        .then((hit) => hit || actualizar.then((res) => res || fetch(req)))
    );
    return;
  }

  // Fuentes de Google: cache primero, se guardan al vuelo.
  if (FUENTES.test(req.url)) {
    ev.respondWith(
      caches.match(req).then((hit) => hit || fetch(req).then((res) => {
        const copia = res.clone();
        caches.open(CACHE).then((c) => c.put(req, copia));
        return res;
      }).catch(() => hit))
    );
    return;
  }

  // Todo lo demas del propio dominio: cache primero.
  if (new URL(req.url).origin === self.location.origin) {
    ev.respondWith(
      caches.match(req).then((hit) => hit || fetch(req).then((res) => {
        const copia = res.clone();
        caches.open(CACHE).then((c) => c.put(req, copia));
        return res;
      }))
    );
  }
});
