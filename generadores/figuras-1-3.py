# -*- coding: utf-8 -*-
"""Figuras F1 a F3: coste del descuento, primeras visitas necesarias y valor del paciente.

Se ejecuta desde build.py; también se puede lanzar suelto. Escribe en
fuentes/ los bloques que después ensambla el generador del Plan de Dirección.
"""
import pathlib

RAIZ = pathlib.Path(__file__).resolve().parent.parent
FUENTES = RAIZ / "fuentes"

TEAL = "#0F7A6E"      # validado: paleta categórica de 2 series sobre #FFFFFF
OCRE = "#B0641C"
SALIDA = FUENTES / "figuras-1-3.html"

def txt(x, y, s, anchor="start", size=12, weight=400, color="var(--ink-2)"):
    return ('<text x="%s" y="%s" text-anchor="%s" font-size="%s" font-weight="%s" '
            'fill="%s" font-family="var(--f-body)">%s</text>' % (x, y, anchor, size, weight, color, s))

def mono(x, y, s, anchor="start", size=11, color="var(--muted)"):
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" fill="{color}" '
            f'font-family="var(--f-mono)" letter-spacing=".04em">{s}</text>')

# ---------------------------------------------------------------- figura 1
def figura_descuento():
    W, H = 860, 348
    ox, oy = 70, 58          # origen del área de trazado
    aw, ah = W - ox - 30, 210
    datos = [(0, 100, 60, 40), (5, 95, 60, 35), (10, 90, 60, 30), (15, 85, 60, 25), (20, 80, 60, 20)]
    maxv = 100
    bw, hueco = 78, 40
    p = [f'<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
         f'aria-label="Reparto de cada 100 euros facturados según el descuento aplicado: los costes se mantienen en 60 y el beneficio cae de 40 a 20." '
         f'style="max-width:100%;height:auto">']
    # rejilla
    for v in (0, 20, 40, 60, 80, 100):
        y = oy + ah - ah * v / maxv
        p.append(f'<line x1="{ox}" y1="{y:.1f}" x2="{ox+aw}" y2="{y:.1f}" stroke="var(--line-soft)" stroke-width="1"/>')
        p.append(mono(ox - 10, y + 4, str(v), anchor="end"))
    for i, (desc, precio, coste, benef) in enumerate(datos):
        x = ox + 24 + i * (bw + hueco)
        y_coste = oy + ah - ah * coste / maxv
        h_coste = ah * coste / maxv
        h_benef = ah * benef / maxv
        y_benef = y_coste - h_benef - 2          # 2px de aire entre segmentos
        p.append(f'<rect x="{x}" y="{y_coste:.1f}" width="{bw}" height="{h_coste:.1f}" fill="{OCRE}"/>')
        p.append(f'<rect x="{x}" y="{y_benef:.1f}" width="{bw}" height="{h_benef:.1f}" fill="{TEAL}" rx="4" ry="4"/>')
        p.append(txt(x + bw / 2, y_benef - 8, f"{benef} €", anchor="middle", size=13, weight=600, color="var(--ink)"))
        etiqueta = "sin descuento" if desc == 0 else f"−{desc} %"
        p.append(mono(x + bw / 2, oy + ah + 22, etiqueta, anchor="middle", size=11, color="var(--ink-2)"))
        if desc:
            perdido = (40 - benef) / 40 * 100
            texto = ("%.1f" % perdido).rstrip("0").rstrip(".").replace(".", ",")
            p.append(mono(x + bw / 2, oy + ah + 40, "−" + texto + " %", anchor="middle", size=10))
    # eje
    p.append(f'<line x1="{ox}" y1="{oy+ah}" x2="{ox+aw}" y2="{oy+ah}" stroke="var(--line)" stroke-width="1"/>')
    p.append(mono(ox + aw, oy + ah + 40, "beneficio perdido", anchor="end", size=10))
    p.append(mono(ox - 10, 22, "€ por cada 100 facturados", anchor="start"))
    # leyenda
    ly = H - 18
    p.append(f'<rect x="{ox}" y="{ly-10}" width="12" height="12" rx="3" fill="{TEAL}"/>')
    p.append(txt(ox + 20, ly, "Beneficio", size=12))
    p.append(f'<rect x="{ox+120}" y="{ly-10}" width="12" height="12" rx="3" fill="{OCRE}"/>')
    p.append(txt(ox + 140, ly, "Costes del caso", size=12))
    p.append("</svg>")
    return "\n".join(p)

# ---------------------------------------------------------------- figura 2
def figura_pv():
    W, H = 860, 312
    ox, oy = 70, 46
    aw, ah = W - ox - 30, 190
    datos = [("30 %", 5.3), ("40 %", 4.0), ("50 %", 3.2), ("60 %", 2.6)]
    maxv = 6
    bw, hueco = 96, 70
    p = [f'<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
         f'aria-label="Primeras visitas necesarias al día según la tasa de conversión: 5,3 con el 30 por ciento y 2,6 con el 60 por ciento." '
         f'style="max-width:100%;height:auto">']
    for v in (0, 2, 4, 6):
        y = oy + ah - ah * v / maxv
        p.append(f'<line x1="{ox}" y1="{y:.1f}" x2="{ox+aw}" y2="{y:.1f}" stroke="var(--line-soft)" stroke-width="1"/>')
        p.append(mono(ox - 10, y + 4, str(v), anchor="end"))
    for i, (etq, val) in enumerate(datos):
        x = ox + 40 + i * (bw + hueco)
        h = ah * val / maxv
        y = oy + ah - h
        p.append(f'<rect x="{x}" y="{y:.1f}" width="{bw}" height="{h:.1f}" fill="{TEAL}" rx="4" ry="4"/>')
        p.append(txt(x + bw / 2, y - 9, f"{val:.1f}".replace(".", ","), anchor="middle", size=14, weight=600, color="var(--ink)"))
        p.append(mono(x + bw / 2, oy + ah + 22, etq, anchor="middle", size=11, color="var(--ink-2)"))
    p.append(f'<line x1="{ox}" y1="{oy+ah}" x2="{ox+aw}" y2="{oy+ah}" stroke="var(--line)" stroke-width="1"/>')
    p.append(mono(ox - 10, 18, "primeras visitas necesarias al día", anchor="start"))
    p.append(mono(ox + aw, oy + ah + 44, "tasa de conversión de la primera visita", anchor="end", size=10))
    p.append("</svg>")
    return "\n".join(p)

# ---------------------------------------------------------------- figura 3
def figura_valor():
    W, H = 860, 320
    ox, oy = 70, 34
    aw, ah = W - ox - 30, 200
    maxv = 1800
    barras = [
        ("Sin programa de cuidado", [("Tratamiento inicial", 720, TEAL)]),
        ("Con programa de cuidado", [("Tratamiento inicial", 720, TEAL),
                                     ("Cuota, 5 años", 285, OCRE),
                                     ("Tratamiento detectado a tiempo", 360, TEAL),
                                     ("Paciente referido", 288, OCRE)]),
    ]
    bh, hueco = 62, 54
    p = [f'<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
         f'aria-label="Valor a cinco años de un paciente: 720 euros sin programa de cuidado y 1.653 euros con él." '
         f'style="max-width:100%;height:auto">']
    for v in (0, 600, 1200, 1800):
        x = ox + aw * v / maxv
        p.append(f'<line x1="{x:.1f}" y1="{oy}" x2="{x:.1f}" y2="{oy+ah-40}" stroke="var(--line-soft)" stroke-width="1"/>')
        p.append(mono(x, oy + ah - 24, f"{v:,}".replace(",", ".") + " €", anchor="middle", size=10))
    for i, (nombre, tramos) in enumerate(barras):
        y = oy + 26 + i * (bh + hueco)
        x = ox
        total = 0
        for j, (etq, val, color) in enumerate(tramos):
            w = aw * val / maxv
            radio = ' rx="4" ry="4"' if j == len(tramos) - 1 else ""
            p.append(f'<rect x="{x:.1f}" y="{y}" width="{max(w-2,2):.1f}" height="{bh}" fill="{color}"{radio}/>')
            if val >= 280:
                p.append(txt(x + w / 2 - 1, y + bh / 2 + 5, f"{val} €", anchor="middle", size=12, weight=600, color="#FFFFFF"))
            x += w
            total += val
        p.append(mono(ox, y - 10, nombre.upper(), size=11, color="var(--ink-2)"))
        p.append(txt(x + 12, y + bh / 2 + 6, f"{total:,}".replace(",", ".") + " €", size=17, weight=600, color="var(--ink)"))
    ly = H - 16
    leyenda = [("Margen de tratamiento", TEAL), ("Margen del programa y del referido", OCRE)]
    lx = ox
    for etq, color in leyenda:
        p.append(f'<rect x="{lx}" y="{ly-10}" width="12" height="12" rx="3" fill="{color}"/>')
        p.append(txt(lx + 20, ly, etq, size=12))
        lx += 26 + len(etq) * 6.6
    p.append("</svg>")
    return "\n".join(p)

SALIDA.write_text("<!--F1-->\n" + figura_descuento() + "\n<!--F2-->\n" + figura_pv() + "\n<!--F3-->\n" + figura_valor() + "\n", encoding="utf-8")
print("figuras generadas:", SALIDA.stat().st_size, "bytes")
