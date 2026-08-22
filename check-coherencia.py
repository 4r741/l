#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verifica que el sistema documental no se contradiga a sí mismo.

    python3 check-coherencia.py

Un sistema que exige listas de verificación no puede fiarse de la memoria para
comprobar su propia coherencia. Este guion afirma los hechos canónicos —cuántas
fases, cuántos indicadores, qué versión— y falla si algún documento dice otra
cosa. Sale con código 1 si encuentra cualquier discrepancia.
"""
import html
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).parent

# ---------------------------------------------------------------- hechos canónicos
VERSION = "6.0"
FECHA = "Agosto 2026"

CIFRAS = {
    "partes numeradas del Manual": 8,
    "fases del recorrido del paciente": 14,
    "fases de la primera visita": 12,
    "puntos de verificación": 322,
    "puestos normalizados": 6,
    "documentos troncales": 3,
    "documentos de apoyo": 14,
    "documentos operativos": 17,
    "indicadores del cuadro de mando": 10,
    "decisiones sometidas a la Junta": 14,
    "riesgos críticos": 5,
    "riesgos de segundo orden": 7,
    "riesgos del registro puntuado": 10,
    "fichas de innovación": 18,
    "decisiones de Gerencia": 20,
    "verificaciones externas": 11,
    "diapositivas de la presentación": 34,
    "piezas del sistema": 21,
    "incoherencias reconciliadas en v6.0": 12,
}

DOCUMENTOS = ["memoria.html", "deck.html", "manual.html", "index.html",
              "otros.html", "otros.html", "inicio.html", "instrumentos/captura.html"]
DOCUMENTOS = list(dict.fromkeys(DOCUMENTOS))

# Versiones que sí pueden aparecer: son referencias históricas explícitas, no
# la versión vigente de ningún documento.
# Solo se admite una versión antigua si el propio texto la presenta como pasada.
VERSIONES_HISTORICAS = {"Sustituye al", "sustituye al", "Ex ", "anterior"}

PROHIBIDOS = ["Höllenback", "Hollenback", "Hermes"]

fallos = []
avisos = []


def texto(ruta, ya_limpio=False):
    t = ruta if ya_limpio else (RAIZ / ruta).read_text(encoding="utf-8")
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", t, flags=re.S)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t)))


def bruto(ruta):
    return (RAIZ / ruta).read_text(encoding="utf-8")


def sin_historia(t):
    """Quita el registro de cambios: ahí las versiones viejas son el contenido."""
    i = t.find('id="cambios"')
    if i < 0:
        return t
    fin = t.find("</table>", i)
    return t[:i] + t[fin:] if fin > 0 else t[:i]


def falla(doc, que):
    fallos.append("%-26s %s" % (doc, que))


def avisa(doc, que):
    avisos.append("%-26s %s" % (doc, que))


# ---------------------------------------------------------------- 1 · versión única
def comprueba_version():
    for doc in DOCUMENTOS:
        crudo = bruto(doc)
        if "v" + VERSION not in crudo:
            falla(doc, "no declara la versión vigente v%s" % VERSION)
        t = sin_historia(crudo)
        for otra in sorted(set(re.findall(r"v\d+\.\d+", t))):
            if otra == "v" + VERSION:
                continue
            contextos = re.findall(r".{60}" + re.escape(otra), t)
            if all(any(frase in c for frase in VERSIONES_HISTORICAS) for c in contextos):
                continue
            falla(doc, "arrastra la versión %s, que ya no es la vigente" % otra)


# ---------------------------------------------------------------- 2 · cifras
def comprueba_cifras():
    # ningún documento puede afirmar un número de indicadores distinto de diez
    for doc in DOCUMENTOS:
        t = texto(sin_historia(bruto(doc)), ya_limpio=True)
        for mal in ("ocho indicadores", "Ocho indicadores", "8 indicadores", "0 / 8", "0/8"):
            if mal in t:
                falla(doc, "dice «%s»; el cuadro de mando tiene %d"
                      % (mal, CIFRAS["indicadores del cuadro de mando"]))
        for mal in ("ocho decisiones", "Ocho decisiones", "ocho acuerdos", "Ocho acuerdos"):
            if mal in t and "ocho primeras" not in t.lower():
                falla(doc, "dice «%s»; se someten %d" % (mal, CIFRAS["decisiones sometidas a la Junta"]))

    # el censo documental tiene que cuadrar
    if CIFRAS["documentos troncales"] + CIFRAS["documentos de apoyo"] != CIFRAS["documentos operativos"]:
        falla("censo", "troncales + apoyo no suman los documentos operativos")

    # otros.html debe contener exactamente los documentos de apoyo declarados
    t = texto("otros.html")
    numerados = set(int(n) for n in re.findall(r"Documento (\d+)", t))
    esperados = set(range(1, CIFRAS["documentos de apoyo"] + 1))
    if numerados != esperados:
        falla("otros.html", "sus documentos numerados son %s y deberían ser 1–%d"
              % (sorted(numerados), CIFRAS["documentos de apoyo"]))


# ---------------------------------------------------------------- 3 · estructura
def filas(doc, marca, hasta="</table>"):
    t = bruto(doc)
    i = t.find(marca)
    if i < 0:
        return None
    bloque = t[i:t.find(hasta, i)]
    return bloque.count("<tr>") - 1        # menos la fila de cabecera


def comprueba_estructura():
    n = filas("memoria.html", "Diccionario de indicadores")
    if n != CIFRAS["indicadores del cuadro de mando"]:
        falla("memoria.html", "el diccionario define %s indicadores y deberían ser %d"
              % (n, CIFRAS["indicadores del cuadro de mando"]))
    n = filas("memoria.html", "Registro puntuado")
    if n != CIFRAS["riesgos del registro puntuado"]:
        falla("memoria.html", "el registro puntúa %s riesgos y deberían ser %d"
              % (n, CIFRAS["riesgos del registro puntuado"]))

    t = bruto("memoria.html")
    actas = t.count('class="acta"')
    if actas != CIFRAS["decisiones sometidas a la Junta"]:
        falla("memoria.html", "el cuadernillo trae %d hojas de acta y deberían ser %d"
              % (actas, CIFRAS["decisiones sometidas a la Junta"]))
    briefs = len(re.findall(r"<b>D\d+ · ", t))
    codigos = set(re.findall(r"\bD(\d{1,2})\b", texto("memoria.html")))
    faltan = {str(i) for i in range(1, CIFRAS["decisiones sometidas a la Junta"] + 1)} - codigos
    if faltan:
        falla("memoria.html", "no menciona las decisiones %s" % sorted(faltan, key=int))
    if briefs != 6:
        avisa("memoria.html", "tiene %d fichas de decisión en detalle (se esperaban 6)" % briefs)

    d = bruto("deck.html")
    n = len(re.findall(r'<section[^>]*class="slide', d))
    if n != CIFRAS["diapositivas de la presentación"]:
        falla("deck.html", "tiene %d diapositivas y deberían ser %d"
              % (n, CIFRAS["diapositivas de la presentación"]))
    esenciales = d.count('data-esencial="1"')
    if esenciales != 12:
        falla("deck.html", "la ruta corta marca %d diapositivas y deberían ser 12" % esenciales)

    c = bruto("instrumentos/captura.html")
    ind = len(re.findall(r'tr data-fila="\d+"', c))
    if ind != CIFRAS["indicadores del cuadro de mando"]:
        falla("instrumentos/captura.html", "captura %d indicadores y deberían ser %d"
              % (ind, CIFRAS["indicadores del cuadro de mando"]))


# ---------------------------------------------------------------- 4 · higiene
def comprueba_higiene():
    for doc in DOCUMENTOS:
        t = bruto(doc)
        for palabra in PROHIBIDOS:
            if palabra in t:
                falla(doc, "contiene «%s», que no puede aparecer en ningún sitio" % palabra)
        if "prefers-color-scheme" in t or 'data-theme' in t:
            falla(doc, "reintroduce el modo oscuro")
        anclas = set(re.findall(r'\sid="([^"]+)"', t))
        rotas = sorted({h for h in re.findall(r'href="#([^"]+)"', t) if h not in anclas})
        if rotas:
            falla(doc, "tiene anclas rotas: %s" % rotas[:5])


# ---------------------------------------------------------------- 5 · censo y cambios
def comprueba_censo():
    t = bruto("memoria.html")
    for ancla, que in (('id="censo"', "el censo documental (§0.1)"),
                       ('id="cambios"', "el registro de cambios (§0.2)")):
        if ancla not in t:
            falla("memoria.html", "no incluye %s" % que)
    n = filas("memoria.html", 'id="cambios"')
    if n != CIFRAS["incoherencias reconciliadas en v6.0"]:
        falla("memoria.html", "el registro de cambios lista %s reconciliaciones y deberían ser %d"
              % (n, CIFRAS["incoherencias reconciliadas en v6.0"]))

    # la aritmética del censo tiene que aparecer y cuadrar
    censo = texto(bruto("memoria.html"), ya_limpio=True)
    if str(CIFRAS["piezas del sistema"]) not in censo:
        falla("memoria.html", "el censo no declara las %d piezas del sistema"
              % CIFRAS["piezas del sistema"])

    # el Manual y la portada tienen que contar sus partes igual
    for doc in ("manual.html", "inicio.html"):
        d = texto(doc)
        if "10 partes" in d or "diez partes" in d.lower():
            falla(doc, "atribuye al Manual diez partes; el Manual declara %d"
                  % CIFRAS["partes numeradas del Manual"])
        if "%d partes" % CIFRAS["partes numeradas del Manual"] not in d:
            avisa(doc, "no declara las %d partes del Manual" % CIFRAS["partes numeradas del Manual"])

    # «el recorrido» nombra las catorce fases del Manual, no las doce del Protocolo
    prot = texto("index.html")
    for mal in ("Las doce fases, una por una", "Lo que se cumple en las doce fases</"):
        if mal in prot:
            falla("index.html", "usa «recorrido» para las doce fases de la primera visita")


# ---------------------------------------------------------------- 6 · generadores
def comprueba_generadores():
    """Los archivos que producen build-export y build-pdf llevan la versión vigente."""
    corto = VERSION.split(".")[0]
    for guion, patron in (("build-pdf.py", r'"[\w-]+-v(\d+\.\d+)\.pdf"'),
                          ("build-export.py", r'"[\w-]+-v(\d+)\.html"')):
        ruta = RAIZ / guion
        if not ruta.exists():
            avisa(guion, "no está en el repositorio")
            continue
        for v in sorted(set(re.findall(patron, ruta.read_text(encoding="utf-8")))):
            if v not in (VERSION, corto):
                falla(guion, "genera archivos marcados v%s, y la versión vigente es v%s" % (v, VERSION))


def main():
    comprueba_version()
    comprueba_cifras()
    comprueba_estructura()
    comprueba_higiene()
    comprueba_censo()
    comprueba_generadores()
    print("Coherencia del sistema documental · versión canónica v%s · %s\n" % (VERSION, FECHA))
    for a in avisos:
        print("  aviso   " + a)
    if fallos:
        print()
        for f in fallos:
            print("  FALLO   " + f)
        print("\n%d incoherencia(s). El sistema no puede publicarse así." % len(fallos))
        return 1
    print("  Sin incoherencias: %d hechos canónicos verificados en %d documentos."
          % (len(CIFRAS), len(DOCUMENTOS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
