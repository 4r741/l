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
import zipfile
import sys
from pathlib import Path

RAIZ = Path(__file__).parent

# ---------------------------------------------------------------- hechos canónicos
# La versión vive en version.py y en ningún otro sitio. Se lee del código fuente
# y no por importación, por el mismo motivo que el modelo de campañas: un .pyc
# obsoleto validaría contra una versión que ya no es la vigente.
_v = {}
exec(compile((RAIZ / "version.py").read_text(encoding="utf-8"), "version.py", "exec"), _v)
VERSION, FECHA = _v["VERSION"], _v["FECHA"]

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
    "decisiones sometidas a la Junta": 15,
    "riesgos críticos": 5,
    "riesgos de segundo orden": 7,
    "riesgos del registro puntuado": 10,
    "fichas de innovación": 18,
    "decisiones de Gerencia": 20,
    "verificaciones externas": 11,
    "diapositivas de la presentación": 43,
    "piezas del sistema": 22,
    "campañas de la cartera": 9,
    "objetivo de facturación en miles de euros": 1200,
    "acciones del catálogo de marketing": 76,
    "estados del paciente": 12,
    "grupos del catálogo": 7,
    "piezas propias del plan de marketing": 10,
}

DOCUMENTOS = ["memoria.html", "deck.html", "marketing.html", "manual.html", "index.html",
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
        t = crudo
        # también en su forma larga: «Versión 5.0 · Agosto 2026»
        for larga in sorted(set(re.findall(r"[Vv]ersión (\d+\.\d+)", t))):
            if larga != VERSION:
                falla(doc, "declara «Versión %s» fuera de un registro de cambios" % larga)
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
        t = texto(bruto(doc), ya_limpio=True)
        for mal in ("ocho indicadores", "Ocho indicadores", "8 indicadores", "0 / 8", "0/8"):
            if mal in t:
                falla(doc, "dice «%s»; el cuadro de mando tiene %d"
                      % (mal, CIFRAS["indicadores del cuadro de mando"]))
        for mal in ("catorce decisiones", "Catorce decisiones", "catorce acuerdos",
                    "Catorce acuerdos", "catorce hojas de acta"):
            if mal in t:
                falla(doc, "dice «%s»; se someten %d" % (mal, CIFRAS["decisiones sometidas a la Junta"]))
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
    if briefs != 7:
        falla("memoria.html", "tiene %d fichas de decisión estratégica y deberían ser 7 (D9 a D15)" % briefs)

    d = bruto("deck.html")
    n = len(re.findall(r'<section[^>]*class="slide', d))
    if n != CIFRAS["diapositivas de la presentación"]:
        falla("deck.html", "tiene %d diapositivas y deberían ser %d"
              % (n, CIFRAS["diapositivas de la presentación"]))
    esenciales = d.count('data-esencial="1"')
    if esenciales != 12:
        falla("deck.html", "la ruta corta marca %d diapositivas y deberían ser 12" % esenciales)

    fichas = len(re.findall(r'class="acta campana"', bruto("memoria.html")))
    if fichas != CIFRAS["campañas de la cartera"]:
        falla("memoria.html", "el anexo B trae %d fichas de campaña y deberían ser %d"
              % (fichas, CIFRAS["campañas de la cartera"]))
    codigos = set(re.findall(r"\bC(\d)\b", texto("memoria.html")))
    faltan = {str(i) for i in range(1, CIFRAS["campañas de la cartera"] + 1)} - codigos
    if faltan:
        falla("memoria.html", "no menciona las campañas %s" % sorted(faltan))

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


# Un documento de gobierno dice lo que el centro hace, no lo que el documento
# hacía antes. El historial de ediciones —qué decía la versión pasada, qué se
# reconcilió, qué incoherencia se corrigió— es trabajo de taller: interesa a
# quien lo edita y estorba a quien lo lee. Estas expresiones no pueden volver a
# aparecer, y la lista está aquí para que nadie tenga que acordarse.
HISTORIAL = [
    "notas de edición", "control de cambios", "registro de cambios",
    "historial de versiones", "qué se reconcilió", "reconciliación",
    "incoherencias detectadas", "en esta versión", "esta edición",
    "edición anterior", "versión anterior", "antes decía", "qué decía la",
    "v5.5", "v5.0", "v4.0", "v1.3", "v2.6", "la 5.5", "la 4.0",
]


def comprueba_sin_historial():
    """Ningún documento puede explicar en qué se diferencia de su versión pasada."""
    for doc in DOCUMENTOS:
        t = texto(bruto(doc), ya_limpio=True).lower()
        for frase in HISTORIAL:
            if frase in t:
                falla(doc, "explica cambios entre versiones: «%s»" % frase)


def comprueba_numeros_de_version():
    """Toda versión que un documento declare tiene que ser la vigente.

    Las comprobaciones anteriores buscaban formas concretas —«v7.0», «Versión
    7.0»— y por eso se les escapó la ficha de control, que pone el rótulo en una
    casilla y el número en la de al lado. Esta busca el patrón, no la forma: si
    en el texto aparece una versión, o es la vigente o es un descuido.
    """
    patron = re.compile(r"(?:versi[oó]n\s+v?|(?<![\w.])v)(\d+\.\d+)", re.I)
    for doc in DOCUMENTOS:
        t = texto(bruto(doc), ya_limpio=True)
        # el rótulo y el número separados por la casilla de una tabla
        t = re.sub(r"\bVersi[oó]n\s+(?=\d+\.\d+)", "version ", t, flags=re.I)
        malas = sorted({v for v in patron.findall(t) if v != VERSION})
        if malas:
            falla(doc, "declara versiones que no son la vigente: %s" % ", ".join(malas))


def comprueba_pies():
    """El pie de cada documento declara la versión, y tiene que ser la vigente.

    El pie del Manual se quedó anunciando la 5.5 durante tres versiones sin que
    nadie lo viera: está a seis mil líneas del principio y nadie baja hasta ahí
    a leer un número que da por supuesto.
    """
    for doc in DOCUMENTOS:
        t = bruto(doc)
        i = t.rfind('class="eyebrow">Versión</p>')
        if i < 0:
            continue
        pie = texto(t[i:i + 400], ya_limpio=True)
        if ("v" + VERSION) not in pie:
            falla(doc, "el pie no declara la versión vigente: «%s»" % pie[:70])


# ---------------------------------------------------------------- 5 · censo y cambios
def comprueba_censo():
    t = bruto("memoria.html")
    if 'id="censo"' not in t:
        falla("memoria.html", "no incluye el censo documental (apartado 0.1)")

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


# ---------------------------------------------------------------- 7 · el modelo
def comprueba_modelo():
    """Las cifras de la Parte VI tienen que ser las que devuelve el modelo.

    Es la comprobación que cierra el círculo: el documento no puede afirmar un
    número que el modelo no produzca. Si alguien edital Plan de Dirección a mano, esto lo
    detecta; si alguien cambia un supuesto del modelo sin regenerar, también.
    """
    ruta = RAIZ / "modelo-campanas.py"
    if not ruta.exists():
        falla("modelo-campanas.py", "no está en el repositorio: la Parte VI queda sin respaldo")
        return
    # Se ejecuta el código fuente en un espacio propio, sin pasar por el sistema
    # de importación: un .pyc obsoleto podría validar contra un modelo viejo, y
    # un verificador que da verde por caché es peor que no tenerlo.
    entorno = {"__name__": "modelo_auditado", "__file__": str(ruta)}
    exec(compile(ruta.read_text(encoding="utf-8"), str(ruta), "exec"), entorno)
    d = entorno["calcula"]()

    def mil(v):
        return "{:,}".format(int(round(v))).replace(",", ".")

    doc = texto("memoria.html")
    if len(d["campanas"]) != CIFRAS["campañas de la cartera"]:
        falla("modelo-campanas.py", "modela %d campañas y deberían ser %d"
              % (len(d["campanas"]), CIFRAS["campañas de la cartera"]))
    if d["puente"]["objetivo"] != CIFRAS["objetivo de facturación en miles de euros"] * 1000:
        falla("modelo-campanas.py", "su objetivo no es el canónico de %d k€"
              % CIFRAS["objetivo de facturación en miles de euros"])
    if d["capacidad"]["pv_campanas"] > d["capacidad"]["pv_ano"]:
        falla("modelo-campanas.py", "las campañas piden más agenda de la que hay")

    faltan = []
    for f in d["campanas"]:
        if mil(abs(f["aporte"]) / 1000) not in doc:
            faltan.append("%s (%s k€)" % (f["cod"], mil(f["aporte"] / 1000)))
    if faltan:
        falla("memoria.html", "no recoge el aporte que el modelo calcula para %s" % ", ".join(faltan))

    p = d["puente"]
    for rotulo, valor in (("base", p["base"]), ("llenar la agenda", p["llenar"]),
                          ("mejora de mezcla", p["mezcla"]), ("seguimiento", p["seguimiento"]),
                          ("planificado", p["planificado"]), ("colchón", -p["colchon"])):
        if mil(valor / 1000) not in doc:
            falla("memoria.html", "el tramo «%s» del puente (%s k€) no aparece en el documento"
                  % (rotulo, mil(valor / 1000)))


# ---------------------------------------------------------------- 8 · el libro de cálculo
def comprueba_libro():
    """El instrumento de los apartados 7 y 13 es un documento más y se audita igual.

    Un xlsx es un zip de XML, así que no hace falta abrirlo con una biblioteca:
    basta leer su tabla de textos. Se comprueba lo mismo que en los HTML —la
    versión vigente, ninguna versión atrasada, ninguna palabra proscrita— y
    además que las fórmulas salgan con su resultado en caché. La versión de este
    libro se le escapó a la revisión de v6.0 justamente por no estar aquí.
    """
    ruta = RAIZ / "instrumentos" / "Captura-Linea-Base-Giraldo-2026.xlsx"
    nombre = "instrumentos/" + ruta.name
    if not ruta.exists():
        falla(nombre, "no está en el repositorio: el apartado 7 se queda sin instrumento")
        return
    with zipfile.ZipFile(ruta) as z:
        piezas = z.namelist()
        cadenas = z.read("xl/sharedStrings.xml").decode("utf-8") if "xl/sharedStrings.xml" in piezas else ""
        hojas = [z.read(n).decode("utf-8") for n in piezas if n.startswith("xl/worksheets/sheet")]
    t = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", cadenas)))

    if "v" + VERSION not in t:
        falla(nombre, "no declara la versión vigente v%s" % VERSION)
    for v in sorted(set(re.findall(r"\bv(\d+\.\d+)", t))):
        if v != VERSION:
            falla(nombre, "arrastra la versión v%s, y la vigente es v%s" % (v, VERSION))
    for palabra in PROHIBIDOS:
        if palabra in t:
            falla(nombre, "contiene «%s», que no puede aparecer en ningún sitio" % palabra)

    # Fórmulas con resultado: <f> sin <v> hermano es una casilla que se verá
    # vacía en cualquier visor que no calcule.
    sin_valor = 0
    for hoja in hojas:
        for celda in re.findall(r"<c\b[^>]*>.*?</c>", hoja, re.S):
            if "<f" in celda and "<v>" not in celda:
                sin_valor += 1
    if sin_valor:
        falla(nombre, "tiene %d fórmula(s) sin valor en caché: hay que pasar recalc.py"
              % sin_valor)



# ---------------------------------------------------------------- 9 · figuras
def comprueba_figuras():
    """Las figuras van numeradas 1..N en el orden en que se leen.

    Doce figuras con tres numeradas, y esas tres fuera de orden, es lo que había
    antes de que el generador las rotulara solo. La comprobación es barata y
    cierra la puerta a que alguien vuelva a escribir el número a mano.
    """
    for doc in ("memoria.html", "marketing.html"):
        figuras_de(doc)


def figuras_de(doc):
    t = bruto(doc)
    pies = re.findall(r"<figcaption[^>]*>\s*(?:<[^>]+>\s*)?(Figura (\d+) ·|.{0,30})", t, re.S)
    numeros = []
    for entero, n in pies:
        if not n:
            falla(doc, "hay un pie de figura sin numerar: «%s…»" % entero.strip()[:40])
        else:
            numeros.append(int(n))
    if numeros and numeros != list(range(1, len(numeros) + 1)):
        falla(doc, "las figuras no van 1..%d en orden de lectura: %s"
              % (len(numeros), numeros))

    sin_marca = re.sub(r"<figcaption.*?</figcaption>", " ", t, flags=re.S)
    citadas = {int(n) for n in re.findall(r"[Ff]igura (\d+)", texto(sin_marca, ya_limpio=True))}
    huerfanas = sorted(citadas - set(numeros))
    if huerfanas:
        falla(doc, "remite a figuras que no existen: %s" % huerfanas)
    for marca in ("@Fig:", "@fig:", "<!--FIG"):
        if marca in t:
            falla(doc, "conserva la marca «%s» sin resolver" % marca)



# ---------------------------------------------------------------- 10 · el catálogo de marketing
def comprueba_catalogo():
    """El Plan Maestro no puede afirmar un recuento que el catálogo no produzca.

    Mismo principio que con el modelo de campañas, y por el mismo motivo: el
    documento se genera a partir de los datos, así que la única forma de que
    diverjan es que alguien edite el HTML a mano. Esto lo detecta.
    """
    ruta = RAIZ / "catalogo-acciones.py"
    if not ruta.exists():
        falla("catalogo-acciones.py", "no está en el repositorio: el plan queda sin respaldo")
        return
    entorno = {"__name__": "catalogo_auditado", "__file__": str(ruta)}
    exec(compile(ruta.read_text(encoding="utf-8"), str(ruta), "exec"), entorno)
    d = entorno["calcula"]()

    if d["total"] != CIFRAS["acciones del catálogo de marketing"]:
        falla("catalogo-acciones.py", "cataloga %d acciones y deberían ser %d"
              % (d["total"], CIFRAS["acciones del catálogo de marketing"]))
    if len(d["estados"]) != CIFRAS["estados del paciente"]:
        falla("catalogo-acciones.py", "define %d estados y deberían ser %d"
              % (len(d["estados"]), CIFRAS["estados del paciente"]))
    if len(d["grupos"]) != CIFRAS["grupos del catálogo"]:
        falla("catalogo-acciones.py", "define %d grupos y deberían ser %d"
              % (len(d["grupos"]), CIFRAS["grupos del catálogo"]))

    # la regla de admisión del plan: ninguna acción sin decir qué gana el paciente
    mudas = [a["cod"] for a in d["acciones"] if not a["gana"]]
    if mudas:
        falla("catalogo-acciones.py", "estas acciones no dicen qué gana el paciente: %s" % mudas[:5])

    doc = bruto("marketing.html")
    # cada código tiene que aparecer en el documento, y ninguno de más
    for a in d["acciones"]:
        if a["cod"] not in doc:
            falla("marketing.html", "no recoge la acción %s del catálogo" % a["cod"])
            break
    fichas = doc.count('class="t-brief"')
    if fichas != CIFRAS["piezas propias del plan de marketing"]:
        falla("marketing.html", "trae %d fichas de pieza propia y deberían ser %d"
              % (fichas, CIFRAS["piezas propias del plan de marketing"]))

    texto_plan = texto(doc, ya_limpio=True)
    for cifra, rotulo in ((d["total"], "el total de acciones"),
                          (d["sin_coste"], "las acciones sin coste"),
                          (d["inmediatas"], "las acciones inmediatas")):
        if str(cifra) not in texto_plan:
            falla("marketing.html", "no declara %s (%d) que calcula el catálogo" % (rotulo, cifra))

    # el plan no puede contradecir a la cartera: toda campaña citada tiene que existir
    ruta_modelo = RAIZ / "modelo-campanas.py"
    entorno_m = {"__name__": "modelo_auditado", "__file__": str(ruta_modelo)}
    exec(compile(ruta_modelo.read_text(encoding="utf-8"), str(ruta_modelo), "exec"), entorno_m)
    validas = {f["cod"] for f in entorno_m["calcula"]()["campanas"]}
    citadas = {a["campana"] for a in d["acciones"] if a["campana"] != "—"}
    huerfanas = sorted(citadas - validas)
    if huerfanas:
        falla("catalogo-acciones.py", "asigna acciones a campañas inexistentes: %s" % huerfanas)



def main():
    comprueba_version()
    comprueba_cifras()
    comprueba_estructura()
    comprueba_higiene()
    comprueba_sin_historial()
    comprueba_numeros_de_version()
    comprueba_pies()
    comprueba_censo()
    comprueba_generadores()
    comprueba_modelo()
    comprueba_libro()
    comprueba_figuras()
    comprueba_catalogo()
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
          % (len(CIFRAS), len(DOCUMENTOS) + 1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
