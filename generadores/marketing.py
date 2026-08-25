#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ensambla marketing.html, el Plan Maestro de Marketing v@VERSION@.

La prosa vive en fuentes/marketing-0*.html; las tablas, los recuentos y las
cuatro figuras se derivan de catalogo-acciones.py y de modelo-campanas.py. No
hay una sola cifra tecleada en el documento: si el catálogo cambia, el
documento cambia con él, y el verificador comprueba que así sea.
"""
import importlib.util
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SP = RAIZ / "fuentes"

# La versión no se teclea: sale de version.py, que es el único sitio donde vive.
_v = {}
exec(compile((RAIZ / "version.py").read_text(encoding="utf-8"), "version.py", "exec"), _v)
VERSION, FECHA, CORTA = _v["VERSION"], _v["FECHA"], _v["CORTA"]


def sello(t):
    """Estampa la versión vigente en el documento antes de escribirlo.

    Los archivos fuente llevan @VERSION@ y @FECHA@ en vez del número, de modo
    que subir de versión sea cambiar una línea de version.py y no catorce
    archivos con catorce oportunidades de olvidarse de uno.
    """
    t = t.replace("@VERSION@", VERSION).replace("@FECHA@", FECHA).replace("@CORTA@", CORTA)
    assert "@VERSION@" not in t and "@FECHA@" not in t
    return t



def carga(nombre, archivo):
    spec = importlib.util.spec_from_file_location(nombre, RAIZ / archivo)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


catalogo = carga("catalogo", "catalogo-acciones.py")
CAT = catalogo.calcula()
D = carga("modelo", "modelo-campanas.py").calcula()
CAMPANA = {f["cod"]: f for f in D["campanas"]}

SEM = {"verde": "sem--verde", "amarillo": "sem--amarillo", "naranja": "sem--naranja"}
SEM_ROTULO = {"verde": "Sin trámite", "amarillo": "Revisar contenido", "naranja": "Revisión previa"}


def mil(v):
    return "{:,}".format(int(round(v))).replace(",", ".")


# ---------------------------------------------------------------- cabecera
manual = (RAIZ / "manual.html").read_text(encoding="utf-8")
i = manual.index("<body>")
cabecera = manual[:i + len("<body>")]
cabecera = cabecera.replace("<title>Manual Maestro Giraldo</title>",
                            "<title>Plan Maestro de Marketing Giraldo</title>")
cabecera = re.sub(r'<meta name="description" content="[^"]*">',
                  '<meta name="description" content="Plan Maestro de Marketing del Centro de '
                  'Excelencia Implantológica Giraldo: doce estados del paciente, seis arquetipos '
                  'de la ría, siete momentos de verdad, un catálogo de 76 acciones con dueño, '
                  'coste y semáforo legal, diez piezas propias, la Campaña de Mar y las reglas '
                  'de medición y de parada.">', cabecera, count=1)
assert "Plan Maestro de Marketing Giraldo" in cabecera

editorial = (SP / "editorial.css").read_text(encoding="utf-8")
k = cabecera.rindex("</style>")
cabecera = cabecera[:k] + editorial + "\n" + cabecera[k:]
script = manual[manual.index("<script>\n(function(){"):]

# ---------------------------------------------------------------- barra
TIRA = [("#portada", "Portada"), ("#control", "§0 Control"),
        ("#parte-1", "I · Doctrina"), ("#doctrina", "§1 Por qué"), ("#regla", "§2 La regla"),
        ("#nunca", "§3 Las ocho que no"), ("#legal", "§4 Marco legal"),
        ("#parte-2", "II · El paciente"), ("#estados", "§5 Doce estados"),
        ("#arquetipos", "§6 Seis de la ría"), ("#momentos", "§7 Momentos de verdad"),
        ("#asimetria", "§8 La asimetría"),
        ("#parte-3", "III · El catálogo"), ("#catalogo", "§9 Las 76 acciones"),
        ("#parte-4", "IV · Las diez piezas"), ("#piezas", "§10 Las diez piezas"),
        ("#parte-5", "V · El territorio"), ("#digital", "§11 Digital"),
        ("#ria", "§12 El mapa de la ría"), ("#mar", "§13 Campaña de Mar"),
        ("#parte-6", "VI · La prioridad"), ("#economia", "§14 Qué aporta cada grupo"),
        ("#prioridad", "§15 Qué va primero"), ("#presupuesto", "§16 Presupuesto"),
        ("#parte-7", "VII · El gobierno"), ("#indicadores", "§17 Las ocho medidas"),
        ("#calendario", "§18 Calendario"), ("#parada", "§19 Reglas de parada"),
        ("#anexo-legal", "Anexo I · Legal"), ("#anexo-cartera", "Anexo II · Cartera"),
        ("#anexo-trimestre", "Anexo III · Este trimestre")]

barra = """
<header class="topbar">
  <div class="wrap">
    <div class="topbar__in">
      <a class="brand" href="#portada">
        <span class="brand__mark">Plan Maestro de <b>Marketing</b></span>
        <span class="brand__tag">Giraldo · v@VERSION@</span>
      </a>
      <a class="crosslink" href="memoria.html">Tesis de Dirección</a>
      <a class="crosslink" href="manual.html">Manual Maestro</a>
      <a class="crosslink" href="otros.html">Otros documentos</a>
    </div>
    <nav class="strip" id="strip" aria-label="Índice del plan">
%s
    </nav>
  </div>
</header>

<main>

<div class="printhead" aria-hidden="true"><b>Plan Maestro de Marketing · Junta Directiva · v@VERSION@</b><span>Centro de Excelencia Implantológica Giraldo · Uso interno · Confidencial</span></div>
""" % "\n".join('      <a href="%s">%s</a>' % (h, r) for h, r in TIRA)


# ---------------------------------------------------------------- tablas del catálogo
def fila(a):
    campana = a["campana"]
    if campana != "—":
        campana = '<b>%s</b> · %s' % (campana, CAMPANA[campana]["nombre"])
    return ('<tr>'
            '<td class="num">%s</td>'
            '<td><strong>%s</strong><br><span style="color:var(--muted)">%s</span></td>'
            '<td>%s</td>'
            '<td class="num">%s</td><td>%s</td><td class="num">%s</td>'
            '<td>%s</td>'
            '<td><span class="sem %s">%s</span></td>'
            '<td>%s</td>'
            '</tr>'
            % (a["cod"], a["accion"], a["gana"], catalogo.PUESTO[a["quien"]],
               a["coste"], catalogo.PLAZO[a["plazo"]], a["efecto"], a["indicador"],
               SEM[a["sem"]], SEM_ROTULO[a["sem"]], campana))


def tablas_catalogo():
    piezas = []
    for cod, estados, titulo, lede in CAT["grupos"]:
        acciones = [a for a in CAT["acciones"] if a["grupo"] == cod]
        piezas.append(
            '<h3 style="font-size:var(--step-1);margin:3rem 0 .5rem" id="grupo-%s">'
            '%s · %s <span class="sem sem--verde">%d acciones</span></h3>'
            '<p style="color:var(--ink-2);max-width:74ch"><span class="mono">%s</span> — %s</p>'
            '<div class="tablewrap"><table><thead><tr>'
            '<th>Cód.</th><th>Acción · y qué gana el paciente</th><th>Dueño</th>'
            '<th>Coste</th><th>Plazo</th><th>Ef.</th><th>Indicador</th>'
            '<th>Legal</th><th>Campaña</th>'
            '</tr></thead><tbody>%s</tbody></table></div>'
            % (cod.lower(), cod, titulo, len(acciones), estados, lede,
               "".join(fila(a) for a in acciones)))
    return "\n".join(piezas)


def tabla_estados():
    return "".join('<tr><td class="num">%s</td><td><strong>%s</strong></td><td>%s</td></tr>'
                   % e for e in CAT["estados"])


def anexo_legal():
    piezas = []
    for sem in ("naranja", "amarillo", "verde"):
        acciones = [a for a in CAT["acciones"] if a["sem"] == sem]
        piezas.append(
            '<h3 style="font-size:var(--step-1);margin:2.6rem 0 .5rem">'
            '<span class="sem %s">%s</span> &nbsp;%d acciones</h3>'
            '<div class="tablewrap"><table><thead><tr><th>Cód.</th><th>Acción</th>'
            '<th>Qué hay que resolver antes</th></tr></thead><tbody>%s</tbody></table></div>'
            % (SEM[sem], SEM_ROTULO[sem], len(acciones),
               "".join('<tr><td class="num">%s</td><td>%s</td><td>%s</td></tr>'
                       % (a["cod"], a["accion"], {
                           "naranja": "Consentimiento expreso o verificación jurídica previa, "
                                      "con constancia escrita de quién revisó y cuándo",
                           "amarillo": "Revisión del contenido: una frase de más lo convierte "
                                       "en promesa de resultado",
                           "verde": "Nada. Se ejecuta sin trámite",
                       }[sem]) for a in acciones)))
    return "\n".join(piezas)


def anexo_cartera():
    filas = []
    for f in D["campanas"]:
        acciones = [a for a in CAT["acciones"] if a["campana"] == f["cod"]]
        codigos = " · ".join("<b>%s</b>" % a["cod"] for a in acciones) or "—"
        aporte = "%s k€" % mil(f["aporte"] / 1000) if f["aporte"] >= 0 \
            else "−%s k€" % mil(abs(f["aporte"]) / 1000)
        filas.append('<tr><td class="num">%s</td><td><strong>%s</strong></td>'
                     '<td class="num">%s</td><td>%s</td><td class="num">%d</td></tr>'
                     % (f["cod"], f["nombre"], aporte, codigos, len(acciones)))
    fuera = [a for a in CAT["acciones"] if a["campana"] == "—"]
    filas.append('<tr><td class="num">—</td><td><strong>Fuera de la cartera</strong><br>'
                 '<span style="color:var(--muted)">El fondo del que salen las campañas de los '
                 'ejercicios siguientes, incluida la Campaña de Mar</span></td>'
                 '<td class="num">sin aporte declarado</td><td>%d acciones</td>'
                 '<td class="num">%d</td></tr>' % (len(fuera), len(fuera)))
    return ('<div class="tablewrap"><table><thead><tr><th>Cód.</th><th>Campaña</th>'
            '<th>Aporte</th><th>Acciones que la sostienen</th><th>Nº</th>'
            '</tr></thead><tbody>%s</tbody></table></div>' % "".join(filas))


def anexo_trimestre():
    acciones = [a for a in CAT["acciones"] if a["coste"] == "0" and a["plazo"] == "ya"]
    por_puesto = {}
    for a in acciones:
        por_puesto.setdefault(a["quien"], []).append(a)
    piezas = []
    for puesto in catalogo.PUESTO:
        if puesto not in por_puesto:
            continue
        suyas = por_puesto[puesto]
        piezas.append(
            '<h3 style="font-size:var(--step-1);margin:2.6rem 0 .5rem">%s '
            '<span class="sem sem--verde">%d</span></h3>'
            '<div class="tablewrap"><table><thead><tr><th>Cód.</th><th>Acción</th>'
            '<th>Qué gana el paciente</th><th>Indicador</th></tr></thead><tbody>%s</tbody>'
            '</table></div>'
            % (catalogo.PUESTO[puesto], len(suyas),
               "".join('<tr><td class="num">%s</td><td>%s</td><td>%s</td><td>%s</td></tr>'
                       % (a["cod"], a["accion"], a["gana"], a["indicador"]) for a in suyas)))
    return "\n".join(piezas)


# ---------------------------------------------------------------- montaje
cuerpo = "\n\n".join((SP / ("marketing-0%d.html" % n)).read_text(encoding="utf-8").strip("\n")
                     for n in range(1, 6))

figuras = (SP / "figuras-marketing.html").read_text(encoding="utf-8")


def figura(marca):
    return figuras.split("<!--%s-->" % marca)[1].split("<!--")[0].strip()


ya0 = len([a for a in CAT["acciones"] if a["coste"] == "0" and a["plazo"] == "ya"])
FICHAS = {
    "@FM1@": figura("FM1"), "@FM2@": figura("FM2"),
    "@FM3@": figura("FM3"), "@FM4@": figura("FM4"),
    "@CATALOGO@": tablas_catalogo(),
    "@ESTADOS@": tabla_estados(),
    "@ANEXO_LEGAL@": anexo_legal(),
    "@ANEXO_CARTERA@": anexo_cartera(),
    "@ANEXO_TRIMESTRE@": anexo_trimestre(),
    "@TOTAL@": str(CAT["total"]),
    "@NGRUPOS@": str(len(CAT["grupos"])),
    "@SINCOSTE@": str(CAT["sin_coste"]),
    "@PCTSINCOSTE@": str(int(round(100 * CAT["sin_coste"] / CAT["total"]))),
    "@YA@": str(CAT["inmediatas"]),
    "@YA0@": str(ya0),
    "@CONCAMPANA@": str(CAT["con_campana"]),
    "@FUERA@": str(CAT["fuera_de_cartera"]),
    "@TECHO@": mil(CAT["techo_anual"]),
}
for marca, valor in FICHAS.items():
    cuerpo = cuerpo.replace(marca, valor)
# El sello de versión se estampa al final, así que sus marcas no cuentan aquí.
sobran = set(re.findall(r"@[A-Z_0-9]+@", cuerpo)) - {"@VERSION@", "@FECHA@", "@CORTA@"}
assert not sobran, "quedan marcas sin sustituir: %s" % sorted(sobran)

# ---------------------------------------------------------------- numeración de figuras
# Igual que en la Tesis: el número lo pone el generador, en el orden en que el
# lector encuentra las figuras. Escribirlo a mano es lo que deja una figura 2
# en sexto lugar en cuanto alguien reordena un apartado.
def numera(texto):
    n = 0

    def rotula(m):
        nonlocal n
        n += 1
        return re.sub(r"(<figcaption[^>]*>\s*<(?:b|strong)>)",
                      r"\g<1>Figura %d · " % n, m.group(0), count=1)

    texto = re.sub(r"<figure\b.*?</figure>", rotula, texto, flags=re.S)
    quedan = re.findall(r"<figcaption[^>]*>\s*<(?:b|strong)>(?!Figura \d)", texto)
    assert not quedan, "%d pie(s) de figura sin numerar" % len(quedan)
    return texto, n


cuerpo, n_figuras = numera(cuerpo)

salida = RAIZ / "marketing.html"
salida.write_text(sello(cabecera + "\n" + barra + "\n" + cuerpo + "\n\n" + script), encoding="utf-8")
print("marketing.html · %d acciones · %d figuras · %d KB"
      % (CAT["total"], n_figuras, salida.stat().st_size // 1024))
