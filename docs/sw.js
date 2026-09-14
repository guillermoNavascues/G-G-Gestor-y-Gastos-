/* G&G - service worker.
   Sube el numero de VERSION cada vez que cambies index.html. */
const VERSION = "v7";
const CACHE = "gyg-" + VERSION;

// "./" es la entrada canonica de la app y la que declara el manifiesto.
// NO se lista "./index.html": Cloudflare (y otros hosts) responden a esa
// ruta con un 307 hacia "/", y una respuesta redirigida no se puede
// guardar en la cache. Listarla haria fallar la instalacion entera y nos
// quedariamos sin modo sin conexion, encima en silencio.
const ESQUELETO = [
  "./",
  "./manifest.webmanifest",
  "./iconos/icono-192.png",
  "./iconos/icono-512.png",
  "./iconos/icono-maskable-512.png",
  "./iconos/apple-touch-icon.png",
  "./iconos/favicon-32.png"
];

const FUENTES = /^https:\/\/fonts\.(googleapis|gstatic)\.com\//;

self.addEventListener("install", (ev) => {
  // Se guarda fichero a fichero en lugar de con addAll: addAll es todo o
  // nada, asi que un solo activo caido dejaria al worker sin instalar y a
  // la app sin funcionar sin conexion. Aqui lo que falle se reintentara
  // en su proxima peticion.
  //
  // {cache: "reload"} es imprescindible: sin el, la copia podria salir de
  // la cache HTTP del navegador y guardariamos una version vieja dandola
  // por actual, con lo que la actualizacion no llegaria nunca.
  ev.waitUntil(
    caches.open(CACHE)
      .then((c) => Promise.all(ESQUELETO.map((u) =>
        fetch(new Request(u, { cache: "reload" }))
          .then((res) => (res.ok ? c.put(u, res) : null))
          .catch(() => null)
      )))
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
        // Una respuesta redirigida no se puede guardar; se sirve igual.
        if (!res.ok || res.redirected) return res;
        const copia = res.clone();
        return caches.open(CACHE).then((c) => c.put("./", copia)).then(() => res);
      })
      .catch(() => null);

    ev.waitUntil(actualizar);   // sincrono: mantiene vivo el worker hasta guardar
    ev.respondWith(
      caches.match("./")
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
