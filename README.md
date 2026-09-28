# G&G — Gestor y Gastos

Presupuesto personal con el método **50/30/20**, pensado para usarse desde el
móvil. Se instala como app (Android e iPhone), funciona sin conexión y no
depende de ninguna tienda de aplicaciones.

- **50 %** esenciales — vivienda, comida, transporte, salud
- **30 %** ocio — restaurantes, ropa, caprichos, viajes
- **20 %** ahorro — fondo de emergencia e inversión

## Diseño

Oscuro con acento verde lima, inspirado en el panel de *Control Financiero*
(@controlapp_es) y adaptado a Android: tipografía Manrope, cercana a MiSans.

- **Tres secciones:** *Inicio* (balance del mes, patrimonio, reparto, metas y
  últimos movimientos), *Movimientos* (con filtros) y *Análisis* (a dónde ha ido
  la nómina, dónde está tu dinero y el plan de traspasos).
- **Barra inferior** con el botón **+** en el centro. En pantallas anchas se
  convierte en el menú lateral del diseño original.
- **Alta rápida en tres pasos:** *¿Qué es?* → *¿Cuánto cuesta?* (teclado
  numérico propio) → *¿De qué es?*. Recuerda: al repetir un concepto propone el
  importe, la categoría y la cuenta de la última vez.
- **Atajos del icono:** mantén pulsado G&G → *Nuevo gasto* o *Movimientos*. El
  atajo se puede arrastrar a la pantalla de inicio como botón de un toque.
- **Gesto atrás de Android:** retrocede un paso, cierra la hoja o vuelve a
  Inicio, en lugar de salir de la app.
- Aviso inferior con **Deshacer** al apuntar un gasto.

## Qué hace

- Los tres sobres, con lo que queda en cada uno, y la lista de gastos.
- **Comprometido vs. libre:** los gastos fijos que aún no han pasado se
  descuentan visualmente, para no confundir el saldo con dinero disponible.
- **Capital ahorrado y Ahorros:** lo que sobró de esenciales y ocio este mes,
  y el total acumulado de todos los meses. Mover dinero al ahorro no cuenta
  como gasto: cambia de sitio y sigue siendo tuyo.
- **Metas de ahorro:** varias compras concretas a la vez, ordenadas por
  prioridad. Se aporta con un movimiento de tipo *Meta*, como cualquier otro
  gasto, así que lo acumulado es dinero realmente apartado y no una promesa.
  Cada meta dice cuánto le falta y para cuándo: con una aportación mensual
  prevista mientras no hayas aportado nada, y con tu ritmo real en cuanto
  empiezas — describe lo que haces, no lo que dijiste que harías.

  Entre todas las metas no pueden llevarse más de **el sobre de ocio + un
  10 % del sobre de ahorro** al mes. De los esenciales, nada. El límite lo
  impone la app: una aportación que se pase no se guarda.
- **Plan de traspasos al cobrar:** cuánto mover a cada cuenta el día de la
  nómina, según el papel que tenga asignado cada banco.
- Devoluciones y Bizums recibidos restan del gasto en lugar de contar como ingreso.
- **El sobre de ahorro se cumple con traspasos, no gastando de él.** Muestra
  el objetivo del mes y se marca como hecho cuando has movido esa cantidad a
  la cuenta con rol *Ahorro*. Si retiras dinero de ahí, se desmarca sola: el
  cómputo es neto.
- Los traspasos entre cuentas propias no cuentan como gasto.
- **Efectivo.** Es una cuenta más: puedes pagar en metálico, ingresarlo en el
  banco o sacarlo, con un traspaso normal. En *Ajustes → Cuentas*, el campo
  **ya tenía** declara el dinero que había en cada sitio antes de empezar a
  usar la app, para que cuente desde el primer día.
- **Dónde está tu dinero:** el saldo de cada cuenta, calculado a partir del
  saldo inicial y de todo lo registrado. Su total coincide con el de Ahorros:
  son dos caminos al mismo número.
- Los sobres son siempre el porcentaje exacto del ingreso: lo que sobra a fin
  de mes no los infla, pasa a los ahorros.
- **Recuperarse de errores** (*Ajustes → Datos*):
  - **Deshacer:** antes de cada cambio se guarda cómo estaba lo que se va a
    pisar; se conservan los últimos 20 pasos.
  - **Copias de cada mes:** una foto completa al empezar cada mes; quedan las
    dos últimas.
  - **Borrar este mes:** vacía los movimientos del mes que estás viendo, con
    doble toque. Los demás meses y lo ahorrado en ellos no se tocan, y se puede
    deshacer.
- Copia de seguridad exportable e importable en `.json`.

La categoría decide en qué sobre cae un gasto — **no** la cuenta desde la que
se paga. Es lo que permite que el 50 % se reparta entre varios bancos.

## Estructura

```
src/
  gyg.html            Fuente único de la app
  construir_pwa.py    Genera docs/ a partir del fuente
  gen_iconos.py       Genera los iconos (bandas 50/30/20) y los de los atajos
docs/
  index.html          Build de la PWA — lo que sirve Cloudflare
  manifest.webmanifest
  sw.js               Service worker
  .nojekyll           Para que GitHub Pages sirviese .well-known/ (sin uso hoy)
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

## Publicar

Desplegado en **Cloudflare Workers** como Worker de sólo activos: `wrangler.jsonc`
declara `docs/` como directorio a servir, y cada push a `main` despliega solo.

Se eligió Workers en lugar de Pages porque el backend de PSD2 de la Fase 2 vivirá
aquí mismo: bastará añadir `main` al `wrangler.jsonc` y el mismo Worker servirá la
app y la API bajo el mismo dominio. Cambiar de dominio implicaría perder los datos
guardados en el móvil, así que conviene no mudarse.

Hace falta HTTPS: sin certificado no hay service worker, y sin service worker no
hay instalación ni funcionamiento sin conexión.

## Instalar en el móvil

- **Android (Chrome):** menú ⋮ → *Instalar aplicación*.
- **iPhone (Safari):** *Compartir* → *Añadir a pantalla de inicio*. Tiene que
  ser Safari; desde Chrome en iOS no se instala.

Los atajos del icono sólo aparecen si la app está **instalada** desde Chrome
(*Instalar aplicación*), no si es un simple acceso directo de *Añadir a pantalla
de inicio*. Un botón en los Ajustes rápidos de Android no es posible para una
web instalada: sólo pueden añadirlo apps nativas.

## Generar el APK

El APK se construye con [PWABuilder](https://www.pwabuilder.com) a partir de
la URL publicada. Genera una *Trusted Web Activity*: una app Android real que
envuelve la PWA.

1. Pega la URL publicada en PWABuilder → *Package for stores* → *Android*.
2. Guarda el **keystore y sus contraseñas** en sitio seguro. Si se pierden,
   no se podrá volver a firmar una actualización de la app.
3. Copia el `assetlinks.json` que genera a `docs/.well-known/assetlinks.json`
   y vuelve a publicar. Sin ese fichero la app muestra barra de direcciones.
4. Instala el APK en el móvil (hay que permitir orígenes desconocidos).

El APK es un envoltorio: carga desde la URL publicada y funciona sin conexión
gracias al service worker, pero el primer arranque necesita red.

**El APK es solo para Android.** En iPhone no existe el sideload: allí se
instala la PWA desde Safari. La PWA es el producto; el APK, una comodidad.

## Dónde viven los datos

En el almacenamiento del navegador, en ese dominio concreto. Implica que:

1. No se sincronizan entre dispositivos.
2. Cambiar de dominio equivale a empezar de cero.
3. Al cambiar de móvil hay que migrar a mano: *Ajustes → Datos → Exportar*,
   y en el nuevo *Importar*.

La sincronización real llega en la Fase 2, cuando el backend haga falta de
todas formas.

## Hoja de ruta

| Fase | Contenido | Estado |
|------|-----------|--------|
| 0 | App manual, tres sobres, gastos fijos, plan de traspasos, metas de ahorro | ✅ |
| 1 | Importación de extractos CSV + motor de reglas de categorización | pendiente |
| 2 | Conexión bancaria PSD2 vía GoCardless + backend + sincronización | pendiente |
| 3 | Notificaciones, detección de recurrentes, fondos para gastos anuales | pendiente |
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
