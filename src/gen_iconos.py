# -*- coding: utf-8 -*-
"""Iconos del rediseno.

Mismo concepto que la app actual (tres bandas cuyas alturas son 50/30/20),
con la paleta nueva: cielo, ambar y lima sobre negro. Ademas, los iconos de
los atajos que aparecen al mantener pulsado G&G en el movil.
"""
import os, zlib, struct

FONDO = (0x0B, 0x0D, 0x0A)
LIMA = (0xC6, 0xF4, 0x32)
BANDAS = [(0.50, (0x6E, 0xC1, 0xFF)),   # esenciales
          (0.30, (0xFF, 0xB2, 0x3E)),   # ocio
          (0.20, LIMA)]                 # ahorro

DESTINO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                       os.pardir, "docs", "iconos"))


def escribir_png(ruta, tam, pixel):
    filas = []
    for y in range(tam):
        filas.append(b"\x00" + bytes(v for x in range(tam) for v in pixel(x, y)))
    crudo = b"".join(filas)

    def trozo(tipo, datos):
        c = tipo + datos
        return struct.pack(">I", len(datos)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

    with open(ruta, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n"
                + trozo(b"IHDR", struct.pack(">IIBBBBB", tam, tam, 8, 2, 0, 0, 0))
                + trozo(b"IDAT", zlib.compress(crudo, 9))
                + trozo(b"IEND", b""))


def icono_bandas(tam):
    hueco = max(1, round(tam * 0.022))
    util = tam - hueco * 2
    altos = [round(util * BANDAS[0][0]), round(util * BANDAS[1][0])]
    altos.append(util - altos[0] - altos[1])
    cortes = []
    y = 0
    for i, (_, color) in enumerate(BANDAS):
        cortes.append((y, y + altos[i], color))
        y += altos[i] + (hueco if i < 2 else 0)

    def pixel(x, yy):
        for a, b, color in cortes:
            if a <= yy < b:
                return color
        return FONDO
    return pixel


def icono_gasto(tam):
    """Circulo lima con un + oscuro: el boton central de la app."""
    c, r = tam / 2.0, tam * 0.40
    grosor, largo = tam * 0.075, tam * 0.20

    def pixel(x, y):
        dx, dy = x + 0.5 - c, y + 0.5 - c
        if dx * dx + dy * dy > r * r:
            return FONDO
        if (abs(dx) <= grosor / 2 and abs(dy) <= largo) or (abs(dy) <= grosor / 2 and abs(dx) <= largo):
            return FONDO
        return LIMA
    return pixel


def icono_lista(tam):
    """Tres barras lima: la lista de movimientos."""
    barras = [(0.30, 0.74), (0.47, 0.74), (0.64, 0.56)]   # (y relativa, largo relativo)
    alto = tam * 0.085
    x0 = tam * 0.20

    def pixel(x, y):
        for yr, lr in barras:
            cy = tam * yr
            if abs(y + 0.5 - cy) <= alto / 2 and x0 <= x < x0 + tam * lr:
                return LIMA
        return FONDO
    return pixel


os.makedirs(DESTINO, exist_ok=True)
for nombre, tam, fn in [("icono-192.png", 192, icono_bandas), ("icono-512.png", 512, icono_bandas),
                        ("icono-maskable-512.png", 512, icono_bandas), ("apple-touch-icon.png", 180, icono_bandas),
                        ("favicon-32.png", 32, icono_bandas),
                        ("atajo-gasto.png", 96, icono_gasto), ("atajo-movs.png", 96, icono_lista)]:
    ruta = os.path.join(DESTINO, nombre)
    escribir_png(ruta, tam, fn(tam))
    print("%-26s %4d px  %5d bytes" % (nombre, tam, os.path.getsize(ruta)))
