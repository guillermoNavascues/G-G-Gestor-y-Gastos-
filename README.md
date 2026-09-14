# G&G — Gestor y Gastos

Presupuesto personal con el método **50/30/20**, pensado para usarse desde el
móvil. Se instala como app (Android e iPhone), funciona sin conexión y no
depende de ninguna tienda de aplicaciones.

- **50 %** esenciales — vivienda, comida, transporte, salud
- **30 %** ocio — restaurantes, ropa, caprichos, viajes
- **20 %** ahorro — fondo de emergencia e inversión

## Qué hace

- Los tres sobres arriba, con lo que queda en cada uno, y la lista de gastos abajo.
- **Comprometido vs. libre:** los gastos fijos que aún no han pasado se
  descuentan visualmente, para no confundir el saldo con dinero disponible.
- **Capital acumulado:** todo lo que no has gastado desde que usas la app,
  desglosado entre lo apartado en el sobre de ahorro y lo que sobró sin
  llegar a moverlo. Mover dinero al ahorro no cuenta como gasto: cambia de
  sitio y sigue siendo tuyo.
- **Plan de traspasos al cobrar:** cuánto mover a cada cuenta el día de la
  nómina, según el papel que tenga asignado cada banco.
- Devoluciones y Bizums recibidos restan del gasto en lugar de contar como ingreso.
- Los traspasos entre cuentas propias no tocan ningún sobre.
- Arrastre configurable de lo que sobra a fin de mes.
- Copia de seguridad exportable e importable en `.json`.

La categoría decide en qué sobre cae un gasto — **no** la cuenta desde la que
se paga. Es lo que permite que el 50 % se reparta entre varios bancos.

## Estructura

```
src/
  gyg.html            Fuente único de la app
  construir_pwa.py    Genera docs/ a partir del fuente
  gen_iconos.py       Genera los iconos (las bandas son 50/30/20)
docs/
  index.html          Build de la PWA — lo que sirve GitHub Pages
  manifest.webmanifest
  sw.js               Service worker
  .nojekyll           Para que Pages sirva .well-known/
  iconos/
```

Sin npm, sin build system, sin dependencias. Python solo para generar.

## Compilar

```bash
cd src
python gen_iconos.py      # sólo si cambian los colores de marca
python construir_pwa.py
```

`docs/index.html` **no se edita a mano**: se regenera. Todo cambio va en
`src/gyg.html`.

> Al cambiar la app, sube el número de `VERSION` en `sw.js` (`"v1"` → `"v2"`).
> Sin eso, los móviles que ya la tengan instalada seguirán sirviendo la
> versión cacheada.

## Publicar en GitHub Pages

*Settings → Pages → Source: rama `main`, carpeta `/docs`.*

Queda en `https://<usuario>.github.io/<repo>/`. Hace falta HTTPS: sin
certificado no hay service worker, y sin service worker no hay instalación.

## Instalar en el móvil

- **Android (Chrome):** menú ⋮ → *Instalar aplicación*.
- **iPhone (Safari):** *Compartir* → *Añadir a pantalla de inicio*. Tiene que
  ser Safari; desde Chrome en iOS no se instala.

## Generar el APK

El APK se construye con [PWABuilder](https://www.pwabuilder.com) a partir de
la URL de Pages. Genera una *Trusted Web Activity*: una app Android real que
envuelve la PWA.

1. Pega la URL de Pages en PWABuilder → *Package for stores* → *Android*.
2. Guarda el **keystore y sus contraseñas** en sitio seguro. Si se pierden,
   no se podrá volver a firmar una actualización de la app.
3. Copia el `assetlinks.json` que genera a `docs/.well-known/assetlinks.json`
   y vuelve a publicar. Sin ese fichero la app muestra barra de direcciones.
4. Instala el APK en el móvil (hay que permitir orígenes desconocidos).

El APK es un envoltorio: carga desde la URL de Pages y funciona sin conexión
gracias al service worker, pero el primer arranque necesita red.

**El APK es solo para Android.** En iPhone no existe el sideload: allí se
instala la PWA desde Safari. La PWA es el producto; el APK, una comodidad.

## Dónde viven los datos

En el almacenamiento del navegador, en ese dominio concreto. Implica que:

1. No se sincronizan entre dispositivos.
2. Cambiar de dominio equivale a empezar de cero.
3. Al cambiar de móvil hay que migrar a mano: *Ajustes → Copia → Exportar*,
   y en el nuevo *Importar*.

La sincronización real llega en la Fase 2, cuando el backend haga falta de
todas formas.

## Hoja de ruta

| Fase | Contenido | Estado |
|------|-----------|--------|
| 0 | App manual, tres sobres, gastos fijos, plan de traspasos | ✅ |
| 1 | Importación de extractos CSV + motor de reglas de categorización | pendiente |
| 2 | Conexión bancaria PSD2 vía GoCardless + backend + sincronización | pendiente |
| 3 | Notificaciones, fondos de reserva, detección de recurrentes | pendiente |
| 4 | Informes, patrimonio neto, exportación | pendiente |

### Sobre la conexión bancaria (Fase 2)

Los bancos no se conectan directamente: en Europa se hace vía PSD2 a través
de un agregador con licencia AISP. **GoCardless Bank Account Data** es
prácticamente el único con acceso self-service sin sociedad constituida.

Limitaciones que son regulatorias, no técnicas:

- **Solo lectura.** PSD2-AIS permite leer movimientos y saldos, no mover
  dinero. Los traspasos los ejecuta el usuario; la app sólo dice cuánto.
- **Reconsentimiento cada 90–180 días** según el banco.
- Histórico inicial limitado a unos 90 días.
