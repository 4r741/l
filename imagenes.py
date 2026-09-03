#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Las imágenes del centro, dibujadas aquí.

    python3 imagenes.py --muestra      # una página con todas, para mirarlas

No hay fotografías del centro, y una web de clínica sin una sola imagen se lee
como un documento: era exactamente lo que le pasaba a esta. Así que la imagen
se dibuja. Campos de líneas que se levantan, arcos concéntricos, tramas de
puntos, anillos interrumpidos y seis retratos que no son de nadie. Todo es SVG
escrito por este guion: pesa poco, se ve nítido a cualquier tamaño y va dentro
del archivo, que es la regla de toda la entrega.

Nada de esto es adorno. El motivo que gobierna todas las piezas es el mismo
—el arco dental y sus catorce posiciones—, que es la forma del trabajo del
centro y el número de fases del recorrido del paciente.

Las piezas se publican una sola vez, como definiciones. Cada sitio donde
aparece una imagen no repite el dibujo: recorta un trozo distinto de la misma
pieza y le da su color desde la hoja de estilos. Once cabeceras cuestan lo que
cuestan cuatro dibujos.
"""
import math
import pathlib
import sys

AZUL = "#1F45FF"


class Azar:
    """Un generador congruencial: la misma semilla dibuja siempre lo mismo."""

    def __init__(self, semilla):
        self.x = (semilla * 1103515245 + 12345) & 0x7FFFFFFF

    def __call__(self):
        self.x = (self.x * 1103515245 + 12345) & 0x7FFFFFFF
        return self.x / 0x7FFFFFFF

    def entre(self, a, b):
        return a + (b - a) * self()


# ---------------------------------------------------------------------------
#  El arco dental: la curva de la que sale todo lo demás
# ---------------------------------------------------------------------------
def arco_punto(t, ancho, alto):
    """Un punto del arco, con t de 0 a 1 de un extremo al otro.

    No es media circunferencia: un arco dental va abierto por detrás y cerrado
    por delante. Una parábola achatada se le parece bastante.
    """
    x = (t - 0.5) * 2
    return (0.5 + x * 0.5) * ancho, (0.06 + 0.94 * (x * x)) * alto


def suave(puntos):
    """Una polilínea convertida en curva: los picos de una lista no se ven."""
    d = ["M%d %d" % puntos[0]]
    for i in range(len(puntos) - 1):
        x0, y0 = puntos[i]
        x1, y1 = puntos[i + 1]
        d.append("Q%d %d %d %d" % (x0, y0, (x0 + x1) // 2, (y0 + y1) // 2))
    d.append("L%d %d" % puntos[-1])
    return "".join(d)


def _trazo(d, ancho, opacidad, acento=False):
    return ('<path d="%s" fill="none" stroke="%s" stroke-width="%.2f" '
            'stroke-opacity="%.2f"/>'
            % (d, "var(--arte-a)" if acento else "currentColor", ancho, opacidad))


# ---------------------------------------------------------------------------
#  Las cuatro piezas
# ---------------------------------------------------------------------------
def campo(ancho=1200, alto=600, semilla=7, lineas=40, bultos=3, fuerza=1.0):
    """Un campo de líneas paralelas, levantado por debajo.

    Es la pieza que hace de fotografía. No representa nada y, aun así, tiene
    relieve, profundidad y un centro donde se puede poner un titular.
    """
    az = Azar(semilla)
    focos = []
    for _ in range(bultos):
        fx, fy = arco_punto(az.entre(0.12, 0.88), ancho, alto * 0.9)
        focos.append((fx, fy * az.entre(0.55, 1.0) + alto * 0.05,
                      az.entre(0.11, 0.25) * min(ancho, alto), az.entre(0.5, 1.0) * fuerza))
    paso = alto / (lineas + 1)
    n = 46
    trazos = []
    for i in range(1, lineas + 1):
        y0 = i * paso
        puntos = []
        for j in range(n + 1):
            x = ancho * j / n
            dy = 0.0
            for fx, fy, r, f in focos:
                d2 = ((x - fx) ** 2 + (y0 - fy) ** 2) / (2 * r * r)
                if d2 < 12:
                    dy -= math.exp(-d2) * r * 0.66 * f
            puntos.append((int(x), int(y0 + dy)))
        hondo = min(1.0, abs(min(p[1] for p in puntos) - y0) / (alto * 0.16))
        trazos.append(_trazo(suave(puntos), 1.1 + 1.5 * hondo, 0.20 + 0.62 * hondo,
                             i % 9 == 0 and hondo > 0.3))
    return "".join(trazos)


def arcos(ancho=1200, alto=600, capas=24, marcadas=(5, 9, 10)):
    """Arcos concéntricos sobre la curva dental, con sus catorce posiciones.

    Las tres marcadas no son un adorno: son las tres fases en las que el
    paciente decide —el diagnóstico, la presentación y el cierre—.
    """
    trazos = []
    for k in range(capas):
        f = k / (capas - 1.0)
        h, w = alto * (0.26 + 0.70 * f), ancho * (0.30 + 0.66 * f)
        base = alto * 0.97
        puntos = []
        for j in range(49):
            x, y = arco_punto(j / 48.0, w, h)
            puntos.append((int(x + (ancho - w) / 2), int(base - h + y)))
        trazos.append(_trazo(suave(puntos), 1.0 + f * 1.6, 0.12 + 0.46 * f))
    h, w, base = alto * 0.88, ancho * 0.94, alto * 0.97
    for i in range(14):
        x, y = arco_punto(0.045 + 0.91 * (i / 13.0), w, h)
        x, y = x + (ancho - w) / 2, base - h + y
        marcada = (i + 1) in marcadas
        trazos.append('<circle cx="%d" cy="%d" r="%d" fill="%s"/>'
                      % (x, y, 7 if marcada else 4,
                         "var(--arte-a)" if marcada else "currentColor"))
        if marcada:
            trazos.append('<circle cx="%d" cy="%d" r="16" fill="none" stroke="var(--arte-a)" '
                          'stroke-width="1.4" stroke-opacity=".5"/>' % (x, y))
    return "".join(trazos)


def trama(ancho=1200, alto=600, paso=22):
    """Una trama de puntos que se abre al acercarse al arco.

    Es la pieza tranquila: aguanta un texto encima sin pelearse con él, porque
    no tiene ni una línea recta que compita con el renglón.
    """
    h, w, base = alto * 0.74, ancho * 0.90, alto * 0.94
    curva = [arco_punto(j / 60.0, w, h) for j in range(61)]
    curva = [(x + (ancho - w) / 2, base - h + y) for x, y in curva]
    fuera = []
    for i in range(int(alto / paso) + 1):
        for j in range(int(ancho / paso) + 1):
            x, y = j * paso + paso / 2, i * paso + paso / 2
            d = min((x - cx) ** 2 + (y - cy) ** 2 for cx, cy in curva) ** 0.5
            f = max(0.0, 1.0 - d / (alto * 0.44))
            r = 0.8 + 3.4 * f * f
            if r < 0.95:
                continue
            fuera.append('<circle cx="%d" cy="%d" r="%.1f" fill="%s" fill-opacity="%.2f"/>'
                         % (x, y, r, "var(--arte-a)" if f > 0.88 else "currentColor",
                            0.16 + 0.6 * f))
    return "".join(fuera)


def anillos(lado=700, semilla=4, capas=32):
    """Anillos interrumpidos: el tiempo, sin dibujar una máquina.

    Un implante no se pone: se integra, por capas y con los meses. Esto es
    eso, y no la fotografía de un escáner que no tenemos.
    """
    az = Azar(semilla)
    c = lado / 2
    trazos = []
    for k in range(capas):
        f = k / (capas - 1.0)
        r = (0.05 + 0.92 * f) * c
        hueco, giro = az.entre(0.05, 0.5), az.entre(0, 2 * math.pi)
        d, dentro = [], False
        for j in range(73):
            a = 2 * math.pi * j / 72
            if abs(((a - giro + math.pi) % (2 * math.pi)) - math.pi) < hueco * math.pi:
                dentro = False
                continue
            d.append(("M" if not dentro else "L") + "%d %d"
                     % (c + r * math.cos(a), c + r * math.sin(a)))
            dentro = True
        trazos.append(_trazo("".join(d), 1.0 + f * 1.4,
                             0.14 + 0.5 * (1 - abs(f - 0.5) * 2), k in (11, 26)))
    return "".join(trazos)


def retrato(semilla, lado=400, lineas=30):
    """Un retrato que no es de nadie.

    Seis puestos, seis retratos: el mismo campo encerrado en un círculo, con
    los focos puestos de otra manera en cada uno. Se distinguen entre sí sin
    fingir que hay la fotografía de una persona que no ha posado para esto.
    """
    az = Azar(semilla * 977 + 13)
    focos = [(az.entre(0.25, 0.75) * lado, az.entre(0.22, 0.62) * lado,
              az.entre(0.13, 0.26) * lado, az.entre(0.7, 1.1)) for _ in range(3)]
    paso = lado / (lineas + 1)
    trazos = []
    for i in range(1, lineas + 1):
        y0 = i * paso
        puntos = []
        for j in range(27):
            x = lado * j / 26
            dy = 0.0
            for fx, fy, r, f in focos:
                d2 = ((x - fx) ** 2 + (y0 - fy) ** 2) / (2 * r * r)
                if d2 < 12:
                    dy -= math.exp(-d2) * r * 0.55 * f
            puntos.append((int(x), int(y0 + dy)))
        hondo = min(1.0, abs(min(p[1] for p in puntos) - y0) / (lado * 0.15))
        trazos.append(_trazo(suave(puntos), 1.0 + 1.3 * hondo, 0.30 + 0.58 * hondo,
                             i % 11 == 0))
    return ('<clipPath id="rc%d"><circle cx="%d" cy="%d" r="%d"/></clipPath>'
            '<g clip-path="url(#rc%d)">%s</g>'
            % (semilla, lado / 2, lado / 2, lado / 2, semilla, "".join(trazos)))


# ---------------------------------------------------------------------------
#  Lo que se publica en la página: las definiciones, una sola vez
# ---------------------------------------------------------------------------
PIEZAS = {
    "campo": (1200, 600, lambda: campo(semilla=7)),
    "campo2": (1200, 600, lambda: campo(semilla=23, lineas=42, bultos=2, fuerza=1.2)),
    "arcos": (1200, 600, arcos),
    "trama": (1200, 600, trama),
    "anillos": (700, 700, anillos),
}


def defensa():
    """Las piezas y los seis retratos, definidos una vez para toda la página."""
    partes = []
    for nombre, (_w, _h, fn) in PIEZAS.items():
        partes.append('<g id="arte-%s">%s</g>' % (nombre, fn()))
    for i in range(1, 7):
        partes.append('<g id="arte-retrato-%d">%s</g>' % (i, retrato(i)))
    return ('<svg class="artes" width="0" height="0" aria-hidden="true" focusable="false">'
            '<defs>%s</defs></svg>' % "".join(partes))


def arte(pieza, recorte, clase=""):
    """Un trozo de una pieza, ya definida, con su color puesto desde la hoja."""
    return ('<svg class="arte%s" viewBox="%s" preserveAspectRatio="xMidYMid slice" '
            'aria-hidden="true" focusable="false"><use href="#arte-%s"/></svg>'
            % ((" " + clase) if clase else "", recorte, pieza))


# ---------------------------------------------------------------------------
#  Para mirarlas antes de creérselas
# ---------------------------------------------------------------------------
def muestra():
    bloques = []
    for nombre, (w, h, _fn) in PIEZAS.items():
        for k, modo in enumerate(("noche", "dia")):
            bloques.append('<figure class="%s"><div class="c" style="--r:%s">%s</div>'
                           '<figcaption>%s · %s</figcaption></figure>'
                           % (modo, "16/7" if w > h else "1/1",
                              arte(nombre, "0 0 %d %d" % (w, h)), nombre, modo))
    for i in range(1, 7):
        bloques.append('<figure class="dia"><div class="c c--r">%s</div>'
                       '<figcaption>retrato %d</figcaption></figure>'
                       % (arte("retrato-%d" % i, "0 0 400 400"), i))
    pagina = ("<!doctype html><meta charset=utf-8><title>Muestra</title><style>"
              ":root{--arte-a:%s}body{margin:0;background:#fafafb;font:13px system-ui;padding:22px;"
              "display:grid;grid-template-columns:repeat(2,1fr);gap:22px}"
              "figure{margin:0}.c{aspect-ratio:16/7;line-height:0}"
              ".c--r{aspect-ratio:1/1;max-width:240px}"
              ".arte{width:100%%;height:100%%;display:block}"
              ".noche .c{background:#111112;color:#fff}.dia .c{background:#fff;color:#111112}"
              "figcaption{font:10px ui-monospace;letter-spacing:.2em;text-transform:uppercase;"
              "color:#888;padding-top:7px}</style>%s%s"
              % (AZUL, defensa(), "".join(bloques)))
    destino = pathlib.Path("/tmp/w/muestra.html")
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(pagina, encoding="utf-8")
    print("%s · %d KB de definiciones" % (destino, len(defensa().encode()) // 1024))


if __name__ == "__main__":
    if "--muestra" in sys.argv:
        muestra()
    else:
        print("%d KB de definiciones" % (len(defensa().encode()) // 1024))
