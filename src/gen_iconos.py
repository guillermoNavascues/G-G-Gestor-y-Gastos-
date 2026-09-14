"""Genera los iconos de G&G: tres bandas horizontales cuyas alturas
son exactamente 50 / 30 / 20 — el propio metodo como identidad visual."""
import os, zlib, struct

FONDO = (0x13, 0x16, 0x14)
BANDAS = [(0.50, (0x2D, 0x6A, 0x8A)),   # esenciales
          (0.30, (0xB0, 0x7A, 0x2E)),   # ocio
          (0.20, (0x3E, 0x7A, 0x5C))]   # ahorro


def escribir_png(ruta, ancho, alto, filas):
    crudo = b"".join(b"\x00" + bytes(v for px in fila for v in px) for fila in filas)

    def trozo(tipo, datos):
        cuerpo = tipo + datos
        return (struct.pack(">I", len(datos)) + cuerpo
                + struct.pack(">I", zlib.crc32(cuerpo) & 0xFFFFFFFF))

    png = (b"\x89PNG\r\n\x1a\n"
           + trozo(b"IHDR", struct.pack(">IIBBBBB", ancho, alto, 8, 2, 0, 0, 0))
           + trozo(b"IDAT", zlib.compress(crudo, 9))
           + trozo(b"IEND", b""))
    with open(ruta, "wb") as f:
        f.write(png)


def icono(ruta, tam):
    hueco = max(1, round(tam * 0.022))          # separacion entre bandas
    util = tam - hueco * 2
    altos = [round(util * BANDAS[0][0]), round(util * BANDAS[1][0])]
    altos.append(util - altos[0] - altos[1])

    filas = []
    for i, (_, color) in enumerate(BANDAS):
        filas += [[color] * tam] * altos[i]
        if i < 2:
            filas += [[FONDO] * tam] * hueco

    # cuadra por redondeos
    while len(filas) < tam:
        filas.append(filas[-1])
    filas = filas[:tam]

    escribir_png(ruta, tam, tam, filas)
    return os.path.getsize(ruta)


destino = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "docs", "iconos"))
os.makedirs(destino, exist_ok=True)

for nombre, tam in [("icono-192.png", 192), ("icono-512.png", 512),
                    ("icono-maskable-512.png", 512), ("apple-touch-icon.png", 180),
                    ("favicon-32.png", 32)]:
    b = icono(os.path.join(destino, nombre), tam)
    print("%-26s %4d px  %5d bytes" % (nombre, tam, b))
