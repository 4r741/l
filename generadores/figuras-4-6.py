# -*- coding: utf-8 -*-
"""Figuras F4 a F6: escenarios a 36 meses, sensibilidad y valor acumulado.

Se ejecuta desde build.py; también se puede lanzar suelto. Escribe en
fuentes/ los bloques que después ensambla el generador del Plan de Dirección.
"""
import pathlib

RAIZ = pathlib.Path(__file__).resolve().parent.parent
FUENTES = RAIZ / "fuentes"

TEAL = "#0E8F84"
OCRE = "#A8631B"
MORA = "#7A4FA3"
SALIDA = FUENTES / "figuras-4-6.html"


def txt(x, y, s, anchor="start", size=12, weight=400, color="var(--ink-2)"):
    return ('<text x="%s" y="%s" text-anchor="%s" font-size="%s" font-weight="%s" '
            'fill="%s" font-family="var(--f-body)">%s</text>' % (x, y, anchor, size, weight, color, s))


def mono(x, y, s, anchor="start", size=11, color="var(--muted)"):
    return ('<text x="%s" y="%s" text-anchor="%s" font-size="%s" fill="%s" '
            'font-family="var(--f-mono)" letter-spacing=".04em">%s</text>' % (x, y, anchor, size, color, s))


def mil(v):
    return ("{:,}".format(int(v))).replace(",", ".")


# ------------------------------------------------------------------ F4
def escenarios():
    """Tres trayectorias de facturación anual a 36 meses."""
    W, H = 880, 380
    ox, oy, aw, ah = 78, 54, 760, 236
    series = [
        ("Base · solo sostener", TEAL, [720, 745, 770]),
        ("Objetivo · sistema en marcha", OCRE, [790, 980, 1150]),
        ("Ambición · red y líneas nuevas", MORA, [840, 1180, 1650]),
    ]
    hitos = ["Mes 12", "Mes 24", "Mes 36"]
    maxv = 1800
    grupo = aw / 3
    bw = 62
    p = ['<svg viewBox="0 0 %d %d" width="%d" height="%d" role="img" style="max-width:100%%;height:auto" '
         'aria-label="Tres trayectorias de facturación anual a 36 meses: base de 720 a 770 mil euros, objetivo de 790 a 1.150 y ambición de 840 a 1.650.">' % (W, H, W, H)]
    for v in range(0, 1801, 300):
        y = oy + ah - ah * v / maxv
        p.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="var(--line-soft)" stroke-width="1"/>' % (ox, y, ox + aw, y))
        p.append(mono(ox - 12, y + 4, mil(v), anchor="end"))
    for g, hito in enumerate(hitos):
        cx = ox + grupo * g + grupo / 2
        for s, (nombre, color, valores) in enumerate(series):
            v = valores[g]
            h = ah * v / maxv
            x = cx - (len(series) * (bw + 6)) / 2 + s * (bw + 6)
            y = oy + ah - h
            p.append('<rect x="%.1f" y="%.1f" width="%d" height="%.1f" fill="%s" rx="4" ry="4"/>' % (x, y, bw, h, color))
            p.append(txt(x + bw / 2, y - 8, mil(v), anchor="middle", size=12, weight=600, color="var(--ink)"))
        p.append(mono(cx, oy + ah + 24, hito, anchor="middle", size=11, color="var(--ink-2)"))
    p.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="var(--line)" stroke-width="1"/>' % (ox, oy + ah, ox + aw, oy + ah))
    p.append(mono(ox - 12, 22, "facturación anual · miles de €", anchor="start"))
    lx, ly = ox, H - 18
    for nombre, color, _ in series:
        p.append('<rect x="%.0f" y="%d" width="12" height="12" rx="3" fill="%s"/>' % (lx, ly - 10, color))
        p.append(txt(lx + 19, ly, nombre, size=12))
        lx += 34 + len(nombre) * 6.5
    p.append("</svg>")
    return "\n".join(p)


# ------------------------------------------------------------------ F5
def sensibilidad():
    """Matriz conversión × ticket medio. Rampa secuencial de un solo tono."""
    W, H = 880, 282
    ox, oy = 190, 74
    cw, ch = 148, 52
    conversiones = [0.30, 0.40, 0.50, 0.60]
    tickets = [1400, 1800, 2200]
    pv_dia, dias = 4, 21           # capacidad: 4 primeras visitas al día
    # rampa secuencial teal: claro → oscuro, lightness monótona
    # rampa clara: la lightness sube de forma monótona y el texto se lee
    # siempre en tinta oscura, sin cambio de color a mitad de escala
    rampa = ["#E6F3F1", "#C9E7E3", "#A7D9D3", "#82C8C0", "#57B3A9", "#2FA398"]
    p = ['<svg viewBox="0 0 %d %d" width="%d" height="%d" role="img" style="max-width:100%%;height:auto" '
         'aria-label="Facturación anual estimada según tasa de conversión y ticket medio, de 353 mil a 1,3 millones de euros.">' % (W, H, W, H)]
    valores = []
    for t in tickets:
        fila = []
        for c in conversiones:
            fila.append(pv_dia * c * t * dias * 12 / 1000.0)
        valores.append(fila)
    plano = [v for fila in valores for v in fila]
    vmin, vmax = min(plano), max(plano)
    for j, c in enumerate(conversiones):
        p.append(mono(ox + cw * j + cw / 2, oy - 14, "%d %%" % (c * 100), anchor="middle", size=11, color="var(--ink-2)"))
    p.append(mono(ox + cw * len(conversiones) / 2, oy - 40, "tasa de conversión de la primera visita", anchor="middle", size=11))
    for i, t in enumerate(tickets):
        y = oy + ch * i
        p.append(mono(ox - 16, y + ch / 2 + 4, "%s €" % mil(t), anchor="end", size=11, color="var(--ink-2)"))
        for j, c in enumerate(conversiones):
            v = valores[i][j]
            paso = int(round((v - vmin) / (vmax - vmin) * (len(rampa) - 1)))
            x = ox + cw * j
            p.append('<rect x="%d" y="%d" width="%d" height="%d" fill="%s" stroke="var(--surface)" stroke-width="2"/>'
                     % (x, y, cw, ch, rampa[paso]))
            p.append(txt(x + cw / 2, y + ch / 2 + 5, mil(round(v)) + " k€", anchor="middle", size=13, weight=600, color="#0B1A20"))
    p.append(mono(24, oy + ch * len(tickets) / 2, "ticket", anchor="start", size=11))
    p.append(mono(24, oy + ch * len(tickets) / 2 + 16, "medio", anchor="start", size=11))
    p.append(mono(ox, oy + ch * len(tickets) + 30, "Capacidad fija: 4 primeras visitas al día · 21 días · 12 meses", anchor="start", size=10))
    p.append("</svg>")
    return "\n".join(p)


# ------------------------------------------------------------------ F6
def valor_acumulado():
    """Valor acumulado por paciente a lo largo de cinco años, con y sin programa."""
    W, H = 880, 360
    ox, oy, aw, ah = 78, 46, 740, 230
    anios = [0, 1, 2, 3, 4, 5]
    sin_p = [720, 720, 745, 745, 770, 770]
    con_p = [720, 905, 1090, 1275, 1460, 1653]
    maxv = 1800
    def px(i):
        return ox + aw * i / (len(anios) - 1)
    def py(v):
        return oy + ah - ah * v / maxv
    p = ['<svg viewBox="0 0 %d %d" width="%d" height="%d" role="img" style="max-width:100%%;height:auto" '
         'aria-label="Valor acumulado por paciente a cinco años: 770 euros sin programa de cuidado y 1.653 con él.">' % (W, H, W, H)]
    for v in range(0, 1801, 300):
        y = py(v)
        p.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="var(--line-soft)" stroke-width="1"/>' % (ox, y, ox + aw, y))
        p.append(mono(ox - 12, y + 4, mil(v), anchor="end"))
    for i, a in enumerate(anios):
        p.append(mono(px(i), oy + ah + 24, "año %d" % a if a else "alta", anchor="middle", size=11, color="var(--ink-2)"))
    # área de diferencia
    area = " ".join("%.1f,%.1f" % (px(i), py(con_p[i])) for i in range(len(anios)))
    area += " " + " ".join("%.1f,%.1f" % (px(i), py(sin_p[i])) for i in range(len(anios) - 1, -1, -1))
    p.append('<polygon points="%s" fill="%s" opacity=".10"/>' % (area, TEAL))
    for valores, color, etiqueta in ((sin_p, OCRE, "Sin programa de cuidado"), (con_p, TEAL, "Con programa de cuidado")):
        d = " ".join(("M" if i == 0 else "L") + "%.1f %.1f" % (px(i), py(v)) for i, v in enumerate(valores))
        p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2" stroke-linejoin="round"/>' % (d, color))
        for i, v in enumerate(valores):
            p.append('<circle cx="%.1f" cy="%.1f" r="4" fill="%s" stroke="var(--surface)" stroke-width="2"/>' % (px(i), py(v), color))
        p.append(txt(px(len(valores) - 1) + 12, py(valores[-1]) + 5, mil(valores[-1]) + " €", size=13, weight=600, color="var(--ink)"))
    p.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="var(--line)" stroke-width="1"/>' % (ox, oy + ah, ox + aw, oy + ah))
    p.append(mono(ox - 12, 20, "valor acumulado por paciente · €", anchor="start"))
    lx, ly = ox, H - 16
    for etiqueta, color in (("Con programa de cuidado", TEAL), ("Sin programa de cuidado", OCRE)):
        p.append('<rect x="%.0f" y="%d" width="12" height="12" rx="3" fill="%s"/>' % (lx, ly - 10, color))
        p.append(txt(lx + 19, ly, etiqueta, size=12))
        lx += 34 + len(etiqueta) * 6.6
    p.append("</svg>")
    return "\n".join(p)


SALIDA.write_text("<!--F4-->\n" + escenarios() + "\n<!--F5-->\n" + sensibilidad() +
                  "\n<!--F6-->\n" + valor_acumulado() + "\n", encoding="utf-8")
print("figuras nuevas:", SALIDA.stat().st_size, "bytes")
