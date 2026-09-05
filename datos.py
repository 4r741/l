#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Las cifras del centro, dibujadas.

    python3 datos.py --muestra    # una hoja con las tres figuras, para mirarlas

Hasta aquí los datos del sistema se enseñaban como se enseñan en un documento:
tablas, listas y barras horizontales. Se leen, pero no se ven. Esto es lo
contrario: cada cifra que importa se dibuja, con la misma mano con la que están
dibujadas las imágenes del centro —trazo fino, blanco, un solo color— y con la
misma forma, el arco dental de catorce posiciones, que es la forma del trabajo
que se hace aquí.

Tres figuras, y ninguna inventa un número:

    arco()      el recorrido del paciente sobre el arco dental. Cada fase es
                una posición, su duración es el grosor del trazo y las fases en
                las que el paciente decide van en color.
    cascada()   el puente de lo heredado al objetivo, bloque a bloque, con lo
                que aporta cada uno y la línea que los acumula.
    rejilla()   quién hace qué en las catorce fases, en puntos en vez de en
                letras: se ve el reparto antes de leer una sola casilla.

Todo sale en SVG escrito a mano, sin biblioteca ninguna, con «currentColor» y
«var(--azul)» para que la hoja de estilos mande sobre el color y el archivo
siga abriéndose sin conexión.
"""
import math
import pathlib
import sys
from xml.sax.saxutils import escape

RAIZ = pathlib.Path(__file__).parent


# --------------------------------------------------------------------------
#  La forma
# --------------------------------------------------------------------------
def arco_punto(t, ancho, alto):
    """Un punto del arco dental, con t de 0 a 1 de un extremo al otro.

    Es la misma curva con la que se dibujan las imágenes del centro. Que la
    figura de datos y la imagen compartan la forma no es un adorno: es lo que
    hace que las dos se lean como una sola cosa.
    """
    x = (t - 0.5) * 2
    return (0.5 + x * 0.5) * ancho, (0.06 + 0.94 * (x * x)) * alto


def _n(v):
    """Un número corto: el SVG no necesita quince decimales."""
    return ("%.2f" % v).rstrip("0").rstrip(".")


def _texto(x, y, txt, tam=11, anclaje="middle", clase="", extra=""):
    return ('<text x="%s" y="%s" text-anchor="%s" class="dib__t %s" '
            'font-size="%s"%s>%s</text>'
            % (_n(x), _n(y), anclaje, clase, _n(tam), extra, escape(txt)))


# --------------------------------------------------------------------------
#  1 · El recorrido del paciente, sobre el arco
# --------------------------------------------------------------------------
def arco(fases, ancho=1200, alto=680, decisivas=(7, 9, 10)):
    """Las catorce fases del recorrido, colocadas sobre el arco dental.

    «fases» es una lista de diccionarios con n, label y min. La posición de
    cada fase en el arco es su sitio en el recorrido; el radio de su marca, lo
    que dura. Las fases en las que el paciente decide —el diagnóstico, la
    presentación y el cierre— van en color: son las tres que deciden si hay
    tratamiento, y en un recorrido de catorce se pierden si no se marcan.
    """
    if not fases:
        return ""
    m = 108.0                                  # margen para los dos anillos de rótulos
    an, al = ancho - 2 * m, alto - 2 * m
    tope = max((f.get("min") or 1) for f in fases)
    n = len(fases)

    # la curva, dibujada con muchos puntos para que salga limpia
    curva = []
    for i in range(241):
        x, y = arco_punto(i / 240.0, an, al)
        curva.append("%s %s" % (_n(m + x), _n(m + al - y)))
    trazo = ('<path d="M%s" fill="none" stroke="currentColor" stroke-width="1" '
             'stroke-opacity=".18"/>' % ("L".join(curva)))

    marcas, rotulos = [], []
    for i, f in enumerate(fases):
        t = (i + 0.5) / n
        x, y = arco_punto(t, an, al)
        px, py = m + x, m + al - y
        dur = f.get("min") or 0
        r = 3.0 + 9.0 * (dur / tope if tope else 0)
        decide = f.get("n") in decisivas
        clase = "dib__p dib__p--decide" if decide else "dib__p"
        marcas.append('<circle cx="%s" cy="%s" r="%s" class="%s"/>'
                      % (_n(px), _n(py), _n(r), clase))
        # el rótulo sale hacia fuera del arco, siguiendo la normal
        x2, y2 = arco_punto(min(1.0, t + 0.02), an, al)
        x1, y1 = arco_punto(max(0.0, t - 0.02), an, al)
        dx, dy = (x2 - x1), -(y2 - y1)
        largo = math.hypot(dx, dy) or 1
        nx, ny = -dy / largo, dx / largo         # normal hacia fuera
        if ny > 0:
            nx, ny = -nx, -ny
        # El arco es casi plano por abajo, y ahí la perpendicular apunta recto
        # hacia el suelo: los rótulos de las fases centrales se apilaban unos
        # encima de otros. Se sacan en dos anillos, uno corto y otro largo, de
        # modo que las fases pares y las impares no compiten por el mismo sitio.
        # y donde el arco es más plano —abajo— se separan un poco más, que es
        # justo donde la perpendicular deja de abrir en abanico
        plano = 1.0 - abs(nx)
        fuera_r = r + 26 + plano * 20 + (0 if i % 2 == 0 else 64)
        fx, fy = px + nx * fuera_r, py + ny * fuera_r
        anclaje = "middle" if abs(nx) < 0.35 else ("end" if nx < 0 else "start")
        marcas.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="currentColor" '
                      'stroke-width="1" stroke-opacity=".2"/>'
                      % (_n(px + nx * (r + 3)), _n(py + ny * (r + 3)),
                         _n(px + nx * (fuera_r - 13)), _n(py + ny * (fuera_r - 13))))
        rotulos.append(
            '<g class="dib__g%s">%s%s</g>'
            % (" dib__g--decide" if decide else "",
               _texto(fx, fy, "%02d" % (f.get("n") or i + 1), 12, anclaje, "dib__n"),
               _texto(fx, fy + 15, (f.get("label") or "")[:26], 11.5, anclaje, "dib__r")
               + (_texto(fx, fy + 30, "%d min" % dur, 10.5, anclaje, "dib__m") if dur else "")))

    return ('<svg class="dib dib--arco" viewBox="0 0 %d %d" role="img" '
            'aria-label="Las catorce fases del recorrido del paciente sobre el arco dental">'
            '%s%s%s</svg>'
            % (ancho, alto, trazo, "".join(marcas), "".join(rotulos)))


# --------------------------------------------------------------------------
#  2 · El puente, en cascada
# --------------------------------------------------------------------------
def cascada(tramos, objetivo, ancho=1200, alto=520):
    """De lo heredado al objetivo, bloque a bloque.

    «tramos» es una lista de (rótulo, valor): el primero es el punto de
    partida y los demás, lo que suma cada palanca. Una barra por bloque decía
    cuánto aporta cada uno; una cascada dice además dónde queda el total
    después de cada uno, que es la pregunta que se hace de verdad.
    """
    if not tramos:
        return ""
    izq, der, arr, aba = 150.0, 40.0, 56.0, 92.0
    an, al = ancho - izq - der, alto - arr - aba
    acum, alturas = 0.0, []
    for r, v in tramos:
        alturas.append((r, acum, acum + v, v))
        acum += v
    tope = max(objetivo, acum) * 1.06
    hueco = an / len(tramos)
    ancho_b = hueco * 0.46

    def yy(v):
        return arr + al - (v / tope) * al

    piezas, hilo = [], []
    for i, (r, base, cima, v) in enumerate(alturas):
        cx = izq + hueco * (i + 0.5)
        x = cx - ancho_b / 2
        y0, y1 = yy(base), yy(cima)
        piezas.append('<rect x="%s" y="%s" width="%s" height="%s" class="dib__b%s"/>'
                      % (_n(x), _n(y1), _n(ancho_b), _n(max(1.0, y0 - y1)),
                         " dib__b--base" if i == 0 else ""))
        piezas.append(_texto(cx, y1 - 14, "{:,}".format(int(v)).replace(",", ".") + " €",
                             13, "middle", "dib__v"))
        piezas.append(_texto(cx, arr + al + 26, r[:22], 11.5, "middle", "dib__r"))
        piezas.append(_texto(cx, arr + al + 44, "acumulado " +
                             "{:,}".format(int(cima)).replace(",", ".") + " €",
                             10.5, "middle", "dib__m"))
        hilo.append((cx + ancho_b / 2, yy(cima)))
        if i + 1 < len(alturas):
            sx = izq + hueco * (i + 1.5) - ancho_b / 2
            piezas.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="currentColor" '
                          'stroke-width="1" stroke-opacity=".26" stroke-dasharray="3 3"/>'
                          % (_n(cx + ancho_b / 2), _n(yy(cima)), _n(sx), _n(yy(cima))))

    # la línea del objetivo, que es contra lo que se mide todo
    yo = yy(objetivo)
    piezas.append('<line x1="%s" y1="%s" x2="%s" y2="%s" class="dib__meta"/>'
                  % (_n(izq - 60), _n(yo), _n(ancho - der), _n(yo)))
    piezas.append(_texto(izq - 68, yo - 8, "Objetivo", 11, "end", "dib__r"))
    piezas.append(_texto(izq - 68, yo + 10,
                         "{:,}".format(int(objetivo)).replace(",", ".") + " €",
                         12.5, "end", "dib__v"))
    # la base
    piezas.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="currentColor" '
                  'stroke-width="1" stroke-opacity=".3"/>'
                  % (_n(izq - 60), _n(arr + al), _n(ancho - der), _n(arr + al)))

    return ('<svg class="dib dib--cascada" viewBox="0 0 %d %d" role="img" '
            'aria-label="El puente de lo heredado al objetivo, bloque a bloque">%s</svg>'
            % (ancho, alto, "".join(piezas)))


# --------------------------------------------------------------------------
#  3 · Quién hace qué, en puntos
# --------------------------------------------------------------------------
PESO = {"R/A": 1.0, "R": .82, "A": .66, "C": .42, "I": .26, "—": 0.0}


def rejilla(puestos, columnas, celda, ancho=1200):
    """Las catorce fases contra los seis puestos, en puntos.

    «celda(puesto, columna)» devuelve el papel: R/A, R, A, C, I o «—». Una
    tabla de letras obliga a leer ochenta y cuatro casillas para ver el
    reparto; un punto por casilla lo enseña de un vistazo, y la letra sigue
    ahí para quien la quiera.
    """
    izq, arr = 190.0, 58.0
    paso = (ancho - izq - 30) / max(1, len(columnas))
    alto = arr + len(puestos) * 42 + 30
    piezas = []
    for j, c in enumerate(columnas):
        cx = izq + paso * (j + 0.5)
        piezas.append(_texto(cx, arr - 22, str(c), 11, "middle", "dib__m"))
    for i, p in enumerate(puestos):
        cy = arr + 42 * i + 21
        piezas.append(_texto(izq - 18, cy + 4, p, 12.5, "end", "dib__r"))
        piezas.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="currentColor" '
                      'stroke-width="1" stroke-opacity=".08"/>'
                      % (_n(izq - 6), _n(cy + 21), _n(ancho - 30), _n(cy + 21)))
        for j, c in enumerate(columnas):
            cx = izq + paso * (j + 0.5)
            papel = celda(p, c) or "—"
            w = PESO.get(papel, 0.0)
            if w <= 0:
                piezas.append('<circle cx="%s" cy="%s" r="1.6" class="dib__o"/>'
                              % (_n(cx), _n(cy)))
                continue
            r = 4.5 + 7.5 * w
            clase = "dib__c dib__c--manda" if papel in ("R/A", "R") else "dib__c"
            piezas.append('<circle cx="%s" cy="%s" r="%s" class="%s"><title>%s · %s</title>'
                          '</circle>' % (_n(cx), _n(cy), _n(r), clase, escape(p), escape(papel)))
    return ('<svg class="dib dib--rejilla" viewBox="0 0 %d %d" role="img" '
            'aria-label="Quién hace qué en cada fase del recorrido">%s</svg>'
            % (ancho, int(alto), "".join(piezas)))


# --------------------------------------------------------------------------
#  La hoja de estilos de las figuras
# --------------------------------------------------------------------------
CSS = """
/* ====================================================================
   LAS CIFRAS, DIBUJADAS
   Un solo lenguaje para todas: trazo fino, blanco, negro y el azul solo
   para lo que decide. Las figuras se dibujan con «currentColor», así
   que heredan el color del sitio y no traen ninguno propio.
   ==================================================================== */
.dib{display:block;width:100%;height:auto;color:var(--negro);overflow:visible}
.dib__t{font-family:var(--f-mono);fill:var(--muted);letter-spacing:.08em}
.dib__r{fill:var(--ink-2);font-family:var(--f-body);letter-spacing:0}
.dib__n{fill:var(--negro);letter-spacing:.1em}
.dib__m{fill:var(--muted);letter-spacing:.14em}
.dib__v{fill:var(--negro);font-family:var(--f-mono);letter-spacing:.02em}
.dib__g--decide .dib__n,.dib__g--decide .dib__r{fill:var(--azul)}
.dib__p{fill:var(--blanco);stroke:currentColor;stroke-width:1.2}
.dib__p--decide{fill:var(--azul);stroke:var(--azul)}
.dib__b{fill:var(--negro)}
.dib__b--base{fill:var(--linea)}
.dib__meta{stroke:var(--azul);stroke-width:1.2;stroke-dasharray:6 4}
.dib__c{fill:var(--linea);stroke:none}
.dib__c--manda{fill:var(--azul)}
.dib__o{fill:var(--linea)}
/* al pasar por encima, la fila que se mira se separa del resto */
.dib--rejilla .dib__c{transition:opacity .2s var(--e)}
.dib--rejilla:hover .dib__c{opacity:.35}
.dib--rejilla .dib__c:hover{opacity:1}
.dibcaja{margin:2.4rem 0 0}
.dibpie{margin:1.4rem 0 0;font-size:.92rem;line-height:1.75;color:var(--ink-2);max-width:72ch}
.dibpie b{color:var(--negro);font-weight:400}
.dibleyenda{display:flex;flex-wrap:wrap;gap:.7rem 2rem;margin:1.6rem 0 0;
  font-family:var(--f-mono);font-size:.62rem;letter-spacing:.14em;
  text-transform:uppercase;color:var(--muted)}
.dibleyenda i{display:inline-flex;align-items:center;gap:.5rem;font-style:normal}
.dibleyenda i::before{content:"";width:.6rem;height:.6rem;border-radius:50%;
  background:var(--linea)}
.dibleyenda i.es-azul::before{background:var(--azul)}
.dibleyenda i.es-hueco::before{background:var(--blanco);box-shadow:0 0 0 1px var(--negro)}
/* una nota de lectura no lleva muestra de color: no nombra nada del dibujo */
.dibleyenda i.es-nota::before{display:none}
@media(max-width:900px){
  .dib--arco,.dib--rejilla{min-width:46rem}
  .dibcaja{overflow-x:auto}
}
"""


def muestra():
    fs = [{"n": i, "label": l, "min": m} for i, (l, m) in enumerate(
        [("Preparación", 6), ("Recepción", 5), ("Anamnesis", 8), ("Historial", 5),
         ("Pruebas", 12), ("Briefing", 6), ("Exploración", 15), ("IAC", 10),
         ("Presentación", 18), ("Cierre", 20), ("Agenda", 8), ("Salida", 6),
         ("Postvisita", 2), ("Mantenimiento", 2)], 1)]
    tr = [("Punto de partida", 720000), ("Llenar la agenda", 96479),
          ("Mejor mezcla", 210000), ("Seguimiento", 130000)]
    puestos = ["Dirección", "Doctor", "Recepción", "RAC", "Auxiliar", "Higienista"]
    cols = ["%02d" % i for i in range(1, 15)]
    import random
    random.seed(3)
    papeles = ["R/A", "R", "A", "C", "I", "—"]
    tabla = {(p, c): random.choice(papeles) for p in puestos for c in cols}
    html = ("<!doctype html><meta charset=utf-8><title>Las cifras, dibujadas</title>"
            "<style>body{margin:0;padding:3rem;font-family:system-ui;background:#fff;"
            "--negro:#0B0B0F;--ink-2:#4E4E5A;--muted:#84848F;--linea:#E3E3E9;"
            "--blanco:#fff;--azul:#1E3AD1;--f-mono:ui-monospace,monospace;"
            "--f-body:system-ui;--e:ease}"
            + CSS + "</style>"
            + "<h2>El recorrido</h2>" + arco(fs)
            + "<h2>El puente</h2>" + cascada(tr, 1200000)
            + "<h2>Quién hace qué</h2>"
            + rejilla(puestos, cols, lambda p, c: tabla[(p, c)]))
    (RAIZ / "muestra-datos.html").write_text(html, encoding="utf-8")
    print("  → muestra-datos.html")


if __name__ == "__main__":
    if "--muestra" in sys.argv:
        muestra()
    else:
        print("las cifras, dibujadas · arco(), cascada() y rejilla()")
