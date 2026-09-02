# -*- coding: utf-8 -*-
"""Figura F7: valor de empresa por peldaño de la escalera.

Se ejecuta desde build.py; también se puede lanzar suelto. Escribe en
fuentes/ los bloques que después ensambla el generador del Plan de Dirección.
"""
import pathlib

RAIZ = pathlib.Path(__file__).resolve().parent.parent
FUENTES = RAIZ / "fuentes"

SALIDA = FUENTES / "figuras-7.html"
# rampa secuencial: la misma familia del mapa de calor, lightness monótona
RAMPA = ["#C6E9E4", "#A3D8D1", "#66BDB3", "#2A9C91", "#00857A"]


def txt(x, y, s, anchor="start", size=12, weight=400, color="var(--ink-2)"):
    return ('<text x="%s" y="%s" text-anchor="%s" font-size="%s" font-weight="%s" '
            'fill="%s" font-family="var(--f-body)">%s</text>' % (x, y, anchor, size, weight, color, s))


def mono(x, y, s, anchor="start", size=11, color="var(--muted)"):
    return ('<text x="%s" y="%s" text-anchor="%s" font-size="%s" fill="%s" '
            'font-family="var(--f-mono)" letter-spacing=".04em">%s</text>' % (x, y, anchor, size, color, s))


def mil(v):
    return "{:,}".format(int(round(v))).replace(",", ".")


def escalera():
    EBITDA = 180                      # miles de € · hipótesis de trabajo
    niveles = [
        ("Nivel 1", "Beneficio, dependiente del titular", 3.0, 4.0),
        ("Nivel 2", "Beneficio sin dependencia", 4.5, 5.5),
        ("Nivel 3", "Con ingreso recurrente contratado", 5.5, 6.5),
        ("Nivel 4", "Sistema replicable demostrado", 6.5, 8.0),
        ("Nivel 5", "Con serie clínica propia a 5 años", 8.0, 10.0),
    ]
    W, H = 880, 366
    ox, oy, aw = 132, 62, 620
    fila = 58
    maxv = EBITDA * 10.0
    p = ['<svg viewBox="0 0 %d %d" width="%d" height="%d" role="img" style="max-width:100%%;height:auto" '
         'aria-label="Valor de empresa por nivel de la escalera con el mismo EBITDA de 180 mil euros: '
         'del rango de 540 a 720 mil euros en el nivel 1 al rango de 1.440 a 1.800 en el nivel 5.">'
         % (W, H, W, H)]
    # rejilla vertical en millones
    for v in range(0, 1801, 300):
        x = ox + aw * v / maxv
        p.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="var(--line-soft)" stroke-width="1"/>'
                 % (x, oy - 10, x, oy + fila * len(niveles) - 14))
        p.append(mono(x, oy - 18, mil(v), anchor="middle", size=10))
    p.append(mono(ox, 24, "valor de empresa · miles de € · EBITDA constante de 180 k€", anchor="start"))

    for i, (rotulo, glosa, bajo, alto) in enumerate(niveles):
        y = oy + fila * i
        x1 = ox + aw * (EBITDA * bajo) / maxv
        x2 = ox + aw * (EBITDA * alto) / maxv
        p.append(mono(ox - 14, y + 10, rotulo, anchor="end", size=11, color="var(--ink-2)"))
        p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="20" fill="%s" rx="3"/>'
                 % (x1, y, x2 - x1, RAMPA[i]))
        # extremos del rango
        for x in (x1, x2):
            p.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="var(--ink)" '
                     'stroke-width="1" opacity=".35"/>' % (x, y - 3, x, y + 23))
        p.append(txt(x2 + 12, y + 15, "%s – %s" % (mil(EBITDA * bajo), mil(EBITDA * alto)),
                     size=12, weight=600, color="var(--ink)"))
        p.append(txt(ox + 6, y + 40, "%s  ·  múltiplo %s–%s×" % (glosa, str(bajo).replace(".", ","),
                                                                str(alto).replace(".", ",")),
                     size=11, color="var(--muted)"))
    p.append("</svg>")
    return "\n".join(p)


SALIDA.write_text("<!--F7-->\n" + escalera() + "\n", encoding="utf-8")
print("F7:", SALIDA.stat().st_size, "bytes")
