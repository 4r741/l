#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Las cuatro figuras del Plan Maestro de Marketing.

Escribe en fuentes/figuras-marketing.html los bloques que ensambla después el
generador del plan. Ninguna cifra se teclea aquí: las de aporte vienen del
modelo de campañas y las de recuento, del catálogo de acciones.
"""
import importlib.util
import pathlib

RAIZ = pathlib.Path(__file__).resolve().parent.parent
FUENTES = RAIZ / "fuentes"


def carga(nombre, archivo):
    spec = importlib.util.spec_from_file_location(nombre, RAIZ / archivo)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


D = carga("modelo", "modelo-campanas.py").calcula()
CAT = carga("catalogo", "catalogo-acciones.py").calcula()

SALIDA = FUENTES / "figuras-marketing.html"
TEAL, OCRE, MORA, TINTA = "#0F7A6E", "#B0641C", "#1D5A73", "#12232B"
# Rampa secuencial de un solo tono, monótona en claridad. Para recuentos, no
# para identidad: el color dice «cuántos», nunca «cuál».
RAMPA = ["#F1F9F7", "#D3EBE7", "#A8D5CE", "#71B8AE", "#37988B", "#0F7A6E", "#0B5C53"]


def txt(x, y, s, anchor="start", size=12, weight=400, color="var(--ink-2)"):
    return ('<text x="%s" y="%s" text-anchor="%s" font-size="%s" font-weight="%s" '
            'fill="%s" font-family="var(--f-body)">%s</text>' % (x, y, anchor, size, weight, color, s))


def mono(x, y, s, anchor="start", size=11, color="var(--muted)"):
    return ('<text x="%s" y="%s" text-anchor="%s" font-size="%s" fill="%s" '
            'font-family="var(--f-mono)" letter-spacing=".04em">%s</text>' % (x, y, anchor, size, color, s))


def mil(v):
    return "{:,}".format(int(round(v))).replace(",", ".").replace("-", "−")


def envolver(texto, ancho):
    palabras, linea, lineas = texto.split(), "", []
    for w in palabras:
        if len(linea + " " + w) > ancho:
            lineas.append(linea); linea = w
        else:
            linea = (linea + " " + w).strip()
    lineas.append(linea)
    return lineas


def svg(w, h, cuerpo, titulo):
    return ('<svg viewBox="0 0 %d %d" width="%d" height="%d" role="img" '
            'aria-label="%s" style="max-width:100%%;height:auto">%s</svg>'
            % (w, h, w, h, titulo, cuerpo))


# ================================================================ FM1 · los estados
def fm1():
    """El mapa de los doce estados.

    No es un embudo. Un embudo va en un sentido y termina en la venta; una
    persona va y viene, se apaga y a veces vuelve. Los trazos gruesos son los
    tres pasos que el modelo del Plan de Dirección señala como los que mueven el dinero,
    y ninguno de los tres consiste en captar a nadie nuevo.
    """
    W, H = 1120, 760
    CAJA_W, CAJA_H, GAP, X0 = 210, 62, 26, 48
    p = ['<rect width="%d" height="%d" fill="var(--paper)"/>' % (W, H)]

    BANDAS = [
        (62, "Fuera · todavía no nos busca", ["E1 Ajeno", "E2 Latente", "E3 Despierto"], "#70858F", False),
        (202, "Buscando · nos compara", ["E4 En busca", "E5 En consideración"], MORA, False),
        (342, "Dentro · es nuestro paciente", ["E6 En la puerta", "E7 En decisión", "E8 En tratamiento"], TEAL, False),
        (482, "Después · decide seguir", ["E9 En cuidado", "E10 Prescriptor"], TEAL, False),
        (622, "Apagado · sigue siendo nuestro", ["E11 Dormido", "E12 Perdido"], OCRE, True),
    ]
    pos, rotulos = {}, []
    for y, rotulo, nodos, color, punteado in BANDAS:
        # Los rótulos de banda se pintan al final, sobre fondo de papel: por ahí
        # pasan trazos de vuelta, y en SVG manda el orden, no la intención. Una
        # palabra tachada por una línea deja de ser una palabra.
        rotulos.append('<rect x="%d" y="%d" width="%d" height="15" fill="var(--paper)"/>'
                       % (X0 - 5, y - 57, len(rotulo) * 6.15 + 10))
        rotulos.append(mono(X0, y - 46, rotulo.upper(), size=10))
        x = X0
        for n in nodos:
            cod, nombre = n.split(" ", 1)
            p.append('<rect x="%d" y="%d" width="%d" height="%d" rx="3" fill="%s" stroke="%s" '
                     'stroke-width="1.5"%s/>'
                     % (x, y, CAJA_W, CAJA_H, "var(--surface)" if punteado or color == "#70858F" else "var(--paper)",
                        color, ' stroke-dasharray="5 3"' if punteado else ""))
            p.append(mono(x + 14, y + 22, cod, size=10, color=color))
            p.append(txt(x + 14, y + 43, nombre, size=14, weight=600, color="var(--ink)"))
            pos[cod] = {"x": x, "y": y, "x2": x + CAJA_W, "y2": y + CAJA_H, "cx": x + CAJA_W / 2}
            x += CAJA_W + GAP

    p.append('<defs>'
             '<marker id="pm-f" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">'
             '<path d="M0,0 L10,5 L0,10 z" fill="%s"/></marker>'
             '<marker id="pm-g" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">'
             '<path d="M0,0 L10,5 L0,10 z" fill="%s"/></marker>'
             '<marker id="pm-o" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">'
             '<path d="M0,0 L10,5 L0,10 z" fill="%s"/></marker>'
             '</defs>' % (TEAL, "#70858F", OCRE))

    def horizontal(a, b, color="#70858F", grosor=1.4, marca="pm-g", guion=""):
        A, B = pos[a], pos[b]
        return ('<path d="M%s %s H%s" fill="none" stroke="%s" stroke-width="%s"%s '
                'marker-end="url(#%s)"/>'
                % (A["x2"] + 3, A["y"] + CAJA_H / 2, B["x"] - 9, color, grosor, guion, marca))

    def codo(a, b, color="#70858F", grosor=1.4, marca="pm-g", guion="", desvio=0, entrada=0):
        """Baja de A, gira por el pasillo entre bandas y entra por arriba de B."""
        A, B = pos[a], pos[b]
        pasillo = B["y"] - 20 + desvio
        return ('<path d="M%s %s V%s H%s V%s" fill="none" stroke="%s" stroke-width="%s"%s '
                'marker-end="url(#%s)"/>'
                % (A["cx"], A["y2"] + 3, pasillo, B["cx"] + entrada, B["y"] - 9,
                   color, grosor, guion, marca))

    def sube(a, b, color, grosor, marca, guion="", carril=0):
        """Vuelve hacia arriba por un carril lateral, a la izquierda de todo."""
        A, B = pos[a], pos[b]
        return ('<path d="M%s %s H%s V%s H%s" fill="none" stroke="%s" stroke-width="%s"%s '
                'marker-end="url(#%s)"/>'
                % (A["x"] - 3, A["y"] + CAJA_H / 2, carril, B["y"] + CAJA_H / 2,
                   B["x"] - 9, color, grosor, guion, marca))

    for a, b in (("E1", "E2"), ("E2", "E3"), ("E4", "E5"), ("E6", "E7"), ("E7", "E8"), ("E9", "E10")):
        p.append(horizontal(a, b))
    p.append(codo("E3", "E4"))
    p.append(codo("E5", "E6"))

    # E8 → E9 · el paso que sostiene un tercio de lo que aporta la cartera
    p.append(codo("E8", "E9", TEAL, 5, "pm-f"))
    p.append(mono(660, 455, "C1 · 171 k€  ·  QUE NO TERMINE AL TERMINAR", size=11, color=TEAL))

    # E9 → E11 · la gente no se va: se apaga
    p.append(codo("E9", "E11", OCRE, 1.6, "pm-o", ' stroke-dasharray="5 3"', entrada=95))
    p.append(horizontal("E11", "E12", OCRE, 1.4, "pm-o", ' stroke-dasharray="5 3"'))
    p.append(mono(540, 596, "NO SE VA: SE APAGA, Y SIN AVISAR", size=10, color=OCRE))

    # E11 → E6 · el rescate, por el carril de la izquierda
    p.append(sube("E11", "E6", TEAL, 5, "pm-f", carril=22))
    p.append(mono(540, 659, "C6 · 172 k€  ·  C3 · 13 k€  ·  VOLVER A LLAMAR", size=11, color=TEAL))

    # E10 → E4 · el prescriptor no vuelve a buscarnos: pone a OTRA persona en E4.
    # Sube por el margen derecho, que está vacío, y no por el carril de la
    # izquierda, donde se confundiría con el rescate.
    A, B = pos["E10"], pos["E4"]
    p.append('<path d="M%s %s H%s V%s H%s V%s" fill="none" stroke="%s" stroke-width="2.6" '
             'stroke-dasharray="2 4" marker-end="url(#pm-f)"/>'
             % (A["x2"] + 3, A["y"] + CAJA_H / 2, W - 40, 134, B["cx"] + 60, B["y"] - 9, TEAL))
    p.append(mono(660, 126, "C8 · SU PALABRA PONE A OTRA PERSONA EN E4", size=11, color=TEAL))

    p.extend(rotulos)
    p.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="var(--line)"/>' % (X0, H - 46, W - 48, H - 46))
    p.append('<rect x="%d" y="%d" width="26" height="5" fill="%s"/>' % (X0, H - 27, TEAL))
    p.append(mono(X0 + 36, H - 20, "LOS TRES PASOS QUE SOSTIENEN EL 63 % DE LO QUE APORTA LA CARTERA, "
                  "Y NINGUNO CAPTA A NADIE NUEVO", size=10, color=TEAL))
    return svg(W, H, "".join(p), "Los doce estados del paciente y los pasos entre ellos")


# ================================================================ FM2 · dónde aporta
GRUPO_DE = {"C1": "G6", "C2": "G3", "C3": "G6", "C4": "G7", "C5": "G3",
            "C6": "G6", "C7": "G3", "C8": "G7", "C9": "G2"}


def aportes_por_grupo():
    ap = {g[0]: 0.0 for g in CAT["grupos"]}
    for f in D["campanas"]:
        ap[GRUPO_DE[f["cod"]]] += f["aporte"]
    return ap


def fm2():
    """Lo que cada grupo aporta este ejercicio, frente a cuántas acciones tiene.

    Es el hallazgo incómodo del plan: los tres grupos con más acciones aportan
    cero euros este año. No sobran; es que su plazo no es este ejercicio.
    """
    W, H = 1120, 546
    ap = aportes_por_grupo()
    maxv = max(abs(v) for v in ap.values())
    p = ['<rect width="%d" height="%d" fill="var(--paper)"/>' % (W, H)]
    x0, ancho, alto, gap = 330, 600, 44, 16
    cero = x0 + ancho * 0.06
    escala = (x0 + ancho - cero) / maxv

    p.append(mono(48, 34, "GRUPO", size=10))
    p.append(mono(x0, 34, "APORTE PLANIFICADO EN EL EJERCICIO", size=10))
    p.append(mono(W - 48, 34, "ACCIONES", size=10, anchor="end"))

    y = 56
    for cod, estados, titulo, _ in CAT["grupos"]:
        v = ap[cod]
        n = CAT["por_grupo"][cod]
        p.append(mono(48, y + 18, cod, size=11, color=TEAL if v > 0 else "var(--muted)"))
        p.append(txt(86, y + 20, titulo, size=14, weight=600, color="var(--ink)"))
        p.append(mono(86, y + 38, estados, size=10))
        p.append('<line x1="%s" y1="%d" x2="%s" y2="%d" stroke="var(--line)"/>' % (cero, y - 6, cero, y + alto + 6))
        if abs(v) < 1:
            p.append(txt(cero + 10, y + 26, "sin aporte directo este ejercicio", size=12, color="var(--muted)"))
        elif v > 0:
            w = v * escala
            p.append('<rect x="%s" y="%d" width="%s" height="%d" rx="3" fill="%s"/>' % (cero + 2, y, w - 2, alto, TEAL))
            p.append(txt(cero + w + 10, y + 27, mil(v / 1000) + " k€", size=14, weight=700, color="var(--ink)"))
        else:
            w = abs(v) * escala
            p.append('<rect x="%s" y="%d" width="%s" height="%d" rx="3" fill="%s"/>' % (cero - w, y, w - 2, alto, OCRE))
            # el rótulo va al lado vacío del eje: a la izquierda chocaría con el título
            p.append(txt(cero + 12, y + 27, "−" + mil(abs(v) / 1000) + " k€", size=13, weight=700,
                         color="var(--ink)"))
        p.append(txt(W - 48, y + 27, str(n), size=15, weight=700, color="var(--ink)", anchor="end"))
        y += alto + gap

    p.append('<line x1="48" y1="%d" x2="%d" y2="%d" stroke="var(--line)"/>' % (y + 6, W - 48, y + 6))
    p.append(mono(48, y + 30, "APORTE POSITIVO", size=10, color=TEAL))
    p.append('<rect x="180" y="%d" width="22" height="10" rx="2" fill="%s"/>' % (y + 21, TEAL))
    p.append(mono(220, y + 30, "APORTE NEGATIVO EN RÉGIMEN DE AGENDA LLENA", size=10, color=OCRE))
    p.append('<rect x="640" y="%d" width="22" height="10" rx="2" fill="%s"/>' % (y + 21, OCRE))
    return svg(W, H, "".join(p), "Aporte planificado por grupo del catálogo frente al número de acciones")


# ================================================================ FM3 · coste × plazo
def fm3():
    """Las 76 acciones repartidas por lo que cuestan y por lo que tardan."""
    COSTES = [("0", "Sin coste"), ("€", "Hasta 1 k€"), ("€€", "1–5 k€"), ("€€€", "5–15 k€"), ("€€€€", "Más de 15 k€")]
    PLAZOS = [("ya", "Ya"), ("trim", "Un trimestre"), ("año", "Un año"), ("estruct", "Estructural")]
    rec = {}
    for a in CAT["acciones"]:
        rec[(a["plazo"], a["coste"])] = rec.get((a["plazo"], a["coste"]), 0) + 1
    tope = max(rec.values())

    W, H = 1000, 400
    cw, ch, x0, y0 = 152, 62, 210, 78
    p = ['<rect width="%d" height="%d" fill="var(--paper)"/>' % (W, H)]
    for j, (_, rot) in enumerate(COSTES):
        p.append(mono(x0 + j * cw + cw / 2, y0 - 14, rot.upper(), size=10, anchor="middle"))
    for i, (pk, rot) in enumerate(PLAZOS):
        p.append(txt(x0 - 18, y0 + i * ch + ch / 2 + 5, rot, size=13, weight=600,
                     color="var(--ink)", anchor="end"))
        for j, (ck, _) in enumerate(COSTES):
            n = rec.get((pk, ck), 0)
            paso = 0 if n == 0 else 1 + int(round((len(RAMPA) - 2) * (n / tope)))
            x, y = x0 + j * cw, y0 + i * ch
            p.append('<rect x="%d" y="%d" width="%d" height="%d" fill="%s" stroke="var(--paper)" '
                     'stroke-width="2"/>' % (x, y, cw, ch, RAMPA[paso]))
            if n:
                tinta = "#FFFFFF" if paso >= len(RAMPA) - 2 else TINTA
                p.append(txt(x + cw / 2, y + ch / 2 + 7, str(n), size=19, weight=700,
                             color=tinta, anchor="middle"))
    p.append(mono(48, 34, "PLAZO × COSTE  ·  %d ACCIONES" % CAT["total"], size=11, color=TINTA))
    p.append(mono(48, H - 40, "MÁS OSCURO, MÁS ACCIONES EN ESA CASILLA", size=10))
    for k, c in enumerate(RAMPA[1:], start=0):
        p.append('<rect x="%d" y="%d" width="26" height="10" fill="%s"/>' % (430 + k * 27, H - 49, c))
    p.append(mono(430, H - 26, "1", size=10))
    p.append(mono(430 + 6 * 27 + 26, H - 26, str(tope), size=10, anchor="end"))
    return svg(W, H, "".join(p), "Las acciones del catálogo por plazo y por banda de coste")


# ================================================================ FM4 · la ventana de mar
def fm4():
    """El calendario de tierra: cuándo se puede tratar a quien embarca.

    Naturaleza: modelo. Las ventanas son un supuesto de trabajo que hay que
    contrastar con las cofradías y con los armadores antes de comprometer nada.
    """
    MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    # (rótulo, meses en tierra 0-11, nota)
    FLOTAS = [
        ("Bajura y artes menores", [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
         "En tierra casi todo el año; la restricción es el horario, no el calendario"),
        ("Cerco y arrastre de litoral", [0, 1, 11],
         "Paradas biológicas y temporal de invierno"),
        ("Gran altura · campañas largas", [0, 1, 6, 7],
         "Ventanas de tierra entre mareas, cortas y con fecha fija"),
        ("Personal de tierra del puerto", [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
         "Sin restricción de calendario; sí de turno"),
    ]
    W, H = 1080, 380
    x0, y0, cw, ch = 330, 92, (W - 330 - 48) / 12.0, 58
    p = ['<rect width="%d" height="%d" fill="var(--paper)"/>' % (W, H)]
    p.append(mono(48, 36, "VENTANA DE TIERRA POR TIPO DE FLOTA  ·  SUPUESTO A CONTRASTAR", size=11, color=OCRE))
    for j, m in enumerate(MESES):
        p.append(mono(x0 + j * cw + cw / 2, y0 - 14, m.upper(), size=10, anchor="middle"))
    for i, (rot, meses, nota) in enumerate(FLOTAS):
        y = y0 + i * ch
        p.append(txt(48, y + 24, rot, size=13, weight=600, color="var(--ink)"))
        for lin_i, lin in enumerate(envolver(nota, 44)[:2]):
            p.append(txt(48, y + 40 + lin_i * 13, lin, size=10.5, color="var(--muted)"))
        for j in range(12):
            x = x0 + j * cw
            dentro = j in meses
            p.append('<rect x="%s" y="%d" width="%s" height="%d" fill="%s" stroke="var(--paper)" '
                     'stroke-width="2"/>' % (x, y, cw, ch - 12, TEAL if dentro else "var(--surface)"))
        y += ch
    p.append('<line x1="48" y1="%d" x2="%d" y2="%d" stroke="var(--line)"/>' % (H - 52, W - 48, H - 52))
    p.append('<rect x="48" y="%d" width="22" height="10" rx="2" fill="%s"/>' % (H - 40, TEAL))
    p.append(mono(80, H - 31, "EN TIERRA: SE PUEDE PLANIFICAR TRATAMIENTO", size=10))
    p.append('<rect x="520" y="%d" width="22" height="10" rx="2" fill="var(--surface)" stroke="var(--line)"/>' % (H - 40))
    p.append(mono(552, H - 31, "EMBARCADO O NO DISPONIBLE", size=10))
    return svg(W, H, "".join(p), "Ventana de tierra por tipo de flota a lo largo del año")


FIGS = [("FM1", fm1()), ("FM2", fm2()), ("FM3", fm3()), ("FM4", fm4())]
SALIDA.write_text("\n".join("<!--%s-->\n%s\n" % (c, s) for c, s in FIGS), encoding="utf-8")
print("figuras del plan: %d · %d bytes" % (len(FIGS), SALIDA.stat().st_size))
