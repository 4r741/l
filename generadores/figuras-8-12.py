# -*- coding: utf-8 -*-
"""Figuras F8 a F12, derivadas del modelo de campañas.

Se ejecuta desde build.py; también se puede lanzar suelto. Escribe en
fuentes/ los bloques que después ensambla el generador del Plan de Dirección.
"""
import pathlib

RAIZ = pathlib.Path(__file__).resolve().parent.parent
FUENTES = RAIZ / "fuentes"
import importlib.util

spec = importlib.util.spec_from_file_location("modelo", RAIZ / "modelo-campanas.py")
modelo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(modelo)
D = modelo.calcula()

SALIDA = FUENTES / "figuras-8-12.html"
TEAL, OCRE, MORA, TINTA = "#00857A", "#C25A12", "#0B3B45", "#080B0A"


def txt(x, y, s, anchor="start", size=12, weight=400, color="var(--ink-2)"):
    return ('<text x="%s" y="%s" text-anchor="%s" font-size="%s" font-weight="%s" '
            'fill="%s" font-family="var(--f-body)">%s</text>' % (x, y, anchor, size, weight, color, s))


def mono(x, y, s, anchor="start", size=11, color="var(--muted)"):
    return ('<text x="%s" y="%s" text-anchor="%s" font-size="%s" fill="%s" '
            'font-family="var(--f-mono)" letter-spacing=".04em">%s</text>' % (x, y, anchor, size, color, s))


def mil(v):
    """Miles con punto y signo menos tipográfico, no guion."""
    return "{:,}".format(int(round(v))).replace(",", ".").replace("-", "\u2212")


def envolver(texto, ancho):
    palabras, linea, lineas = texto.split(), "", []
    for w in palabras:
        if len(linea + " " + w) > ancho:
            lineas.append(linea); linea = w
        else:
            linea = (linea + " " + w).strip()
    lineas.append(linea)
    return lineas


# ------------------------------------------------------------------ F8 · puente
def puente():
    p_ = D["puente"]
    pasos = [
        ("Heredado", "3,5 primeras visitas al día", p_["base"] / 1000, "total"),
        ("Llenar la agenda", "Hasta las 4 que caben", p_["llenar"] / 1000, "suma"),
        ("Mejor mezcla", "Siete campañas de agenda", p_["mezcla"] / 1000, "suma"),
        ("Seguimiento", "Las dos de fuera del embudo", p_["seguimiento"] / 1000, "suma"),
        ("Colchón", "No ejecución (%.0f %%)" % (p_["colchon_pct"] * 100), -(-p_["colchon"]) / 1000, "resta"),
        ("Objetivo", "Facturación anual", p_["objetivo"] / 1000, "total"),
    ]
    W, H = 900, 400
    ox, oy, aw, ah = 68, 62, 806, 250
    maxv = 1500
    ancho = aw / len(pasos) - 22
    p = ['<svg viewBox="0 0 %d %d" width="%d" height="%d" role="img" style="max-width:100%%;height:auto" '
         'aria-label="Puente de facturación: 720 mil euros heredados, más 96 de llenar la agenda, más 204 '
         'de mejor mezcla y 343 de seguimiento, menos 163 de colchón, hasta el objetivo de 1,2 millones.">'
         % (W, H, W, H)]

    def y(v):
        return oy + ah - ah * v / maxv

    for v in range(0, 1501, 300):
        p.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="var(--line-soft)" stroke-width="1"/>'
                 % (ox, y(v), ox + aw, y(v)))
        p.append(mono(ox - 12, y(v) + 4, mil(v), anchor="end", size=10))
    p.append(mono(ox - 12, 22, "facturación anual · miles de €", anchor="start"))

    acumulado = 0
    for i, (rotulo, glosa, valor, clase) in enumerate(pasos):
        x = ox + (aw / len(pasos)) * i + 11
        if clase == "total":
            base, alto, color = valor, ah * valor / maxv, TINTA
            acumulado = valor
        elif clase == "suma":
            base = acumulado + valor
            alto, color = ah * valor / maxv, TEAL
            acumulado = base
        else:
            base, alto, color = acumulado, ah * abs(valor) / maxv, OCRE
            acumulado += valor
        p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" rx="3"/>'
                 % (x, y(base), ancho, alto, color))
        signo = "+" if clase == "suma" else "−" if clase == "resta" else ""
        p.append(txt(x + ancho / 2, y(base) - 9, signo + mil(abs(valor)), anchor="middle",
                     size=12.5, weight=600, color="var(--ink)"))
        p.append(mono(x + ancho / 2, oy + ah + 22, rotulo, anchor="middle", size=10, color="var(--ink-2)"))
        for k, l in enumerate(envolver(glosa, 22)):
            p.append(txt(x + ancho / 2, oy + ah + 40 + k * 13, l, anchor="middle", size=9.5,
                         color="var(--muted)"))
        if i < len(pasos) - 1:
            nivel = acumulado if clase != "total" or i == 0 else acumulado
            p.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="var(--rule)" '
                     'stroke-width="1" stroke-dasharray="4 3" opacity=".55"/>'
                     % (x + ancho, y(nivel), x + aw / len(pasos) + 11, y(nivel)))
    p.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="var(--line)" stroke-width="1"/>'
             % (ox, y(0), ox + aw, y(0)))
    p.append("</svg>")
    return "\n".join(p)


# ------------------------------------------------------------------ F9 · calendario
def calendario():
    MESES = ["E", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]
    RITMO = {
        "C1": [1] * 12,
        "C2": [2, 1, 1, 0, 0, 0, 0, 0, 2, 1, 1, 0],
        "C3": [0, 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
        "C4": [0, 0, 0, 0, 0, 2, 1, 0, 1, 1, 1, 1],
        "C5": [0, 0, 0, 2, 1, 1, 0, 0, 0, 0, 0, 0],
        "C6": [0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 1],
        "C7": [0, 0, 0, 0, 2, 1, 1, 0, 0, 0, 0, 0],
        "C8": [1] * 12,
        "C9": [1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1],
    }
    COLORES = {0: "#F2F4F3", 1: "#A3D8D1", 2: "#00857A"}
    campanas = sorted(D["campanas"], key=lambda f: f["cod"])
    W = 900
    ox, oy, cw, ch = 292, 62, 44, 30
    H = oy + ch * len(campanas) + 96
    p = ['<svg viewBox="0 0 %d %d" width="%d" height="%d" role="img" style="max-width:100%%;height:auto" '
         'aria-label="Calendario de las nueve campañas a lo largo de doce meses, con el mes de arranque, '
         'los de sostenimiento y el aporte anual de cada una.">' % (W, H, W, H)]
    for j, m in enumerate(MESES):
        p.append(mono(ox + cw * j + cw / 2, oy - 14, m, anchor="middle", size=11, color="var(--ink-2)"))
    p.append(mono(ox, oy - 34, "meses del ejercicio", anchor="start", size=10))
    p.append(mono(ox + cw * 12 + 16, oy - 14, "k€/año", anchor="start", size=10))
    for i, f in enumerate(campanas):
        y = oy + ch * i
        p.append(txt(ox - 16, y + ch / 2 + 4, "%s · %s" % (f["cod"], f["nombre"]), anchor="end",
                     size=11.5, color="var(--ink)"))
        for j, estado in enumerate(RITMO[f["cod"]]):
            p.append('<rect x="%d" y="%d" width="%d" height="%d" fill="%s" stroke="var(--surface)" '
                     'stroke-width="2" rx="2"/>' % (ox + cw * j, y + 2, cw, ch - 4, COLORES[estado]))
        v = f["aporte"] / 1000
        p.append(txt(ox + cw * 12 + 16, y + ch / 2 + 4, ("−" if v < 0 else "") + mil(abs(v)),
                     size=12, weight=600, color=OCRE if v < 0 else "var(--ink)"))
    total = sum(f["aporte"] for f in campanas) / 1000
    yb = oy + ch * len(campanas)
    p.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="var(--line)" stroke-width="1"/>'
             % (ox + cw * 12 + 16, yb + 6, W - 16, yb + 6))
    p.append(txt(ox + cw * 12 + 16, yb + 26, mil(total), size=13, weight=600, color=TEAL))
    p.append(mono(ox - 16, yb + 26, "Cartera completa, antes del colchón", anchor="end", size=10))
    ly = H - 34
    for k, (estado, rotulo) in enumerate(((2, "Arranque"), (1, "Sostenimiento"), (0, "Inactiva"))):
        x = ox + k * 150
        p.append('<rect x="%d" y="%d" width="14" height="14" fill="%s" rx="2" stroke="var(--line)"/>'
                 % (x, ly - 11, COLORES[estado]))
        p.append(txt(x + 20, ly, rotulo, size=11))
    p.append(mono(ox - 16, ly, "Nunca más de dos arranques a la vez", anchor="end", size=10))
    p.append("</svg>")
    return "\n".join(p)


# ------------------------------------------------------------------ F10 · composición
def composicion():
    p_, c_ = D["puente"], D["capacidad"]
    hoy = p_["base"] / 1000
    pv_final = (p_["base"] + p_["llenar"] + p_["mezcla"]) / 1000
    seguimiento = p_["seguimiento"] / 1000
    W, H = 880, 320
    ox, oy, ah = 150, 52, 196
    maxv = 1500
    bw = 128
    p = ['<svg viewBox="0 0 %d %d" width="%d" height="%d" role="img" style="max-width:100%%;height:auto" '
         'aria-label="Composición: hoy 720 mil euros, todos de primera visita; en el plan 1.020 de primera '
         'visita y 343 de seguimiento, antes del colchón.">' % (W, H, W, H)]

    def y(v):
        return oy + ah - ah * v / maxv

    for v in range(0, 1501, 300):
        p.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="var(--line-soft)" stroke-width="1"/>'
                 % (ox - 30, y(v), ox + 400, y(v)))
        p.append(mono(ox - 42, y(v) + 4, mil(v), anchor="end", size=10))
    p.append(mono(ox - 42, 20, "facturación anual · miles de €", anchor="start"))
    barras = [("Hoy", [(hoy, TEAL)]), ("Planificado", [(pv_final, TEAL), (seguimiento, OCRE)])]
    for i, (rotulo, trozos) in enumerate(barras):
        x = ox + i * 240
        acumulado = 0
        for valor, color in trozos:
            alto = ah * valor / maxv
            p.append('<rect x="%d" y="%.1f" width="%d" height="%.1f" fill="%s" rx="3"/>'
                     % (x, y(acumulado + valor), bw, alto, color))
            p.append(txt(x + bw / 2, y(acumulado + valor) + alto / 2 + 5, mil(valor),
                         anchor="middle", size=12, weight=600, color="#FFFFFF"))
            acumulado += valor
        p.append(txt(x + bw / 2, y(acumulado) - 12, mil(acumulado) + " k€", anchor="middle",
                     size=13, weight=600, color="var(--ink)"))
        p.append(mono(x + bw / 2, oy + ah + 24, rotulo, anchor="middle", size=11, color="var(--ink-2)"))
    lx, ly = ox + 420, oy + 22
    for nombre, color in (("Primera visita", TEAL), ("Seguimiento y recurrente", OCRE)):
        p.append('<rect x="%d" y="%d" width="12" height="12" rx="3" fill="%s"/>' % (lx, ly - 10, color))
        p.append(txt(lx + 19, ly, nombre, size=11.5))
        ly += 24
    for k, l in enumerate(["El bloque de primera visita crece un 42 %,",
                           "y de ese crecimiento dos tercios son mezcla,",
                           "no volumen. El seguimiento parte de cero:",
                           "es el único bloque enteramente nuevo."]):
        p.append(txt(lx, ly + 12 + k * 18, l, size=11.5, color="var(--ink)"))
    p.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="var(--line)" stroke-width="1"/>'
             % (ox - 30, y(0), ox + 400, y(0)))
    p.append("</svg>")
    return "\n".join(p)


# ------------------------------------------------------------------ F11 · retorno
def retorno():
    filas = sorted([f for f in D["campanas"]], key=lambda f: -(f["retorno"] or -99))
    W = 900
    ox, oy, ah = 300, 60, 34
    H = oy + ah * len(filas) + 78
    maxr = max(f["retorno"] for f in filas if f["retorno"])
    aw = 380
    p = ['<svg viewBox="0 0 %d %d" width="%d" height="%d" role="img" style="max-width:100%%;height:auto" '
         'aria-label="Retorno de cada campaña: aporte dividido entre coste. Las dos de seguimiento superan '
         'las treinta veces; la presencia digital es la única con retorno directo negativo.">' % (W, H, W, H)]
    p.append(mono(ox, oy - 26, "euros aportados por cada euro gastado", anchor="start", size=10))
    for k in (0, 10, 20, 30, 40):
        x = ox + aw * k / 40
        p.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="var(--line-soft)" stroke-width="1"/>'
                 % (x, oy - 8, x, oy + ah * len(filas) - 6))
        p.append(mono(x, oy - 14, "%d×" % k, anchor="middle", size=9))
    for i, f in enumerate(filas):
        y = oy + ah * i
        p.append(txt(ox - 16, y + 20, "%s · %s" % (f["cod"], f["nombre"]), anchor="end",
                     size=11.5, color="var(--ink)"))
        r = f["retorno"] or 0
        if r > 0:
            largo = aw * min(r, 40) / 40
            p.append('<rect x="%d" y="%d" width="%.1f" height="18" fill="%s" rx="3"/>'
                     % (ox, y + 6, largo, TEAL if r >= 5 else "#A3D8D1"))
            p.append(txt(ox + largo + 10, y + 20, "%.1f×" % r, size=11.5, weight=600, color="var(--ink)"))
        else:
            p.append('<rect x="%d" y="%d" width="46" height="18" fill="%s" rx="3"/>' % (ox, y + 6, OCRE))
            p.append(txt(ox + 56, y + 20, "retorno directo negativo", size=11.5, weight=600, color=OCRE))
        p.append(mono(ox + aw + 76, y + 20, "%s k€ / %s k€" % (mil(f["aporte"] / 1000), mil(f["coste"] / 1000)),
                      anchor="start", size=9.5))
    p.append(mono(16, H - 26, "Umbral de la cartera: ningún gasto puede superar el 40 % de lo que la "
                  "campaña aporta. C5 lo roza; C9 lo incumple y se aprueba como habilitador, no como campaña.",
                  anchor="start", size=10))
    p.append("</svg>")
    return "\n".join(p)


# ------------------------------------------------------------------ F12 · concentración
def concentracion():
    filas = sorted(D["campanas"], key=lambda f: -f["aporte"])
    total = sum(f["aporte"] for f in filas)
    W, H = 900, 190
    ox, oy, aw, ah = 40, 74, 820, 46
    p = ['<svg viewBox="0 0 %d %d" width="%d" height="%d" role="img" style="max-width:100%%;height:auto" '
         'aria-label="Concentración de la cartera: dos campañas de nueve aportan el 63 por ciento de lo que '
         'suman todas.">' % (W, H, W, H)]
    p.append(mono(ox, 30, "peso de cada campaña sobre lo que aporta la cartera", anchor="start", size=10))
    x = ox
    for i, f in enumerate(filas):
        if f["aporte"] <= 0:
            continue
        ancho = aw * f["aporte"] / total
        color = TEAL if i < 2 else ("#66BDB3" if i < 4 else "#C6E9E4")
        p.append('<rect x="%.1f" y="%d" width="%.1f" height="%d" fill="%s" stroke="var(--surface)" '
                 'stroke-width="2"/>' % (x, oy, ancho, ah, color))
        if ancho > 54:
            p.append(txt(x + ancho / 2, oy + 20, f["cod"], anchor="middle", size=12, weight=600,
                         color="#FFFFFF" if i < 4 else "var(--ink)"))
            p.append(txt(x + ancho / 2, oy + 36, "%.0f %%" % (f["aporte"] / total * 100), anchor="middle",
                         size=10.5, color="#FFFFFF" if i < 4 else "var(--ink-2)"))
        x += ancho
    dos = sum(f["aporte"] for f in filas[:2]) / total
    p.append('<line x1="%d" y1="%d" x2="%.1f" y2="%d" stroke="var(--ink)" stroke-width="1.5"/>'
             % (ox, oy - 10, ox + aw * dos, oy - 10))
    p.append(txt(ox + aw * dos / 2, oy - 18, "C6 y C1 · %.0f %% de la cartera" % (dos * 100),
                 anchor="middle", size=11.5, weight=600, color="var(--ink)"))
    p.append(txt(ox, oy + ah + 26, "Las dos campañas más baratas de la cartera son las dos que más aportan. "
                 "Si falla cualquiera de ellas, no se pierde un bloque: se pierde el objetivo.",
                 size=11.5, color="var(--ink-2)"))
    p.append("</svg>")
    return "\n".join(p)


SALIDA.write_text("\n".join([
    "<!--F8-->", puente(), "<!--F9-->", calendario(), "<!--F10-->", composicion(),
    "<!--F11-->", retorno(), "<!--F12-->", concentracion(), ""]), encoding="utf-8")
print("figuras derivadas del modelo:", SALIDA.stat().st_size, "bytes")
