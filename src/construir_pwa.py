# -*- coding: utf-8 -*-
"""Convierte gyg.html (version Artifact) en una PWA instalable:
documento completo + manifiesto + service worker + copia de seguridad."""
import io, os, sys

BASE = os.path.dirname(os.path.abspath(__file__))
DEST = os.path.abspath(os.path.join(BASE, os.pardir, "docs"))
os.makedirs(DEST, exist_ok=True)

src = io.open(os.path.join(BASE, "gyg.html"), encoding="utf-8").read()


def sustituir(texto, viejo, nuevo, etiqueta):
    if texto.count(viejo) != 1:
        sys.exit("ANCLA FALLIDA (%s): aparece %d veces" % (etiqueta, texto.count(viejo)))
    return texto.replace(viejo, nuevo)


# ---------------------------------------------------------------- 1. cabecera
CABECERA = u"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#F4F5F2" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#131614" media="(prefers-color-scheme: dark)">
<meta name="description" content="G&amp;G \u2014 Gestor y Gastos. Presupuesto personal con el m\u00e9todo 50/30/20.">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="iconos/favicon-32.png" sizes="32x32">
<link rel="apple-touch-icon" href="iconos/apple-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="G&amp;G">
<style>
  html{-webkit-text-size-adjust:100%}
  body{margin:0}
  img{max-width:100%}
  [hidden]{display:none!important}
</style>
"""

SEGURO = u"""</style>

<style>
  /* respeta el notch y la barra inferior del iPhone */
  body{padding-bottom:calc(96px + env(safe-area-inset-bottom))}
  .top{padding-top:calc(18px + env(safe-area-inset-top))}
  .fab{bottom:calc(20px + env(safe-area-inset-bottom))}
  .hoja{padding-bottom:calc(24px + env(safe-area-inset-bottom))}
</style>
</head>
<body>

<div class="wrap">"""

src = sustituir(src, u'</style>\n\n<div class="wrap">', SEGURO, "cierre de estilos")
src = CABECERA + src + u"\n</body>\n</html>\n"


# ------------------------------------------------- 2. pestana nueva en ajustes
src = sustituir(
    src,
    u'[["general","Reparto"],["meta","Metas"],["cuentas","Cuentas"],["fijos","Fijos"],["cats","Categorías"]]',
    u'[["general","Reparto"],["meta","Metas"],["cuentas","Cuentas"],["fijos","Fijos"],["cats","Categorías"],["datos","Copia"]]',
    "pestanas")


# -------------------------------------------------------- 3. panel de la copia
PANEL = u"""  if (pestana === "datos"){
    var inv = inventario();
    cuerpo =
      '<p class="nota" style="margin-top:0">Tus datos viven en este dispositivo. Antes de cambiar de móvil, exporta una copia y la importas en el nuevo.</p>' +
      '<div class="item" style="margin-bottom:12px">' +
        '<div class="g"><b>' + inv.meses + (inv.meses === 1 ? ' mes guardado' : ' meses guardados') + '</b>' +
        '<span>' + inv.movs + (inv.movs === 1 ? ' movimiento' : ' movimientos') + ' en total</span></div>' +
      '</div>' +
      '<button class="add" id="dExportar" style="margin-bottom:9px">Exportar copia de seguridad</button>' +
      '<button class="add" id="dImportar">Importar una copia</button>' +
      '<input type="file" id="dFichero" accept="application/json,.json" style="display:none">' +
      '<div id="dAviso"></div>' +
      instalarHTML();
  }

"""
# el panel se construye ANTES de volcar el HTML...
src = sustituir(src,
                u'  document.getElementById("ajBody").innerHTML =\n    \'<h2>Ajustes',
                PANEL + u'  document.getElementById("ajBody").innerHTML =\n    \'<h2>Ajustes',
                "panel copia")

# ...y se cablea DESPUES, cuando los botones ya existen en el DOM
src = sustituir(src, u'  // categorías\n  if (pestana === "cats"){',
                u'  // copia de seguridad\n  if (pestana === "datos"){ cablearDatos(); }\n\n'
                u'  // categorías\n  if (pestana === "cats"){',
                "cableado copia")


# ------------------------------------------------- 4. logica de copia e install
LOGICA = u"""/* ============================ copia de seguridad ============================ */

function inventario(){
  var meses = mesesConocidos(), movs = 0;
  Object.keys(meses).forEach(function(id){
    movs += ((meses[id] && meses[id].movimientos) || []).length;
  });
  return {meses: Object.keys(meses).length, movs: movs, datos: meses};
}

function exportarCopia(){
  var inv = inventario();
  var paquete = {
    app: "gyg", version: 1,
    exportado: new Date().toISOString(),
    config: cfg(), meses: inv.datos
  };
  var blob = new Blob([JSON.stringify(paquete, null, 2)], {type: "application/json"});
  var url = URL.createObjectURL(blob);
  var a = document.createElement("a");
  a.href = url; a.download = "gyg-" + hoyISO() + ".json";
  document.body.appendChild(a); a.click(); a.remove();
  setTimeout(function(){ URL.revokeObjectURL(url); }, 2000);
  avisoDatos("ok", "Copia descargada. Gu\\u00e1rdala donde puedas recuperarla desde el otro m\\u00f3vil.");
}

function importarCopia(fichero){
  var fr = new FileReader();
  fr.onload = function(){
    var d;
    try{ d = JSON.parse(String(fr.result)); }catch(e){ d = null; }
    if (!d || (d.app !== "gyg" && d.app !== "tres-sobres")){
      avisoDatos("mal", "Ese fichero no es una copia de G&G. Busca el .json que exportaste.");
      return;
    }
    if (d.config) { S.config = normalizarConfig(d.config); almacen.escribir("config/app", "config", S.config); }
    var n = 0;
    Object.keys(d.meses || {}).forEach(function(id){
      S.meses[id] = d.meses[id];
      almacen.escribir("meses/" + id, "mes:" + id, d.meses[id]);
      n++;
    });
    render();
    pintarAjustes();
    avisoDatos("ok", "Restaurados " + n + (n === 1 ? " mes." : " meses."));
  };
  fr.onerror = function(){ avisoDatos("mal", "No se ha podido leer el fichero."); };
  fr.readAsText(fichero);
}

function avisoDatos(tipo, texto){
  var el = document.getElementById("dAviso");
  if (!el) return;
  var col = tipo === "ok" ? "var(--a)" : "var(--danger)";
  el.innerHTML = '<p class="nota" style="margin:12px 0 0;color:' + col + '">' + esc(texto) + '</p>';
}

var promptInstalar = null;
window.addEventListener("beforeinstallprompt", function(ev){
  ev.preventDefault();
  promptInstalar = ev;
});

function yaInstalada(){
  return (window.matchMedia && window.matchMedia("(display-mode: standalone)").matches)
      || window.navigator.standalone === true;
}

function instalarHTML(){
  if (yaInstalada()) return '<p class="nota" style="margin:16px 0 0">Est\\u00e1s usando la app instalada. \\u00bfQu\\u00e9 bien.</p>';
  if (promptInstalar) return '<button class="btn" id="dInstalar" style="margin-top:16px;width:100%">Instalar en este m\\u00f3vil</button>';
  var esIOS = /iphone|ipad|ipod/i.test(navigator.userAgent);
  if (esIOS) return '<p class="nota" style="margin:16px 0 0">Para instalarla: toca <b>Compartir</b> en Safari y elige <b>A\\u00f1adir a pantalla de inicio</b>.</p>';
  return '<p class="nota" style="margin:16px 0 0">Para instalarla: men\\u00fa del navegador y <b>Instalar aplicaci\\u00f3n</b> o <b>A\\u00f1adir a pantalla de inicio</b>.</p>';
}

function cablearDatos(){
  var ex = document.getElementById("dExportar");
  var im = document.getElementById("dImportar");
  var fi = document.getElementById("dFichero");
  var ins = document.getElementById("dInstalar");
  if (ex) ex.onclick = exportarCopia;
  if (im) im.onclick = function(){ fi.click(); };
  if (fi) fi.onchange = function(){ if (fi.files && fi.files[0]) importarCopia(fi.files[0]); };
  if (ins) ins.onclick = function(){
    promptInstalar.prompt();
    promptInstalar.userChoice.then(function(){ promptInstalar = null; pintarAjustes(); });
  };
}

"""
src = sustituir(src, u'/* ============================ arranque ============================ */',
                LOGICA + u'/* ============================ arranque ============================ */',
                "logica copia")


# ---------------------------------------------------------- 5. pie informativo
src = sustituir(
    src,
    u'''  document.getElementById("sync").innerHTML = almacen.estado === "nube"
    ? "<b>Sincronizado en la nube.</b> Tus datos te siguen si cambias de móvil."
    : "<b>Guardado solo en este dispositivo.</b> Aún no hay conexión con la nube.";''',
    u'''  document.getElementById("sync").innerHTML = almacen.estado === "nube"
    ? "<b>Sincronizado en la nube.</b> Tus datos te siguen si cambias de móvil."
    : "<b>Guardado en este dispositivo.</b> Antes de cambiar de móvil, exporta una copia desde Ajustes \\u2192 Copia.";''',
    "pie")


# ------------------------------------------------------ 6. service worker + pie
ARRANQUE = u"""
/* ============================ instalacion ============================ */

if ("serviceWorker" in navigator){
  window.addEventListener("load", function(){
    navigator.serviceWorker.register("sw.js").catch(function(){});
  });
}

})();
</script>"""
src = sustituir(src, u'\n})();\n</script>', ARRANQUE, "cierre del script")

io.open(os.path.join(DEST, "index.html"), "w", encoding="utf-8").write(src)


# -------------------------------------------------------------- 7. manifiesto
MANIFIESTO = u"""{
  "name": "G&G \u2014 Gestor y Gastos",
  "short_name": "G&G",
  "description": "Presupuesto personal con el m\\u00e9todo 50/30/20.",
  "lang": "es-ES",
  "start_url": "./",
  "scope": "./",
  "display": "standalone",
  "orientation": "portrait",
  "background_color": "#F4F5F2",
  "theme_color": "#F4F5F2",
  "icons": [
    { "src": "iconos/icono-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any" },
    { "src": "iconos/icono-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any" },
    { "src": "iconos/icono-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable" }
  ]
}
"""
io.open(os.path.join(DEST, "manifest.webmanifest"), "w", encoding="utf-8").write(MANIFIESTO)


# ---------------------------------------------------------- 8. service worker
SW = u"""/* G&G - service worker.
   Sube el numero de VERSION cada vez que cambies index.html. */
const VERSION = "v9";
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

const FUENTES = /^https:\\/\\/fonts\\.(googleapis|gstatic)\\.com\\//;

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
"""
io.open(os.path.join(DEST, "sw.js"), "w", encoding="utf-8").write(SW)

print("index.html          %6d bytes" % os.path.getsize(os.path.join(DEST, "index.html")))
print("manifest.webmanifest %5d bytes" % os.path.getsize(os.path.join(DEST, "manifest.webmanifest")))
print("sw.js               %6d bytes" % os.path.getsize(os.path.join(DEST, "sw.js")))
