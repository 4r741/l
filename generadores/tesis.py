#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ensambla memoria.html, el Plan de Dirección v@VERSION@.

Conserva íntegros los diez apartados de la Memoria v1.0 —renumerados— y los
reordena en seis partes, intercalando la capa estratégica y la Parte VI, cuyas
cifras vienen del modelo. Los bloques de contenido están en fuentes/; el
sistema de diseño y el guion de comportamiento se toman del Manual Maestro.
"""
import pathlib
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


# ---------------------------------------------------------------- cabecera
manual = (RAIZ / "manual.html").read_text(encoding="utf-8")
i = manual.index("<body>")
cabecera = manual[:i + len("<body>")]
cabecera = cabecera.replace("<title>Manual Maestro Giraldo</title>",
                            "<title>Plan de Dirección Giraldo</title>")
cabecera = re.sub(r'<meta name="description" content="[^"]*">',
                  '<meta name="description" content="Plan de Dirección del Centro de '
                  'Excelencia Implantológica Giraldo: posición competitiva, foso, sistema '
                  'operativo, economía unitaria y escenarios, creación de valor de empresa, '
                  'escalado, pre-mortem, asignación de capital, el puente hasta el objetivo de 1,2 M€ '
                  'con su cartera de nueve campañas, y las quince decisiones que '
                  'se someten a la Junta Directiva.">',
                  cabecera, count=1)
assert "Plan de Dirección Giraldo" in cabecera

editorial = (SP / "editorial.css").read_text(encoding="utf-8")
k = cabecera.rindex("</style>")
cabecera = cabecera[:k] + editorial + "\n" + cabecera[k:]

script = manual[manual.index("<script>\n(function(){"):]

# ---------------------------------------------------------------- figuras
figuras = "\n".join((SP / n).read_text(encoding="utf-8")
                    for n in ("figuras-1-3.html", "figuras-4-6.html",
                              "figuras-7.html", "figuras-8-12.html"))


def figura(marca):
    return figuras.split("<!--%s-->" % marca)[1].split("<!--")[0].strip()


# ---------------------------------------------------------------- bloques v1
def trocear(texto, patron):
    """Divide un cuerpo en bloques rotulados por su comentario de sección."""
    piezas = re.split(patron, texto)
    return {piezas[n].strip(): piezas[n + 1] for n in range(1, len(piezas), 2)}


v1 = {}
for nombre in ("tesis-01-apertura.html", "tesis-02-linea-riesgos.html", "tesis-03-decisiones.html"):
    v1.update(trocear((SP / nombre).read_text(encoding="utf-8"),
                      r"<!-- ={5,} (.+?) ={5,} -->"))
esperados = {"PORTADA", "CONTROL", "1 · RESUMEN", "2 · TESIS", "3 · SISTEMA",
             "4 · LÍNEA BASE", "5 · RIESGOS", "6 · CUADRO DE MANDO", "7 · PALANCAS",
             "8 · HOJA DE RUTA", "9 · DECISIONES", "10 · SUPUESTOS", "CIERRE"}
assert esperados <= set(v1), esperados - set(v1)

# el cierre arrastra </main> y el pie: se separan para recolocarlos al final
cierre, pie = v1["CIERRE"].split("</main>", 1)
pie = "</main>" + pie

# ---------------------------------------------------------------- renumerado
# Vive en renum_apartados.py, compartido con la presentación: estaba duplicado
# en los dos, y con el signo § metido en el patrón.
import sys as _sys
_sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from renum_apartados import renumera as renumerar


for clave in v1:
    v1[clave] = renumerar(v1[clave])
cierre, pie = renumerar(cierre), renumerar(pie)

# ---------------------------------------------------------------- bloques v2
def trocear_nuevos(nombre):
    return trocear((SP / nombre).read_text(encoding="utf-8"), r"<!--@(\w+)-->")


v2 = {}
for nombre in ("tesis-p1-posicion.html", "tesis-p2-p3-sistema-economia.html", "tesis-p4-p5-riesgo-decision.html", "tesis-fichas-d9-d14.html",
               "tesis-diccionario-valoracion.html", "tesis-riesgos-trazabilidad.html", "tesis-instrumento.html", "tesis-censo-cambios.html", "tesis-p6-generada.html", "tesis-ficha-d15.html", "tesis-supuestos-campanas.html",
               "tesis-anexo-b-campanas.html", "tesis-anexo-a-actas.html"):
    v2.update(trocear_nuevos(nombre))

# las seis fichas nuevas se cosen dentro del apartado de decisiones, antes del
# formato de registro del acuerdo, para que las catorce viajen juntas
ancla = '    <h3 style="font-size:var(--step-1);margin:2.8rem 0 .6rem">Formato de registro'
assert v1["9 · DECISIONES"].count(ancla) == 1
v1["9 · DECISIONES"] = v1["9 · DECISIONES"].replace(
    ancla, v2["BRIEFS"] + v2["D15"] + "\n" + ancla, 1)
v1["9 · DECISIONES"] = (v1["9 · DECISIONES"]
                        .replace("<h2>Ocho acuerdos</h2>", "<h2>Quince acuerdos</h2>")
                        .replace("apartado 17 · Decisiones que se someten a la Junta",
                                 "apartado 17 · Decisiones que se someten a la Junta")
                        .replace("Ninguna requiere información adicional a la contenida en esta memoria.",
                                 "Las ocho primeras resuelven la operación; las siete últimas fijan las "
                                 "reglas con las que se decidirá lo que aún no está sobre la mesa, "
                                 "incluida la cifra a la que se dirige todo. "
                                 "Ninguna requiere información adicional a la contenida en este documento."))

# los bloques de la segunda capa se cosen dentro del apartado al que pertenecen,
# antes del ancla indicada, para que cada uno viaje con su materia
COSIDOS = [
    ("6 · CUADRO DE MANDO", "KPIDEF",
     '    <h3 style="font-size:var(--step-1);margin:2.8rem 0 .6rem">Lo que cuesta un descuento'),
    ("5 · RIESGOS", "RIESGOSPUNT",
     '      <div>\n        <div class="rulebox" style="max-width:none">\n'
     '          <p class="eyebrow">La única regla que detiene la clínica</p>'),
    ("CONTROL", "CENSO", "__final__"),
    ("10 · SUPUESTOS", "SUPUESTOS6", "__final__"),
    ("4 · LÍNEA BASE", "INSTRUMENTO", "__final__"),
    ("9 · DECISIONES", "INACCION",
     '    <h3 style="font-size:var(--step-1);margin:2.8rem 0 .6rem">Formato de registro'),
]
for clave, bloque, ancla in COSIDOS:
    if ancla == "__final__":                      # al pie del apartado, antes de cerrarlo
        cierre_ap = "  </div>\n</section>"
        assert v1[clave].rstrip().endswith(cierre_ap), clave
        v1[clave] = v1[clave].rstrip()[:-len(cierre_ap)] + v2[bloque].rstrip() + "\n" + cierre_ap + "\n"
        continue
    assert v1[clave].count(ancla) == 1, (clave, bloque)
    v1[clave] = v1[clave].replace(ancla, v2[bloque].rstrip() + "\n\n" + ancla, 1)

# la comprobación en directo va tras la matriz de sensibilidad, y la aritmética
# de valoración tras la escalera de valor: ambas dentro de apartados nuevos
ancla_calc = '    <div class="rulebox" style="max-width:none">\n      <p class="eyebrow">La lectura de gerencia</p>'
assert v2["UNIDAD"].count(ancla_calc) == 1
v2["UNIDAD"] = v2["UNIDAD"].replace(ancla_calc, v2["CALC"].rstrip() + "\n\n" + ancla_calc, 1)

ancla_valor = '    <div class="callout" style="max-width:none">\n      <p class="eyebrow">Lo que esto implica para esta Junta</p>'
assert v2["ACTIVO"].count(ancla_valor) == 1
v2["ACTIVO"] = v2["ACTIVO"].replace(ancla_valor, v2["VALOR"].rstrip() + "\n\n" + ancla_valor, 1)

ancla_traza = ('          <tr><td class="num">D14</td>')
assert v2["TRAZA"].count(ancla_traza) == 1
v2["TRAZA"] = v2["TRAZA"].replace(
    "</tbody>", v2["TRAZA15"].strip() + "\n        </tbody>", 1)

# ---------------------------------------------------------------- montaje
orden = [
    (SP / "tesis-portada.html").read_text(encoding="utf-8"),
    v1["CONTROL"], v1["1 · RESUMEN"],
    v2["P1"], v1["2 · TESIS"], v2["MAPA"], v2["FOSO"],
    v2["P2"], v1["3 · SISTEMA"], v2["INNOVACION"],
    v2["P3"], v1["4 · LÍNEA BASE"], v2["UNIDAD"], v2["ACTIVO"], v2["ESCALADO"],
    v2["P4"], v1["5 · RIESGOS"], v2["PREMORTEM"], v1["6 · CUADRO DE MANDO"],
    v2["P5"], v1["7 · PALANCAS"], v2["CAPITAL"], v1["8 · HOJA DE RUTA"],
    v1["9 · DECISIONES"], v1["10 · SUPUESTOS"], v2["TRAZA"],
    v2["P6"], v2["PUENTE"], v2["CARTERA"], v2["CALENDARIO"], v2["CIERTO"],
    v2["ACTAS"], v2["CAMPANAS"],
    cierre, pie,
]
cuerpo = "\n\n".join(bloque.strip("\n") for bloque in orden)

# El Plan Maestro de Marketing entra en la barra del Plan de Dirección junto a los
# demás enlaces cruzados: un documento al que no se llega desde ningún
# sitio es un documento que no existe.
cruzado = '<a class="crosslink" href="otros.html">Otros documentos</a>'
assert cuerpo.count(cruzado) >= 1
cuerpo = cuerpo.replace(cruzado, cruzado + '\n      '
                        '<a class="crosslink" href="marketing.html">Plan de Marketing</a>', 1)

# ---------------------------------------------------------------- numeración de figuras
# Las figuras se numeran solas, en el orden en que el lector las encuentra. El
# número escrito a mano se queda atrás en cuanto se reordena un apartado: así
# es como este Plan de Dirección llegó a tener doce figuras con tres numeradas y el orden
# roto. Las ranuras F1…F12 son nombres internos del generador; lo que el lector
# ve —«Figura 1 ·»— y lo que dice cualquier remisión salen los dos de aquí.
def numera_figuras(texto):
    orden = {}
    for marca in re.findall(r"<!--FIG(\d+)-->", texto):
        orden.setdefault("F" + marca, len(orden) + 1)

    def rotula(m):
        bloque = m.group(0)
        marca = re.search(r"<!--FIG(\d+)-->", bloque)
        if not marca:
            return bloque
        n = orden["F" + marca.group(1)]
        # el rótulo es el primer <b> o <strong> del pie, se escriba como se escriba
        return re.sub(r"(<figcaption[^>]*>\s*<(?:b|strong)>)",
                      r"\1Figura %d · " % n, bloque, count=1)

    texto = re.sub(r"<figure\b.*?</figure>", rotula, texto, flags=re.S)
    quedan = re.findall(r"<figcaption[^>]*>\s*<(?:b|strong)>(?!Figura \d)", texto)
    assert not quedan, "%d pie(s) de figura sin numerar" % len(quedan)

    # remisiones simbólicas: @Fig:F3@ se resuelve al número que le haya tocado
    def remite(m):
        return ("Figura " if m.group(1) == "F" else "figura ") + str(orden[m.group(2)])

    texto = re.sub(r"@([Ff])ig:(F\d+)@", remite, texto)
    assert "@Fig:" not in texto and "@fig:" not in texto
    return texto, orden


cuerpo, FIGURAS = numera_figuras(cuerpo)

for n in range(1, 13):
    cuerpo = cuerpo.replace("<!--FIG%d-->" % n, figura("F%d" % n))
assert "<!--FIG" not in cuerpo

# el documento cambia de nombre y de versión en todas sus referencias internas
cuerpo = (cuerpo
          .replace("Memoria de Dirección v1.0", "Plan de Dirección v@VERSION@")
          .replace("Memoria de Dirección para la Junta Directiva",
                   "Plan de Dirección para la Junta Directiva")
          .replace("v1.0 · @FECHA@<br>Revisión trimestral",
                   "v@VERSION@ · @FECHA@<br>Revisión trimestral"))

(RAIZ / "memoria.html").write_text(sello(
    cabecera + "\n\n" + cuerpo + "\n\n" + script.replace(
        "</body>", (SP / "calculadora.js").read_text(encoding="utf-8") + "</body>")),
    encoding="utf-8")
print("memoria.html ·", (RAIZ / "memoria.html").stat().st_size // 1024, "KB")
