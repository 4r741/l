#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""centro.html: el sistema entero, completo, en un sitio que se puede recorrer.

    python3 build-sitio.py

Esto no es un resumen ni una selección. Es el sistema documental completo —los
ocho documentos, con todos sus apartados, todas sus tablas, todas sus fichas y
todas sus diapositivas— puesto en una sola página que se lee como se lee un
sitio: un índice completo delante, un apartado cada vez, un buscador que entra
en el texto y no solo en los títulos, y un hilo continuo que va del primer
apartado del Plan de Dirección al último de la hoja de captura sin saltar
nunca fuera.

La literatura no se toca: se recoge. Cada apartado viaja tal como está escrito
en su documento, con su número, su rótulo y la parte a la que pertenece, que es
lo que ya declara el propio documento. Lo único que se añade es el armazón para
recorrerlo.
"""
import html as H
import collections
import json
import math
import pathlib
import re
import sys

import imagenes

RAIZ = pathlib.Path(__file__).parent
sys.path.insert(0, str(RAIZ))

_v = {"__name__": "version_sitio", "__file__": "version.py"}
exec(compile((RAIZ / "version.py").read_text(encoding="utf-8"), "version.py", "exec"), _v)
VERSION, FECHA = _v["VERSION"], _v["FECHA"]

# ---------------------------------------------------------------------------
#  Los ocho documentos, en el orden del sistema
# ---------------------------------------------------------------------------
#  archivo, rótulo, clase, qué es, marca de identificadores
DOCUMENTOS = [
    ("memoria.html", "Plan de Dirección", "Gobierno",
     "Qué creemos, qué apostamos y las quince decisiones que se someten a la Junta.", "a"),
    ("deck.html", "Presentación de Junta", "Derivado",
     "Las cuarenta y tres diapositivas de la sesión, extraídas del Plan de Dirección.", "b"),
    ("protocolos.html", "Protocolos por puesto", "Vista operativa",
     "El protocolo del centro visto desde cada uno de los seis puestos.", "c"),
    ("index.html", "Protocolo de Primera Visita", "Troncal",
     "Las doce fases de la primera visita, minuto a minuto.", "d"),
    ("manual.html", "Manual Maestro de Operaciones", "Troncal",
     "Las catorce fases del recorrido, los seis puestos y la puesta en marcha.", "e"),
    ("marketing.html", "Plan Maestro de Marketing", "Plan",
     "Setenta y seis acciones sobre los doce estados del paciente.", "f"),
    ("otros.html", "Otros documentos del sistema", "Troncal",
     "Los catorce documentos de apoyo, del compendio maestro al programa de cuidado.", "g"),
    ("instrumentos/captura.html", "Los números del centro", "Instrumento",
     "Los diez indicadores y los cinco números, mes a mes.", "h"),
]

# Lo que hay además de esta página. Nombre, qué es y si se descarga o se abre.
ENTREGA = [
    ("centro.html", "web", "El sistema completo, en un sitio",
     "Esta misma página: los ocho documentos y sus apartados, con índice, buscador y glosario.", False),
    ("Giraldo-TODO-EN-UNO-v8.html", "web", "Los ocho documentos en una página",
     "El archivo único, con el conmutador de documentos y el tablero de cada uno.", False),
    ("Sistema-Documental-Giraldo-v8.0.pdf", "pdf", "El sistema encuadernado",
     "630 páginas con portada, índice paginado y un marcador por documento.", True),
    ("Sistema-Documental-Giraldo-v8.0.docx", "word", "El sistema en Word",
     "Índice automático, 335 tablas y las 23 figuras incrustadas.", True),
]

FUENTES = {}


def fuente(doc):
    if doc not in FUENTES:
        FUENTES[doc] = (RAIZ / doc).read_text(encoding="utf-8")
    return FUENTES[doc]


# ---------------------------------------------------------------------------
#  Recoger. Un documento se parte en apartados; ninguno se queda fuera.
# ---------------------------------------------------------------------------
ETIQUETA = re.compile(r"<([a-zA-Z][\w-]*)")


def elemento(t, ini):
    """El elemento que empieza en «ini», entero y con las etiquetas cuadradas."""
    nombre = ETIQUETA.match(t, ini).group(1)
    abre = re.compile(r"<%s\b" % re.escape(nombre), re.I)
    cierra = re.compile(r"</%s\s*>" % re.escape(nombre), re.I)
    hondo, pos = 0, ini
    while True:
        a, c = abre.search(t, pos), cierra.search(t, pos)
        if not c:
            return None
        if a and a.start() < c.start():
            hondo += 1
            pos = a.end()
            continue
        hondo -= 1
        pos = c.end()
        if hondo == 0:
            return t[ini:pos]


def dentro(elem):
    """El contenido de un elemento, sin su etiqueta de fuera."""
    i = elem.index(">") + 1
    j = elem.rindex("<")
    return elem[i:j]


# Las etiquetas que van dentro de una línea no separan palabras: quitar un
# <em> y dejar un espacio convertía «sistema operativo, no clínica» en «sistema
# operativo , no clínica». El <br> sí separa, porque parte el renglón.
ENLINEA = {"a", "abbr", "b", "bdi", "bdo", "cite", "code", "data", "dfn", "em", "i", "kbd",
           "mark", "q", "rp", "rt", "ruby", "s", "samp", "small", "span", "strong", "sub",
           "sup", "time", "u", "var", "wbr"}


def sin_marcas(html):
    """El texto llano, para el buscador y para contar."""
    t = re.sub(r"<(script|style)\b.*?</\1>", " ", html, flags=re.S | re.I)
    t = re.sub(r"</?([a-zA-Z][\w-]*)[^>]*>",
               lambda m: "" if m.group(1).lower() in ENLINEA else " ", t)
    t = re.sub(r"<[^>]+>", " ", t)
    t = H.unescape(t)
    return re.sub(r"\s+", " ", t).strip()


AP = re.compile(r'<article class="ap"[^>]*>', re.I)


def de_apartados(doc):
    """Los documentos ya vienen partidos en apartados por el propio sistema."""
    t = fuente(doc)
    piezas = []
    for m in AP.finditer(t):
        entero = elemento(t, m.start())
        if entero is None:
            continue
        atr = dict(re.findall(r'data-([\w-]+)="([^"]*)"', m.group(0)))
        piezas.append({
            "id": atr.get("ap", ""),
            "n": atr.get("n", ""),
            "rotulo": H.unescape(atr.get("rotulo", "")) or "Apartado",
            "grupo": H.unescape(atr.get("grupo", "")) or "",
            "html": dentro(entero),
        })
    return piezas


def de_secciones(doc, saltar=()):
    """Los que no se parten —llevan su propio mando dentro— por secciones."""
    t = fuente(doc)
    ini = t.index("<main")
    ini = t.index(">", ini) + 1
    fin = t.index("</main>")
    cuerpo = t[ini:fin]
    piezas = []
    for m in re.finditer(r'<section\b[^>]*\bid="([^"]+)"', cuerpo):
        # solo las de primer nivel: las de dentro viajan con la suya
        if any(z["desde"] < m.start() < z["hasta"] for z in piezas):
            continue
        ident = m.group(1)
        entero = elemento(cuerpo, m.start())
        if entero is None or ident in saltar:
            continue
        rot = re.search(r"<h[12][^>]*>(.*?)</h[12]>", entero, re.S)
        ceja = re.search(r'<p class="eyebrow"[^>]*>(.*?)</p>', entero, re.S)
        piezas.append({
            "id": ident,
            "n": "",
            "rotulo": sin_marcas(rot.group(1)) if rot else ident,
            "grupo": sin_marcas(ceja.group(1))[:60] if ceja else "",
            "html": entero,
            "desde": m.start(), "hasta": m.start() + len(entero),
        })
    for z in piezas:
        z.pop("desde", None), z.pop("hasta", None)
    return piezas


def de_diapositivas(doc):
    """La presentación: las cuarenta y tres, en un apartado por bloque de guion.

    Cada diapositiva lleva su minuto y su rótulo; agruparlas por el minuto que
    marca el guion del ponente sería inventar una estructura que el documento no
    tiene. Van todas, en orden, en un solo apartado que se recorre entero, que
    es exactamente como se pasa una presentación.
    """
    t = fuente(doc)
    trozos = []
    for m in re.finditer(r'<section[^>]*class="[^"]*slide[^"]*"[^>]*>', t):
        entero = elemento(t, m.start())
        if entero:
            trozos.append(entero)
    return [{
        "id": "presentacion",
        "n": "",
        "rotulo": "Las cuarenta y tres diapositivas, en orden",
        "grupo": "La sesión",
        "html": '<div class="deck deck--sitio">%s</div>' % "\n".join(trozos),
    }]


# ---------------------------------------------------------------------------
#  El glosario: no se inventa, se recoge del propio Manual
# ---------------------------------------------------------------------------
#  El Manual Maestro trae dos glosarios escritos —el de roles, en su Parte I, y
#  el de términos, en el Anexo 10— y el Protocolo de Primera Visita trae el
#  suyo. De ahí salen las definiciones que aparecen al pulsar una sigla en
#  cualquier punto del sistema: son las del documento, palabra por palabra, no
#  una redacción nueva.
GLOSARIOS = [
    ("manual.html", "m-3-glosario-roles", "Manual Maestro · Glosario de roles"),
    ("manual.html", "m-anexo-10-glosario-terminos-ampliacion", "Manual Maestro · Anexo 10"),
    ("index.html", "p-anexo-e-glosario", "Protocolo de Primera Visita · Anexo E"),
]

# Siglas que no se marcan aunque estén definidas: son palabras corrientes o
# aparecen tantas veces que la página se llenaría de subrayados.
NO_MARCAR = {"PV", "DR", "DC", "REC", "AUX", "HIG"}


def glosario():
    """{sigla: (definición, de dónde sale)} sacado de los glosarios escritos."""
    voces = {}
    for doc, ancla, procede in GLOSARIOS:
        t = fuente(doc)
        i = t.find('id="%s"' % ancla)
        if i < 0:
            continue
        trozo = t[i:i + 14000]
        # forma de tabla: rol | abreviatura | función
        for fila in re.findall(r"<tr>(.*?)</tr>", trozo, re.S):
            celdas = [sin_marcas(c) for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", fila, re.S)]
            if len(celdas) >= 3 and 1 <= len(celdas[1]) <= 5 and celdas[1].isupper():
                voces.setdefault(celdas[1], ("%s — %s" % (celdas[0], celdas[2]), procede))
        # forma de rejilla: <div><h5>voz</h5><p>definición</p></div>
        for h, d in re.findall(r"<h[45][^>]*>(.*?)</h[45]>\s*<p[^>]*>(.*?)</p>", trozo, re.S):
            clave, valor = sin_marcas(h), sin_marcas(d)
            if clave and valor and len(clave) <= 34:
                voces.setdefault(clave, (valor, procede))
        # forma de lista de definiciones
        for dt, dd in re.findall(r"<dt[^>]*>(.*?)</dt>\s*<dd[^>]*>(.*?)</dd>", trozo, re.S):
            clave, valor = sin_marcas(dt), sin_marcas(dd)
            if clave and valor and len(clave) <= 34:
                voces.setdefault(clave, (valor, procede))
        # forma de párrafo con la voz en negrita al principio
        for b, resto in re.findall(r"<p[^>]*><strong>(.*?)</strong>(.*?)</p>", trozo, re.S):
            clave, valor = sin_marcas(b).rstrip(" ·:—"), sin_marcas(resto).lstrip(" ·:—")
            if clave and valor and len(clave) <= 34:
                voces.setdefault(clave, (valor, procede))
    return {k: v for k, v in voces.items() if k not in NO_MARCAR}


def recoge(doc):
    if doc == "deck.html":
        return de_diapositivas(doc)
    piezas = de_apartados(doc)
    if piezas:
        return piezas
    return de_secciones(doc)


# ---------------------------------------------------------------------------
#  Preparar cada apartado para convivir con los demás en una sola página
# ---------------------------------------------------------------------------
TABLA = re.compile(r"<table\b", re.I)


def entabla(cuerpo):
    """Toda tabla dentro de una caja que se desplace sola.

    En su documento la columna era la página entera y una tabla ancha no se
    notaba. Aquí la columna es más estrecha y en un teléfono la última columna
    se salía por la derecha sin manera de llegar a ella.
    """
    fuera, pos = [], 0
    for m in TABLA.finditer(cuerpo):
        if m.start() < pos:
            continue
        entera = elemento(cuerpo, m.start())
        if entera is None:
            continue
        pos = m.start() + len(entera)
        if "tablewrap" not in cuerpo[max(0, m.start() - 60):m.start()]:
            fuera.append((m.start(), pos))
    for ini, fin in reversed(fuera):
        cuerpo = cuerpo[:ini] + '<div class="tablewrap">' + cuerpo[ini:fin] + "</div>" + cuerpo[fin:]
    return cuerpo


# Dentro de estos elementos no se marca nada: un enlace dentro de un enlace no
# existe, un titular con una sigla subrayada se lee peor, y en el glosario
# mismo sería marcar la definición con su propia definición.
VEDADOS = {"a", "button", "h1", "h2", "h3", "h4", "h5", "h6",
           "code", "kbd", "script", "style", "textarea", "dt", "summary", "title"}
TROZOS = re.compile(r"<[^>]+>|[^<]+")


def marca_glosario(cuerpo, voces, orden_voces):
    """Marca la primera aparición de cada voz, y solo en el texto.

    Se recorre el marcado trozo a trozo llevando la cuenta de dónde se está: la
    sustitución solo entra en texto suelto y nunca dentro de un atributo, de un
    enlace o de un titular. Una vez por apartado y voz: subrayar las once veces
    que aparece «IAC» en una fase sería ruido, no ayuda.
    """
    hondo, fuera, vistas = [], [], set()
    for m in TROZOS.finditer(cuerpo):
        z = m.group(0)
        if z.startswith("<"):
            fuera.append(z)
            if z.startswith("</"):
                nombre = z[2:-1].strip().lower()
                if hondo and hondo[-1] == nombre:
                    hondo.pop()
            elif not z.endswith("/>"):
                # los comentarios y las declaraciones no abren nada
                n = re.match(r"<([a-zA-Z][\w-]*)", z)
                if n and n.group(1).lower() not in (
                        "br", "img", "hr", "input", "meta", "link", "source", "use", "path", "col"):
                    hondo.append(n.group(1).lower())
            continue
        if any(x in VEDADOS for x in hondo):
            fuera.append(z)
            continue
        for voz in orden_voces:
            if voz in vistas:
                continue
            patron = re.compile(r"(?<![\w-])%s(?![\w-])" % re.escape(voz))
            n = patron.search(z)
            if not n:
                continue
            vistas.add(voz)
            z = (z[:n.start()]
                 + '<button type="button" class="gl" data-gl="%s">%s</button>' % (H.escape(voz), n.group(0))
                 + z[n.end():])
        fuera.append(z)
    return "".join(fuera)


ATRS = ("headers", "aria-labelledby", "aria-describedby", "aria-controls", "list", "form")


def prefija(cuerpo, marca):
    """Identificadores propios: ocho documentos en una página sin chocar."""
    cuerpo = re.sub(r'\bid="([^"]+)"', lambda m: 'id="%s%s"' % (marca, m.group(1)), cuerpo)
    cuerpo = re.sub(r'\bfor="([^"]+)"', lambda m: 'for="%s%s"' % (marca, m.group(1)), cuerpo)
    for a in ATRS:
        cuerpo = re.sub(
            r'\b%s="([^"]+)"' % a,
            lambda m, a=a: '%s="%s"' % (a, " ".join(marca + x for x in m.group(1).split())),
            cuerpo)
    cuerpo = re.sub(r"url\(#([^)]+)\)", lambda m: "url(#%s%s)" % (marca, m.group(1)), cuerpo)
    return cuerpo


# ---------------------------------------------------------------------------
#  Montar: el sistema entero en una página, con su índice completo
# ---------------------------------------------------------------------------

# ===========================================================================
#  LOS DATOS DEL CENTRO
#  Nada de esto se teclea aquí: sale de los modelos que ya gobiernan el
#  sistema —perfiles.py, el catálogo de acciones, el modelo de campañas— y de
#  los propios documentos. Si un supuesto cambia allí, cambia aquí.
# ===========================================================================
import importlib.util
import subprocess


def _modelo(nombre):
    ruta = RAIZ / nombre
    esp = importlib.util.spec_from_file_location(nombre[:-3].replace("-", "_"), ruta)
    mod = importlib.util.module_from_spec(esp)
    esp.loader.exec_module(mod)
    return mod


def _json_de(script):
    """Los modelos que ya publican sus datos en JSON los publican para todos."""
    salida = subprocess.run([sys.executable, str(RAIZ / script), "--json"],
                            capture_output=True, text=True, check=True)
    return json.loads(salida.stdout)


PERFILES = _modelo("perfiles.py")
CATALOGO = _json_de("catalogo-acciones.py")
CAMPANAS = _json_de("modelo-campanas.py")

# El color de cada puesto. Los mismos seis de todo el sistema.
COLOR_ROL = {
    "recepcion": "var(--rol-recepcion)", "director": "var(--rol-direccion)",
    "doctor": "var(--rol-doctor)", "higienista": "var(--rol-higienista)",
    "auxiliar": "var(--rol-auxiliar)", "rac": "var(--rol-rac)",
}
NOMBRE_ROL = {
    "recepcion": "Recepción", "director": "Dirección de Clínica", "doctor": "Doctor",
    "higienista": "Higienista", "auxiliar": "Auxiliar", "rac": "RAC",
    "dr": "Doctor", "dc": "Dirección de Clínica", "hig": "Higienista", "aux": "Auxiliar",
}

TITULARES = {"h1", "h2", "h3", "h4", "h5", "h6"}


def pieza(doc, ancla):
    """La literatura que cuelga de un identificador, entera.

    Si está en un titular, la pieza es la sección que lo contiene; si está en el
    propio bloque —cada fase es un <article> con su identificador—, la pieza es
    ese bloque.
    """
    t = fuente(doc)
    i = t.index('id="%s"' % ancla)
    ini = t.rfind("<", 0, i)
    nombre = ETIQUETA.match(t, ini).group(1).lower()
    if nombre in TITULARES:
        ini = t.rfind("<section", 0, i)
        if ini < 0:
            raise SystemExit("  %s#%s: el titular no está dentro de una sección" % (doc, ancla))
    trozo = elemento(t, ini)
    if trozo is None:
        raise SystemExit("  %s#%s: el bloque no se cierra" % (doc, ancla))
    return trozo


FASE = re.compile(r'<article class="phase[^"]*" id="(\w+)"([^>]*)>', re.I)


def fases(doc):
    """Las fases de un documento, con sus datos y su literatura entera.

    Cada fase ya declara en el marcado cuánto dura, quién la lleva y en qué
    momento del recorrido cae. Esos datos son los que dibujan el reloj y los
    carriles; el texto es el que se lee al abrirla.
    """
    t = fuente(doc)
    fuera = []
    for m in FASE.finditer(t):
        entero = elemento(t, m.start())
        if entero is None:
            continue
        atr = dict(re.findall(r'data-([\w-]+)="([^"]*)"', m.group(0)))
        meta = []
        for dt, dd in re.findall(r"<dt[^>]*>(.*?)</dt>\s*<dd[^>]*>(.*?)</dd>", entero, re.S):
            meta.append((sin_marcas(dt), sin_marcas(dd)))
        if not meta:
            for h, p in re.findall(r"<p class=\"phase__mt\"[^>]*>(.*?)</p>\s*<p[^>]*>(.*?)</p>",
                                   entero, re.S):
                meta.append((sin_marcas(h), sin_marcas(p)))
        tit = re.search(r"<h[23][^>]*>(.*?)</h[23]>", entero, re.S)
        lede = re.search(r'<p class="(?:lede|phase__lede)"[^>]*>(.*?)</p>', entero, re.S)
        if not lede:
            lede = re.search(r"</h[23]>\s*<p[^>]*>(.*?)</p>", entero, re.S)
        fuera.append({
            "id": m.group(1),
            "n": int(re.sub(r"\D", "", m.group(1)) or 0),
            "min": int(atr.get("min") or 0),
            "roles": (atr.get("roles") or "").split(),
            "label": atr.get("label", ""),
            "momento": atr.get("time", ""),
            "titulo": sin_marcas(tit.group(1)) if tit else atr.get("label", ""),
            "lede": sin_marcas(lede.group(1)) if lede else "",
            "meta": meta,
            "html": entero,
        })
    return fuera


def meta_de(f, clave, porDefecto=""):
    for k, v in f["meta"]:
        if clave.lower() in k.lower():
            return v
    return porDefecto


# ===========================================================================
#  LAS SECCIONES DEL SITIO
#  Cada una está construida para lo que cuenta, no rellenada con una plantilla:
#  la primera visita es una línea de tiempo porque son ciento veintitrés
#  minutos; los puestos son una matriz porque son seis por catorce fases; el
#  marketing es una tabla que se filtra porque son setenta y seis acciones.
# ===========================================================================
#  LITERATURA NUEVA
#  Se añade, no se sustituye: los ocho documentos siguen enteros y con su texto
#  intacto. Lo que se escribe aquí es lo que faltaba entre ellos —qué es cada
#  sección, por qué existe y cómo se lee—, que en un archivo de documentos no
#  hace falta y en un sitio es lo primero que se busca.
# ===========================================================================
CLAVES_META = ("Momento", "Responsable", "Ubicación", "Herramienta", "KPI")

# Cada sección: qué es, en una línea; y de qué va, en un párrafo que se escribe
# aquí por primera vez.
INTROS = {
    "inicio": ("", ""),
    "direccion": (
        "Lo que se cree, lo que se apuesta y lo que se decide",
        "Un centro no se dirige con intenciones: se dirige con decisiones fechadas y con "
        "alguien que responde de cada una. Este documento es el que gobierna: fija dónde está "
        "parado el centro y por qué ahí, qué construye la ventaja que un competidor no puede "
        "comprar, de dónde sale el dinero y qué lo destruye, y termina en quince decisiones "
        "que solo puede tomar la Junta. Las cifras que aparecen son de dos clases y están "
        "marcadas como tales: las del modelo, que se derivan de supuestos declarados, y las "
        "del sector, que se citan como rango y nunca como dato propio."),
    "presentacion": (
        "Las cuarenta y tres diapositivas de la sesión",
        "La presentación no añade nada al Plan de Dirección: lo extrae. Sirve para conducir "
        "una sesión de Junta de una hora sin leer setenta y nueve páginas en voz alta, y está "
        "construida para eso: una idea por diapositiva, la cifra siempre a la vista y una ruta "
        "corta de veinte minutos para cuando la agenda se rompe."),
    "protocolos": (
        "Qué se espera de cada puesto, en un solo sitio",
        "Todo lo que el sistema dice de un puesto vivía repartido en cuatro documentos. Quien "
        "llega un lunes a trabajar no debería recorrer cuatro documentos para saber qué se "
        "espera de él. Aquí se elige el puesto y aparece lo suyo: en qué fases del recorrido "
        "interviene y con qué papel, qué procedimientos tiene escritos, qué funciones de "
        "vanguardia le tocan y con qué se le mide. Nada de esto sale de esta página."),
    "primera-visita": (
        "La visita que decide, minuto a minuto",
        "Un paciente entra sin saber qué le pasa y sale con un diagnóstico en la mano, un plan "
        "en tres dimensiones y una decisión que puede tomar. Entre una cosa y otra hay doce "
        "fases, cinco puestos que se pasan el testigo cinco veces y nueve documentos que "
        "quedan firmados. La duración no es una estimación: está medida fase a fase, y la "
        "suma es la que es."),
    "operaciones": (
        "Las catorce fases del recorrido, los seis puestos y la puesta en marcha",
        "El documento troncal. Va de la primera llamada al mantenimiento a largo plazo, y cada "
        "fase construye sobre la anterior: la información recogida en la llamada personaliza "
        "la recepción, la anamnesis alimenta la presentación y el cierre abre el circuito de "
        "producción. La cadena es tan fuerte como su eslabón más débil, y por eso ninguna fase "
        "se salta «por falta de tiempo»."),
    "marketing": (
        "Cómo llega el paciente, y qué no haremos nunca para que llegue",
        "El paciente no recorre un embudo: recorre estados, y los recorre en los dos sentidos. "
        "Un embudo termina en la venta; una persona, no. Este plan ordena setenta y seis "
        "acciones sobre doce estados, cada una con dueño, coste, plazo y el número que se "
        "mueve si funciona. Y tiene una regla de entrada que es también el filtro: una acción "
        "entra si puede declarar en una línea qué gana el paciente. No qué ganamos nosotros."),
    "otros": (
        "Los catorce documentos que sostienen a los tres troncales",
        "Un sistema de gestión no son tres documentos: son tres documentos y todo lo que los "
        "hace ejecutables. Aquí están el compendio que los ordena, los 322 puntos con los que "
        "se verifica el centro, la auditoría de la clínica adquirida, el plan de los primeros "
        "cien días, los protocolos operativos por perfil, las fichas de innovación y el "
        "programa de cuidado. Cada uno dice qué es y cuándo se abre."),
    "numeros": (
        "Con qué se mide todo esto, y qué sabemos de verdad hoy",
        "Sin números propios, cualquier objetivo comercial es una opinión bien redactada. Esta "
        "sección es el instrumento: diez indicadores que se cuentan mes a mes, cinco números "
        "que todavía no se tienen y están señalados como lo que son, y el puente que lleva de "
        "los 720.000 € heredados al objetivo del tercer ejercicio, bloque a bloque y con cada "
        "bloque auditable por separado."),
}

# Los bloques del inicio. Están escritos aquí y no salen de ningún documento:
# son la capa que faltaba entre la puerta y los ocho documentos.
INICIO_BLOQUES = [
    ("El método",
     "Un sistema operativo, no una clínica",
     "Lo que se ha construido no es una consulta con buenos profesionales: es un sistema "
     "operativo que puede describirse, enseñarse, auditarse y repetirse. Tres documentos "
     "troncales lo gobiernan —dirección, operaciones y primera visita—, catorce lo sostienen y "
     "un instrumento lo mide. La consecuencia práctica es que el centro no depende de que "
     "alguien concreto tenga un buen día: depende de que el sistema se cumpla, y de que "
     "alguien responda cuando no se cumple.",
     [("14", "fases del recorrido"), ("6", "puestos con manual propio"),
      ("26", "procedimientos numerados"), ("322", "puntos de verificación")]),
    ("El equipo",
     "Seis puestos y ninguna zona gris",
     "Un organigrama dice quién manda. Una matriz RACI dice algo más útil: quién ejecuta, "
     "quién responde del resultado, a quién hay que consultar antes de decidir y a quién hay "
     "que informar después. Las catorce fases del recorrido están repartidas así entre seis "
     "puestos, y no hay ninguna fase sin alguien que responda de ella. Cuando un puesto no "
     "cumple, está escrito qué pasa: no es una conversación, es un procedimiento.",
     [("6", "puestos"), ("14", "fases repartidas"), ("0", "fases sin responsable"),
      ("1", "figura que puede autorizar una excepción")]),
    ("La tecnología",
     "Se compra cuando entra en un protocolo, no antes",
     "El equipamiento no es la ventaja: lo reivindican todos. La ventaja es el flujo digital "
     "completo y el criterio para incorporarlo. Por eso una técnica nueva no entra porque sea "
     "nueva: entra por una vía escrita —ficha de implantación, responsable, indicador y fecha "
     "de revisión— y solo cuando puede colgarse de una fase concreta del recorrido. Lo que no "
     "cabe en un protocolo, no se compra.",
     [("18", "fichas de innovación aplicada"), ("6", "perfiles con funciones de vanguardia"),
      ("3D", "planificación y guía quirúrgica"), ("1", "vía de entrada, escrita")]),
    ("El cuidado",
     "«Le cuidamos para siempre» tiene instrumento",
     "La promesa del centro tiene dos mitades. La primera es el resultado y la fija el "
     "posicionamiento: ningún tratamiento se deja a medias. La segunda es la relación, y una "
     "relación sin instrumento es una intención. El instrumento se llama Giraldo Te Cuida: "
     "cuota anual, revisiones que ocurren de verdad y un informe que se entrega en persona. Es "
     "también la única partida del plan que produce sin ocupar un solo hueco de primera visita.",
     [("1", "programa de cuidado anual"), ("0", "huecos de primera visita que ocupa"),
      ("2", "partidas contables por separado"), ("12", "meses de seguimiento")]),
]

# Lo que no se hará nunca. Un centro se reconoce antes por sus prohibiciones
# que por su catálogo, y una web que solo enseña lo que ofrece no dice nada.
# Están escritas en el Plan de Marketing; aquí se explica por qué cada una.
PRINCIPIOS = [
    ("No se promete lo que no se puede sostener",
     "Ni ausencia de dolor, ni plazos que dependan de que todo salga bien, ni resultados de "
     "otro paciente. Lo que se dice en la primera visita tiene que poder rastrearse hasta el "
     "informe firmado por el Doctor."),
    ("No se presiona con el precio",
     "El presupuesto no se presenta como una oferta que caduca. Se presenta como la "
     "consecuencia lógica de un diagnóstico que el paciente ya ha entendido, y el paciente se "
     "lo lleva a casa si quiere."),
    ("No se trata sin diagnóstico completo",
     "Ningún plan se firma sin las pruebas hechas, el informe emitido y el consentimiento "
     "explicado. La prisa del paciente no es motivo para saltarse una fase."),
    ("No se deja un tratamiento a medias",
     "Ni por presupuesto, ni por agenda, ni por cansancio. De ahí sale el nombre de todo esto: "
     "una media sonrisa es la que se hace a medias, y el corte no lo ve nadie salvo el "
     "paciente, que lo ve todos los días."),
    ("No se abandona al paciente cuando termina",
     "El alta no es una despedida: es el paso a mantenimiento, con cita agendada antes de "
     "salir y un programa que lo sostiene."),
    ("No se cuentan como propios los datos que no lo son",
     "Cuando una cifra viene del sector y no del centro, se dice. Cinco números clave todavía "
     "no se tienen, y están señalados como supuestos de trabajo en todos los documentos donde "
     "aparecen."),
]

# Las preguntas que se hacen de verdad, contestadas con lo que el sistema dice.
PREGUNTAS = [
    ("¿Cuánto dura la primera visita?",
     "Entre ciento quince y ciento veinte minutos de consulta, ciento veintitrés contando la "
     "llamada previa. No es una estimación: está medida fase a fase y cada fase tiene su "
     "duración escrita."),
    ("¿Con quién se habla, y cuántas veces se cambia de persona?",
     "Con cinco puestos, y el testigo se pasa cinco veces: recepción, dirección, doctor, "
     "dirección y recepción otra vez. Esos cinco cambios son los cinco puntos donde una "
     "primera visita se rompe, y por eso están protocolizados uno a uno."),
    ("¿Qué se lleva el paciente el primer día?",
     "Un diagnóstico explicado, un plan en tres dimensiones, un presupuesto con su "
     "justificación y nueve documentos firmados o entregados. Y una decisión que puede tomar "
     "en casa, sin plazo que caduque."),
    ("¿Quién responde si algo se salta?",
     "La matriz RACI asigna a cada una de las catorce fases alguien que ejecuta y alguien que "
     "responde del resultado. No hay ninguna fase sin responsable, y está escrito qué ocurre "
     "cuando un puesto no cumple: no es una conversación, es un procedimiento."),
    ("¿Y después del tratamiento?",
     "El alta abre el programa de cuidado: cuota anual, revisiones agendadas antes de salir de "
     "la clínica e informe que se entrega en persona. Es la única partida del plan que produce "
     "sin ocupar un hueco de primera visita."),
    ("¿Se puede auditar todo esto?",
     "Esa es la idea. Trescientos veintidós puntos de verificación —físicos, documentales y de "
     "proceso—, veintiséis procedimientos numerados y un instrumento que mide diez indicadores "
     "mes a mes. Lo que no se verifica, no ocurre."),
]

HECHOS = [
    ("8", "documentos", "Tres troncales, cuatro derivados y un instrumento. Misma versión y misma fecha: ninguno puede quedar desfasado respecto de otro sin que se note."),
    ("@TOTAL@", "apartados", "Todos están en este sitio, enteros y sin resumir. Lo que no está aquí, no está escrito."),
    ("14", "fases", "De la primera llamada al mantenimiento a largo plazo, encadenadas y con responsable."),
    ("123′", "la primera visita", "Medidos fase a fase, no estimados. Doce fases y cinco entregas del testigo."),
    ("@ACC@", "acciones de marketing", "Cada una con dueño, coste, plazo y el número que se mueve si funciona."),
    ("322", "puntos de verificación", "Físicos, documentales y de proceso. Lo que no se verifica, no ocurre."),
    ("15", "decisiones abiertas", "Se someten a la Junta con formato de acuerdo, no de informe."),
    ("1,2 M€", "objetivo", "Facturación del tercer ejercicio, con el puente que lo sostiene bloque a bloque."),
]


# ===========================================================================
#  LAS NUEVE SECCIONES
#  Una por documento, más el inicio. Cada sección lleva su documento entero
#  —todos sus apartados, sin resumir— y, delante, el bloque que ese documento
#  pide: un reloj para la primera visita, una matriz para los protocolos, una
#  tabla que se filtra para el marketing, un puente para los números.
# ===========================================================================
SECCIONES = [
    ("inicio", "Inicio", None, None, ""),
    ("direccion", "Dirección", "memoria.html", "a", "Plan de Dirección"),
    ("presentacion", "Presentación", "deck.html", "b", "Presentación de Junta"),
    ("protocolos", "Protocolos", "protocolos.html", "c", "Protocolos por puesto"),
    ("primera-visita", "Primera Visita", "index.html", "d", "Protocolo de Primera Visita"),
    ("operaciones", "Operaciones", "manual.html", "e", "Manual Maestro de Operaciones"),
    ("marketing", "Marketing", "marketing.html", "f", "Plan Maestro de Marketing"),
    ("otros", "Otros", "otros.html", "g", "Otros documentos del sistema"),
    ("numeros", "Los números", "instrumentos/captura.html", "h", "Los números del centro"),
]

ENLACE = re.compile(r"<a\b([^>]*)>(.*?)</a>", re.I | re.S)
SOLO_DOC = re.compile(r'href="([^"#]+\.html)"')


def cose(html, mapa, seccion, rotulos):
    """Cada enlace lleva a donde tiene que llevar, y dice adónde.

    Aquí está todo en la misma página: los ocho documentos y sus 135 apartados.
    Así que un enlace no tiene por qué morir ni por qué sacar al lector del
    sitio. Se resuelve contra el mapa de todo lo que hay:

      · si el destino está en esta misma sección, es un enlace normal;
      · si está en otra, sigue siendo un enlace y se le pone al lado el nombre
        de la sección a la que va, para que nadie pulse a ciegas;
      · si no está en ninguna parte —porque el ancla venía mal escrita—, no se
        finge: el texto se queda y el enlace desaparece.

    De la tercera clase quedaban once, todas con el ancla cortada a treinta y
    cuatro caracteres en perfiles.py. Estaban arregladas en el origen antes de
    escribir esto, y check-coherencia falla si vuelve a aparecer una.
    """
    def uno(m):
        atr, texto = m.group(1), m.group(2)
        href = re.search(r'href="([^"]*)"', atr)
        if not href:
            return m.group(0)
        destino = href.group(1)
        if destino.startswith("#"):
            clave = destino[1:]
        elif ".html#" in destino:
            clave = destino.split("#", 1)[1]
        elif destino.endswith(".html"):
            clave = None
        else:
            return m.group(0)            # correo, teléfono, enlace externo

        if clave is None:
            # un enlace al documento entero: lleva a su sección
            doc = destino.split("/")[-1]
            sec = DOC_A_SEC.get(destino) or DOC_A_SEC.get(doc)
            if not sec:
                return '<span class="ref">%s</span>' % texto
            return ('<a href="#%s" class="salta">%s<i class="salta__d">%s</i></a>'
                    % (sec, texto, H.escape(rotulos[sec])))

        aqui = mapa.get(seccion + "/" + clave)
        if aqui:
            return '<a href="#%s"%s>%s</a>' % (aqui[0], _limpio(atr), texto)
        for s in mapa.get("@" + clave, []):
            ident, sec = s
            return ('<a href="#%s" class="salta">%s<i class="salta__d">%s</i></a>'
                    % (ident, texto, H.escape(rotulos[sec])))
        return '<span class="ref">%s</span>' % texto
    return ENLACE.sub(uno, html)


def _limpio(atr):
    """Los atributos del enlace menos el href, que se reescribe."""
    return re.sub(r'\s*href="[^"]*"', "", atr)


DOC_A_SEC = {}


def submenu(apartados, pre):
    """El índice de la sección: sus apartados, agrupados como los agrupa él."""
    filas, grupo = [], None
    for p in apartados:
        if p["grupo"] != grupo:
            grupo = p["grupo"]
            if grupo:
                filas.append('<p class="sub__g">%s</p>' % H.escape(grupo))
        filas.append('<a href="#%s%s" data-ir="%s%s"><span>%s</span>%s</a>'
                     % (pre, p["id"], pre, p["id"], H.escape(p["n"] or "·"),
                        H.escape(p["rotulo"])))
    return "".join(filas)


def cifras(pares):
    return ('<div class="cifras">%s</div>'
            % "".join('<div><b>%s</b><span>%s</span></div>' % (b, H.escape(s)) for b, s in pares))


# --------------------------------------------------------------------------
#  Los bloques propios de cada sección
# --------------------------------------------------------------------------
# Un recorte de marcado no tiene por qué cuadrar: si se corta un capítulo por
# sus apartados, al primer trozo le faltan cierres y al último le sobran. Esto
# lo arregla, y si aun así no cuadra, para la construcción en vez de publicar
# una página rota.
ETIQUETAS = re.compile(r"<(/?)([a-zA-Z][\w-]*)([^>]*)>")
VACIAS = {"area", "base", "br", "circle", "col", "embed", "hr", "img", "input", "line",
          "link", "meta", "path", "polygon", "polyline", "rect", "source", "stop",
          "track", "use", "wbr"}
CIERRE_FINAL = re.compile(r"\s*</[a-zA-Z][\w-]*>\s*$")


def _pila(frag):
    """Lo que queda abierto y los cierres que sobran, en ese orden."""
    abiertas, huerfanos = [], 0
    for m in ETIQUETAS.finditer(frag):
        nombre = m.group(2).lower()
        if nombre in VACIAS or m.group(3).rstrip().endswith("/"):
            continue
        if not m.group(1):
            abiertas.append(nombre)
        elif abiertas and abiertas[-1] == nombre:
            abiertas.pop()
        elif nombre in abiertas:
            while abiertas.pop() != nombre:
                pass
        else:
            huerfanos += 1
    return abiertas, huerfanos


def cuadra(frag):
    """El recorte, con sus etiquetas cuadradas."""
    _abiertas, huerfanos = _pila(frag)
    for _ in range(huerfanos):
        frag = CIERRE_FINAL.sub("", frag, count=1)
    abiertas, huerfanos = _pila(frag)
    frag += "".join("</%s>" % n for n in reversed(abiertas))
    if _pila(frag) != ([], 0):
        raise SystemExit("  un recorte no cuadra: %s…" % frag[:80])
    return frag


def reparte(entera, anclas):
    """Una pieza repartida entre los titulares que lleva dentro.

    Devuelve lo que va antes del primero —la entrada del capítulo— y un trozo
    por titular, en un diccionario, porque el orden en que el documento los
    escribe no tiene por qué ser el orden en que conviene leerlos. Cada trozo
    se cuadra: al recortar, al primero le faltan cierres y al último le sobran.
    """
    cortes = []
    for a in anclas:
        i = entera.find('id="%s"' % a)
        if i < 0:
            return None, None
        cortes.append((entera.rfind("<", 0, i), a))
    cortes.sort()                      # el documento manda en el orden del corte
    trozos = {}
    for k, (ini, a) in enumerate(cortes):
        hasta = cortes[k + 1][0] if k + 1 < len(cortes) else len(entera)
        trozos[a] = cuadra(entera[ini:hasta])
    return cuadra(entera[:cortes[0][0]]), trozos


def partes_de(doc, anclas):
    """Los apartados, vengan como vengan.

    Hay apartados que son secciones propias y hay apartados que son un titular
    dentro de una sección: las funciones de vanguardia de cada puesto, por
    ejemplo, son cinco o seis <h3> dentro de un solo capítulo. Pedir cada uno
    por separado devolvería el capítulo entero cinco veces; aquí se pide una
    vez y se reparte por sus titulares, que es lo que son.
    """
    if not anclas:
        return []
    entera = pieza(doc, anclas[0])
    if all(('id="%s"' % a) in entera for a in anclas[1:]):
        _entrada, trozos = reparte(entera, anclas)
        if trozos:
            return trozos
    return {a: pieza(doc, a) for a in anclas}


# ---------------------------------------------------------------------------
#  El desplegable
# ---------------------------------------------------------------------------
#  Un titular que se pulsa y debajo aparece lo que hay. Es el mecanismo con el
#  que esta web deja de ser una lista de enlaces: el texto está aquí, no «a un
#  clic de aquí». Sin JavaScript no hay nada que pulsar y todo queda abierto,
#  que es como tiene que quedarse un documento cuando el navegador no ejecuta
#  nada; con JavaScript se cierran al arrancar y se abre el que se quiera.
def desplegable(clave, n, rotulo, apunte, cuerpo, extra=""):
    return (
        '<section class="desp" id="%s"%s>\n'
        '  <h4 class="desp__h"><button type="button" class="desp__b" aria-expanded="true"\n'
        '      aria-controls="%s-c">'
        '<span class="desp__n">%s</span>'
        '<span class="desp__t"><b>%s</b>%s</span>'
        '<span class="desp__x" aria-hidden="true"></span></button></h4>\n'
        '  <div class="desp__c" id="%s-c" role="region">\n'
        '    <div class="desp__in">%s</div>\n'
        '  </div>\n'
        '</section>'
        % (clave, extra, clave, H.escape(n), H.escape(rotulo),
           ('<i>%s</i>' % H.escape(apunte)) if apunte else "",
           clave, cuerpo))


def grupo_desplegables(rotulo, apunte, piezas):
    """Un grupo de desplegables, con su rótulo y su «abrir todo»."""
    if not piezas:
        return ""
    return ('<div class="grupod">\n'
            '  <div class="grupod__cab">\n'
            '    <p class="rotulillo">%s</p>\n'
            '    <p class="grupod__q">%s</p>\n'
            '    <button type="button" class="grupod__t" data-abre-todo>Abrir los %d</button>\n'
            '  </div>\n'
            '  <div class="grupod__l">%s</div>\n'
            '</div>'
            % (H.escape(rotulo), H.escape(apunte), len(piezas), "\n".join(piezas)))


def bloque_primera_visita(pre):
    fs = fases("index.html")
    total = sum(f["min"] for f in fs)
    trozos, ejes = [], ""
    for f in fs:
        pct = 100.0 * f["min"] / total
        trozos.append(
            '<a class="reloj__t" href="#%sf%02d" data-ir="%sf%02d" style="width:%.4f%%" '
            'title="%s · %d minutos"><span class="reloj__n">%02d</span>'
            '<span class="reloj__r">%s</span><span class="reloj__m">%d′</span></a>'
            % (pre, f["n"], pre, f["n"], pct, H.escape(f["label"] or f["titulo"]), f["min"],
               f["n"], H.escape(f["label"] or f["titulo"]), f["min"]))
    ejes = "".join('<span style="left:%.4f%%">%d′</span>' % (100.0 * c / total, c)
                   for c in (0, 30, 60, 90, total))

    usados = []
    for f in fs:
        for r in f["roles"]:
            if r not in usados:
                usados.append(r)
    carriles = []
    for r in usados:
        bloques, x = [], 0.0
        for f in fs:
            an = 100.0 * f["min"] / total
            if r in f["roles"]:
                jefe = (f["roles"][0] == r)
                bloques.append(
                    '<a class="carril__b%s" href="#%sf%02d" data-ir="%sf%02d" '
                    'style="left:%.4f%%;width:%.4f%%" title="%s">%s</a>'
                    % (" es-jefe" if jefe else "", pre, f["n"], pre, f["n"], x, an,
                       H.escape("Fase %02d · %s" % (f["n"], f["label"] or f["titulo"])),
                       ("%02d" % f["n"]) if an > 4 else ""))
            x += an
        carriles.append('<div class="carril"><p class="carril__q">%s</p>'
                        '<div class="carril__p">%s</div></div>'
                        % (H.escape(NOMBRE_ROL.get(r, r.title())), "".join(bloques)))

    return ("""
<div class="lienzo">
  <div class="lienzo__cab">
    <h2>El reloj de la visita</h2>
    <p>Cada trozo es una fase y mide lo que dura de verdad. Pulse cualquiera y se abre entera,
      aquí mismo.</p>
  </div>
  <div class="reloj"><div class="reloj__barra">@@T@@</div><div class="reloj__eje">@@E@@</div></div>
</div>
<div class="lienzo">
  <div class="lienzo__cab">
    <h2>Quién tiene al paciente</h2>
    <p>Cuatro carriles a lo largo de los @@TOT@@ minutos. El bloque lleno es de quien lleva la
      fase; el hueco, de quien acompaña. Los cinco cambios de carril son las cinco entregas del
      testigo, y son los cinco puntos donde una primera visita se rompe.</p>
  </div>
  <div class="carriles">@@C@@</div>
</div>
""".replace("@@T@@", "".join(trozos)).replace("@@E@@", ejes)
   .replace("@@C@@", "".join(carriles)).replace("@@TOT@@", str(total)))


CLASE_RACI = {"R/A": "wes-ra", "R": "wes-r", "A": "wes-a", "C": "wes-c", "I": "wes-i", "—": "wes-no"}


# Los identificadores finales de las catorce fases. El recorrido vive en dos
# documentos —doce fases en el Protocolo de Primera Visita y dos en el Manual—
# y aquí, con los ocho documentos en una página, cada uno lleva delante la
# letra de su sección. Si alguna vez dejara de cuadrar, main() lo para: toda
# fase a la que se llama tiene que existir como identificador en la página.
def id_de_fase(n):
    letra = {i: l for i, _r, _d, l, _n in SECCIONES if l}
    return ("%s-f%02d" % (letra["primera-visita"], n) if n <= 12
            else "%s-m%02d" % (letra["operaciones"], n))


# Los ecos: la literatura que se repite a propósito.
#
# El manual de cada puesto vive en Operaciones y aquí se copia entero dentro de
# su ficha, porque quien llega a trabajar un lunes no tiene por qué ir a
# buscarlo a otro documento. La copia no inventa nada ni cambia una palabra: es
# el mismo texto, con sus identificadores prefijados para que no choquen.
#
# Se anotan en ECOS para que el mapa de enlaces siga sabiendo dónde vive el
# original: dentro de Protocolos los enlaces se resuelven en la propia página
# —que es de lo que se trata—, y desde cualquier otra sección se sigue yendo al
# Manual, que es la casa del texto.
ECOS = set()


def marca_eco(cuerpo):
    ECOS.update(re.findall(r'id="([^"]+)"', cuerpo))
    return cuerpo


def eco(ancla, pre, doc="manual.html"):
    """Una pieza de otro documento, traída entera y sin chocar con nada."""
    return marca_eco(prefija(entabla(pieza(doc, ancla)), pre))


def bloque_protocolos(pre):
    P = PERFILES
    botones, fichas = [], []
    for n, p in enumerate(P.PERFILES):
        raci = P.raci_de(p)
        activas = sum(1 for _f, papel in raci if papel != "—")
        cara = imagenes.arte("retrato-%d" % (n + 1), "0 0 400 400", "arte--cara")
        botones.append(
            '<button type="button" class="puestobt%s" data-puesto="%s">'
            '<span class="puestobt__c">%s</span>'
            '<span class="puestobt__t"><b>%s</b><span>%d de 14 fases</span></span></button>'
            % (" es-on" if n == 0 else "", p["id"], cara, H.escape(p["corto"]), activas))
        celdas = "".join(
            '<button type="button" class="wraci__c %s" data-abre-fase="%s" '
            'title="Fase %02d · %s · %s">'
            '<span class="wraci__f">%02d</span><span class="wraci__p">%s</span></button>'
            % (CLASE_RACI[papel], id_de_fase(i + 1), i + 1, H.escape(fase),
               H.escape(P.QUE_ES[papel][0]), i + 1, H.escape(papel))
            for i, (fase, papel) in enumerate(raci))
        suyas = "".join(
            '<button type="button" class="fasep" data-abre-fase="%s">'
            '<span class="fasep__n">%02d</span>'
            '<span class="fasep__r">%s</span>'
            '<span class="fasep__p %s">%s</span></button>'
            % (id_de_fase(i + 1), i + 1, H.escape(fase), CLASE_RACI[papel],
               H.escape(P.QUE_ES[papel][0]))
            for i, (fase, papel) in enumerate(raci) if papel != "—")

        # El manual del puesto, entero. Sus apartados no son secciones sueltas:
        # son los titulares de su propio capítulo. Así que el capítulo se pide
        # una vez y se reparte entre ellos —lo que va antes del primero es la
        # entrada—, y así no se emite ni una línea dos veces.
        capitulo = entabla(pieza("manual.html", p["manual"]))
        entrada, trozos = reparte(capitulo, [a for _r, a in p["bloques"]])
        if trozos is None:
            raise SystemExit("  %s: su capítulo no se deja repartir" % p["id"])

        piezas = [desplegable(
            "%spd-%s-0" % (pre, p["id"]), "00", "Qué es este puesto y de qué responde",
            "Manual Maestro · entrada del capítulo",
            marca_eco(prefija(entrada, pre)))]
        for k, (rotulo, ancla) in enumerate(p["bloques"]):
            piezas.append(desplegable(
                "%spd-%s-%d" % (pre, p["id"], k + 1), "%02d" % (k + 1),
                rotulo, "Manual Maestro · %s" % p["nombre"],
                marca_eco(prefija(trozos[ancla], pre))))
        manual_puesto = grupo_desplegables(
            "Su manual de puesto, entero",
            "Lo que el Manual Maestro escribe de este puesto, aquí mismo y palabra por "
            "palabra. No hay que ir a ninguna otra parte a leerlo.",
            piezas)

        funciones = partes_de("manual.html", [a for _r, a in p["vanguardia"]])
        if p["vanguardia"]:
            vang = grupo_desplegables(
                "Sus funciones de vanguardia",
                "Lo que este puesto hace y en la mayoría de los centros no se hace. Cada "
                "una entera, con sus procedimientos y sus indicadores.",
                [desplegable("%spv-%s-%d" % (pre, p["id"], k + 1), "%02d" % (k + 1),
                             rotulo, "Manual Maestro · funciones de vanguardia",
                             marca_eco(prefija(entabla(funciones[ancla]), pre)))
                 for k, (rotulo, ancla) in enumerate(p["vanguardia"])])
        else:
            vang = ('<div class="grupod"><div class="grupod__cab">'
                    '<p class="rotulillo">Sus funciones de vanguardia</p>'
                    '<p class="grupod__q">Ninguna propia: las suyas son de gobierno del '
                    'sistema, y están escritas en su manual de puesto, aquí arriba.</p>'
                    '</div></div>')

        indice = "".join(
            '<a href="#%spd-%s-%d"><span>%02d</span>%s</a>' % (pre, p["id"], k, k, H.escape(r))
            for k, r in enumerate(["Qué es este puesto y de qué responde"]
                                  + [r for r, _a in p["bloques"]]))
        indice += "".join(
            '<a href="#%spv-%s-%d"><span>V%d</span>%s</a>'
            % (pre, p["id"], k + 1, k + 1, H.escape(r))
            for k, (r, _a) in enumerate(p["vanguardia"]))

        fichas.append(
            '<article class="puesto" data-puesto="%s"%s>\n'
            '  <div class="puesto__cab">\n'
            '    <div class="puesto__cara">%s</div>\n'
            '    <div>\n'
            '      <p class="puesto__k">Puesto %d de 6 · %s</p>\n'
            '      <h3>%s</h3>\n      <p class="puesto__q">%s</p>\n'
            '    </div>\n'
            '  </div>\n'
            '  %s\n'
            '  <p class="rotulillo">Su papel en las catorce fases del recorrido</p>\n'
            '  <div class="wraci">%s</div>\n'
            '  <p class="leyenda">%s</p>\n'
            '  <p class="leyenda leyenda--pista">Pulse una fase y se abre entera; al cerrarla '
            'se vuelve aquí.</p>\n'
            '  <p class="rotulillo">Las fases en las que entra, con nombre</p>\n'
            '  <div class="fases-p">%s</div>\n'
            '  <nav class="puesto__idx" aria-label="Lo que hay de este puesto">%s</nav>\n'
            '  %s\n  %s\n'
            '</article>'
            % (p["id"], "" if n == 0 else " hidden",
               imagenes.arte("retrato-%d" % (n + 1), "0 0 400 400", "arte--cara"), n + 1,
               ("columna %s de la matriz" % p["raci"]) if p.get("raci")
               else "sin columna propia en la matriz: la nota lo sitúa en el mantenimiento",
               H.escape(p["nombre"]), H.escape(p["que"]),
               cifras([(str(activas), "fases en las que interviene"),
                       (str(len(p["bloques"]) + 1), "apartados de su manual, enteros"),
                       (str(len(p["vanguardia"])), "funciones de vanguardia")]),
               celdas,
               " · ".join("<b>%s</b> %s" % (k, H.escape(v[0])) for k, v in P.QUE_ES.items()),
               suyas, indice, manual_puesto, vang))

    return ("""
<div class="lienzo">
  <div class="lienzo__cab">
    <h2>Elija su puesto</h2>
    <p>Seis. Al elegir uno aparece todo lo suyo y nada más: dónde entra en las catorce fases y
      con qué papel, su manual de puesto entero —no un enlace a él: el texto— y las funciones
      de vanguardia que le tocan. Todo ocurre en esta página.</p>
  </div>
  <div class="puestosel">@@B@@</div>
  <div class="puestos">@@F@@</div>
</div>
<div class="lienzo">
  <div class="lienzo__cab">
    <h2>Y si no se cumple</h2>
    <p>Vale para los seis. No es una conversación: es un procedimiento escrito, con sus plazos
      y con quién lo aplica.</p>
  </div>
  @@NOCUMPLE@@
</div>
""".replace("@@B@@", "".join(botones)).replace("@@F@@", "\n".join(fichas))
   .replace("@@NOCUMPLE@@", grupo_desplegables(
       "El procedimiento", "Qué ocurre exactamente cuando un puesto no cumple.",
       [desplegable(pre + "pd-nocumple", "01",
                    "Qué pasa exactamente cuando un puesto no cumple",
                    "Manual Maestro", eco("m-pasa-exactamente-cuando-puesto-no-cumple", pre))])))


COSTE_ROT = {"0": "No cuesta dinero", "€": "Hasta 1.000 €", "€€": "De 1 a 5 mil",
             "€€€": "De 5 a 15 mil", "€€€€": "Más de 15 mil"}
PLAZO_ROT = {"ya": "Ya", "trim": "Este trimestre", "año": "Este año",
             "estruct": "Cambia cómo trabajamos"}
SEM_ROT = {"verde": "Sin reservas", "amarillo": "Con cautela", "naranja": "Requiere criterio"}


def bloque_marketing(pre):
    C = CATALOGO
    estados = "".join(
        '<button type="button" class="estado" data-estado="%s">'
        '<span class="estado__n">%s</span><b>%s</b><p>%s</p></button>'
        % (cod, cod, H.escape(nombre), H.escape(que))
        for cod, nombre, que in C["estados"])
    filas = "".join(
        '<tr data-grupo="%s" data-quien="%s" data-coste="%s" data-plazo="%s" data-sem="%s">'
        '<td class="acc__cod">%s</td>'
        '<td class="acc__q"><b>%s</b><span>%s</span></td>'
        '<td class="acc__gana">%s</td>'
        '<td class="acc__meta"><span class="etq">%s</span><span class="etq">%s</span>'
        '<span class="etq etq--%s">%s</span></td>'
        '<td class="acc__ef"><span class="barrita" style="--v:%d%%"></span>%d</td></tr>'
        % (a["grupo"], a["quien"], a["coste"], a["plazo"], a["sem"], a["cod"],
           H.escape(a["accion"]), H.escape(a["indicador"]), H.escape(a["gana"]),
           H.escape(COSTE_ROT.get(a["coste"], a["coste"])),
           H.escape(PLAZO_ROT.get(a["plazo"], a["plazo"])),
           a["sem"], H.escape(SEM_ROT.get(a["sem"], a["sem"])), 20 * a["efecto"], a["efecto"])
        for a in C["acciones"])

    def opciones(nombre, rot, pares):
        return ('<label class="filtro"><span>%s</span><select data-filtro="%s">'
                '<option value="">Todas</option>%s</select></label>'
                % (rot, nombre, "".join('<option value="%s">%s</option>' % (v, H.escape(r))
                                        for v, r in pares)))
    filtros = (opciones("grupo", "Estado", [(g[0], "%s · %s" % (g[0], g[2])) for g in C["grupos"]])
               + opciones("quien", "Puesto", sorted((k, k) for k in C["por_puesto"]))
               + opciones("coste", "Coste", [(k, COSTE_ROT.get(k, k))
                                             for k in ("0", "€", "€€", "€€€", "€€€€")])
               + opciones("plazo", "Plazo", [(k, PLAZO_ROT[k])
                                             for k in ("ya", "trim", "año", "estruct")])
               + opciones("sem", "Marco", [(k, SEM_ROT[k])
                                           for k in ("verde", "amarillo", "naranja")]))
    camp = "".join(
        '<article class="wcampana"><p class="wcampana__k">%s</p><h4>%s</h4>'
        '<p class="wcampana__r">%s</p>'
        '<dl class="wcampana__c"><div><dt>Aporta</dt><dd>%s €</dd></div>'
        '<div><dt>Cuesta</dt><dd>%s €</dd></div>'
        '<div><dt>Por cada euro</dt><dd>%s €</dd></div></dl></article>'
        % (H.escape(c["cod"]), H.escape(c["nombre"]), H.escape(c.get("razon", "")),
           "{:,}".format(int(c.get("aporta") or sum(p[1] for p in c.get("partes", [])))).replace(",", "."),
           "{:,}".format(int(c["coste"])).replace(",", "."),
           ("%.1f" % ((c.get("aporta") or sum(p[1] for p in c.get("partes", []))) / c["coste"])).replace(".", ","))
        for c in CAMPANAS["campanas"])
    return ("""
<div class="lienzo">
  <div class="lienzo__cab">
    <h2>Los doce estados</h2>
    <p>Pulse uno y la tabla de abajo se queda con las acciones que actúan sobre él.</p>
  </div>
  <div class="estados">@@E@@</div>
</div>
<div class="lienzo">
  <div class="lienzo__cab">
    <h2>Las setenta y seis acciones</h2>
    <p>Con dueño, coste, plazo, efecto esperado y el indicador que las delata. Y con lo que gana
      el paciente, que es la regla de entrada: si esa casilla no se puede rellenar, la acción no
      existe.</p>
  </div>
  <div class="filtros">@@FI@@
    <button type="button" class="limpiar" id="limpiafiltros">Quitar filtros</button>
    <span class="cuentafiltro" id="cuentaacc"></span></div>
  <div class="tablawrap"><table class="acciones" id="tablaacciones">
    <thead><tr><th>Cód.</th><th>Qué se hace y qué mueve</th><th>Qué gana el paciente</th>
      <th>Coste · plazo · marco</th><th>Efecto</th></tr></thead>
    <tbody>@@FA@@</tbody></table></div>
</div>
<div class="lienzo">
  <div class="lienzo__cab">
    <h2>La cartera de campañas</h2>
    <p>Ninguna cifra está escrita a mano: todas salen del modelo, con el criterio conservador
      —una campaña vale la diferencia entre el paciente que trae y el que desplaza, no lo que
      factura.</p>
  </div>
  <div class="campanas">@@CA@@</div>
</div>
""".replace("@@E@@", estados).replace("@@FI@@", filtros)
   .replace("@@FA@@", filas).replace("@@CA@@", camp))


def bloque_numeros(pre):
    P, cap = CAMPANAS["puente"], CAMPANAS["capacidad"]
    tramos = [("Punto de partida", P["base"]), ("Llenar la agenda", P["llenar"]),
              ("Mejor mezcla de casos", P["mezcla"]), ("Seguimiento y cuidado", P["seguimiento"])]
    tope = P["planificado"]
    barras = "".join(
        '<div class="puente__t" style="--w:%.3f%%"><span class="puente__r">%s</span>'
        '<span class="puente__v">%s €</span></div>'
        % (100.0 * v / tope, H.escape(r), "{:,}".format(int(v)).replace(",", "."))
        for r, v in tramos)
    return ("""
<div class="lienzo">
  <div class="lienzo__cab">
    <h2>El puente, a escala</h2>
    <p>De los 720.000 € heredados al objetivo del tercer ejercicio. Cada bloque mide lo que
      aporta y se audita por separado; ninguno está escrito a mano.</p>
  </div>
  <div class="puente">@@B@@
    <p class="puente__pie">Planificado <b>@PL@ €</b> · objetivo <b>@OB@ €</b> ·
      colchón <b>@CO@ €</b> (@PC@ %)</p></div>
  @@CI@@
</div>
""".replace("@@B@@", barras)
   .replace("@@CI@@", cifras([
       ("{:,}".format(int(cap["pv_ano"])).replace(",", "."), "primeras visitas al año de capacidad"),
       ("{:,}".format(int(cap["pv_libres"])).replace(",", "."), "huecos libres para campañas"),
       ("%d €" % int(cap["valor_base"]), "valor medio de una primera visita"),
       ("5", "números que aún no se tienen")]))
   .replace("@PL@", "{:,}".format(int(P["planificado"])).replace(",", "."))
   .replace("@OB@", "{:,}".format(int(P["objetivo"])).replace(",", "."))
   .replace("@CO@", "{:,}".format(int(abs(P["colchon"]))).replace(",", "."))
   .replace("@PC@", ("%.1f" % (100 * P["colchon_pct"])).replace(".", ",")))


def bloque_operaciones(pre):
    fs = fases("manual.html")
    mapa = "".join(
        '<a class="mfase" href="#%sm%02d" data-ir="%sm%02d"><span class="mfase__n">%02d</span>'
        '<b>%s</b><span class="mfase__r">%s</span></a>'
        % (pre, f["n"], pre, f["n"], f["n"], H.escape(f["label"] or f["titulo"]),
           H.escape(NOMBRE_ROL.get(f["roles"][0] if f["roles"] else "", "")))
        for f in fs)
    return ("""
<div class="lienzo">
  <div class="lienzo__cab">
    <h2>El recorrido completo</h2>
    <p>Catorce fases. Las doce primeras son la primera visita; la trece ejecuta lo vendido y la
      catorce es la que da coherencia al nombre del centro.</p>
  </div>
  <div class="wmapa">@@M@@</div>
</div>
""".replace("@@M@@", mapa))


# ---------------------------------------------------------------------------
#  La presentación de Junta, explicada
# ---------------------------------------------------------------------------
#  Las cuarenta y tres diapositivas estaban en la página, pero en la página no
#  se veían: el deck las dibuja una encima de otra y oculta todas menos la que
#  toca, que es lo que hace falta para proyectar y justo lo contrario de lo que
#  hace falta para leer. Aquí se despliegan: cada diapositiva con su minuto y
#  su parte, y debajo el guion del ponente —qué decir al pasarla y qué se
#  contesta a la pregunta difícil—, que hasta ahora no salía de las notas.
DIAPO = re.compile(r'<section([^>]*)class="([^"]*\bslide\b[^"]*)"([^>]*)>', re.I)
NOTA = re.compile(r'<aside class="nota"[^>]*>(.*?)</aside>', re.S | re.I)
LEDE = re.compile(r'<p class="lede"[^>]*>(.*?)</p>', re.S | re.I)


def diapositivas():
    """Las cuarenta y tres, con su minuto, su parte y su guion."""
    t = fuente("deck.html")
    fuera = []
    for m in DIAPO.finditer(t):
        entero = elemento(t, m.start())
        if entero is None:
            continue
        atr = dict(re.findall(r'data-([\w-]+)="([^"]*)"', m.group(1) + m.group(3)))
        nota = NOTA.search(entero)
        eb = re.search(r'<p class="eyebrow"[^>]*>(.*?)</p>', entero, re.S)
        tit = re.search(r"<h[1-4][^>]*>(.*?)</h[1-4]>", entero, re.S)
        lede = LEDE.search(entero)
        fuera.append({
            "min": atr.get("min", ""),
            "esencial": atr.get("esencial") == "1",
            "separa": "slide--div" in m.group(2),
            "eyebrow": sin_marcas(eb.group(1)) if eb else "",
            "titulo": sin_marcas(tit.group(1)) if tit else "",
            "lede": sin_marcas(lede.group(1)) if lede else "",
            "html": NOTA.sub("", entero),
            "guion": nota.group(1).strip() if nota else "",
        })
    return fuera


def _minutos(ms):
    """El minuto en que arranca una diapositiva, en minutos enteros."""
    m = re.match(r"(\d+):(\d+)", ms or "")
    return int(m.group(1)) if m else 0


def bloque_presentacion(pre):
    ds = diapositivas()
    total = len(ds)
    esenciales = sum(1 for d in ds if d["esencial"])
    dura = max(_minutos(d["min"]) for d in ds)

    # Las partes salen de las propias diapositivas de separación: no se inventa
    # una estructura, se lee la que la presentación ya tiene escrita.
    partes = []
    actual = {"rotulo": "La apertura", "titulo": "Con qué se abre la sesión", "esencial": False,
              "lede": "Las dos diapositivas que fijan de qué se va a hablar y con qué regla: "
                      "un plan que se expone a ser refutado, no un informe de lo que ya pasó.",
              "diapos": []}
    for d in ds:
        if d["separa"]:
            if actual["diapos"]:
                partes.append(actual)
            actual = {"rotulo": d["eyebrow"], "titulo": d["titulo"],
                      "lede": d["lede"], "esencial": d["esencial"], "diapos": []}
        else:
            actual["diapos"].append(d)
    if actual["diapos"]:
        partes.append(actual)

    idx, cuerpos = [], []
    for k, parte in enumerate(partes):
        clave = "%spt-%d" % (pre, k)
        dd = parte["diapos"]
        ess = sum(1 for d in dd if d["esencial"])
        idx.append('<a href="#%s"><span>%s</span><b>%s</b><i>%d diapositivas · minuto %s</i></a>'
                   % (clave, H.escape(parte["rotulo"]), H.escape(parte["titulo"]),
                      len(dd), H.escape(dd[0]["min"])))
        piezas = [
            desplegable("%s-d%d" % (clave, j), d["min"] or "·",
                        d["titulo"] or d["eyebrow"] or "Diapositiva",
                        d["eyebrow"] + (" · esencial" if d["esencial"] else ""),
                        '<div class="dia">%s</div>%s'
                        % (d["html"],
                           ('<div class="guion"><p class="rotulillo">El guion del ponente</p>'
                            '%s</div>' % d["guion"]) if d["guion"] else ""),
                        extra=' data-esencial="%d"' % (1 if d["esencial"] else 0))
            for j, d in enumerate(dd)]
        cuerpos.append(
            '<div class="parte" id="%s">\n'
            '  <p class="parte__k">%s · del minuto %s al %s · %d diapositivas%s</p>\n'
            '  <h3>%s</h3>\n  %s\n'
            '  <div class="grupod__l">%s</div>\n'
            '</div>'
            % (clave, H.escape(parte["rotulo"]), H.escape(dd[0]["min"]),
               H.escape(dd[-1]["min"]), len(dd),
               (" · %d de la ruta corta" % (ess + (1 if parte["esencial"] else 0))) if ess else "",
               H.escape(parte["titulo"]),
               ('<p class="parte__q">%s</p>' % H.escape(parte["lede"])) if parte["lede"] else "",
               "\n".join(piezas)))

    return ("""
<div class="lienzo">
  <div class="lienzo__cab">
    <h2>La sesión, diapositiva a diapositiva</h2>
    <p>Las @N@ diapositivas de la Junta, aquí dentro y legibles: cada una con el minuto en el
      que entra, la parte a la que pertenece y —esto no salía de las notas del documento— el
      guion del ponente: qué hay que decir al pasarla y qué se contesta a la pregunta difícil
      que viene detrás. Pulse una y se abre.</p>
  </div>
  @@CIFRAS@@
  <div class="presfil">
    <button type="button" class="presfil__b es-on" data-pres="todas">Todas</button>
    <button type="button" class="presfil__b" data-pres="esencial">Solo la ruta corta</button>
    <p class="presfil__q">La ruta corta son las @E@ diapositivas que sostienen el argumento
      entero cuando la agenda se rompe y la sesión se queda en veinte minutos. Una de ellas
      es la que abre la Parte VI, y aquí es el título de esa parte.</p>
  </div>
  <nav class="presidx" aria-label="Las partes de la sesión">@@IDX@@</nav>
  <div class="partes">@@CUERPOS@@</div>
</div>
""".replace("@@CIFRAS@@", cifras([(str(total), "diapositivas"),
                                  ("%d min" % dura, "dura la sesión entera"),
                                  (str(len(partes)), "partes"),
                                  (str(esenciales), "esenciales: la ruta corta")]))
   .replace("@@IDX@@", "".join(idx))
   .replace("@@CUERPOS@@", "\n".join(cuerpos))
   .replace("@N@", str(total)).replace("@E@", str(esenciales)))


# ---------------------------------------------------------------------------
#  La imagen de cada sección
# ---------------------------------------------------------------------------
#  Una web de clínica sin una sola imagen se lee como un documento, y era
#  exactamente lo que le pasaba a esta. Cada sección abre ahora con una banda
#  a sangre: una de las cinco piezas dibujadas en imagenes.py, recortada por un
#  sitio distinto y en día o en noche, alternando, para que al bajar por el
#  sitio se note que se ha cambiado de sitio.
ARTE = {
    "direccion":      ("campo",   "0 30 1200 430"),
    "presentacion":   ("campo2",  "0 130 1200 400"),
    "protocolos":     ("anillos", "30 40 640 360"),
    "primera-visita": ("arcos",   "0 110 1200 430"),
    "operaciones":    ("campo",   "260 170 940 360"),
    "marketing":      ("trama",   "0 80 1200 430"),
    "otros":          ("campo2",  "180 40 1020 400"),
    "numeros":        ("anillos", "0 190 700 400"),
    "recorridos":     ("arcos",   "180 50 940 400"),
    "mapa":           ("arcos",   "0 30 1200 470"),
}


# ---------------------------------------------------------------------------
#  Qué es cada sección, dicho en tres líneas antes de entrar
# ---------------------------------------------------------------------------
#  Un documento largo no asusta por largo: asusta cuando no se sabe qué es,
#  para quién es ni qué se hace con él. Eso son tres frases, y van delante.
#  Debajo, la extensión declarada: cuántos apartados, cuántas palabras y
#  cuánto se tarda en leerlo entero. Declararla es lo que permite no leerlo
#  entero sin sensación de estar saltándose algo.
QUE_ES = {
    "direccion": (
        "El documento que gobierna. Fija dónde está parado el centro y por qué ahí, qué "
        "construye la ventaja que un competidor no puede comprar, de dónde sale el dinero y "
        "qué lo destruye, y termina en quince decisiones que solo puede tomar la Junta.",
        "Para la Junta y para la Dirección. Quien no decide no necesita leerlo entero; quien "
        "decide, sí.",
        "Se lleva a la sesión de Junta. Cada decisión sale de aquí con fecha y con dueño, y "
        "vuelve aquí cuando se revisa."),
    "presentacion": (
        "El Plan de Dirección extraído en cuarenta y tres diapositivas, para conducir una "
        "sesión de una hora sin leer setenta y nueve páginas en voz alta.",
        "Para quien presenta, y para quien no pudo estar y quiere saber qué se dijo y en qué "
        "minuto se dijo.",
        "Se proyecta. Y aquí, además, se lee: cada diapositiva trae debajo el guion del "
        "ponente y la respuesta a la pregunta difícil que viene detrás."),
    "protocolos": (
        "El sistema visto desde cada uno de los seis puestos: en qué fases del recorrido "
        "entra, con qué papel, y su manual de puesto entero.",
        "Para quien ocupa el puesto, y para quien lo va a ocupar el lunes que viene.",
        "Se abre por el puesto propio y se lee de arriba abajo. Nada de lo que hay aquí "
        "obliga a ir a buscar otro documento."),
    "primera-visita": (
        "Las doce fases de la visita que decide, medidas una a una: ciento veintitrés "
        "minutos, cinco puestos que se pasan el testigo cinco veces y nueve documentos que "
        "quedan firmados.",
        "Para todo el que toca al paciente ese día, y para el paciente que quiere saber qué "
        "le va a pasar.",
        "Se sigue fase a fase. La duración no es una estimación: está medida, y la suma es la "
        "que es."),
    "operaciones": (
        "El documento troncal. De la primera llamada al mantenimiento a largo plazo, con los "
        "seis manuales de puesto, la matriz de responsabilidades y la puesta en marcha.",
        "Para todo el equipo. Es el documento del que cuelgan los demás.",
        "Se consulta por fase o por puesto. Cuando algo se discute, se mira aquí antes que en "
        "ningún otro sitio."),
    "marketing": (
        "Setenta y seis acciones sobre doce estados del paciente, cada una con dueño, coste, "
        "plazo, efecto esperado y el indicador que la delata si no funciona.",
        "Para quien lleva la captación y para quien aprueba el gasto.",
        "Se filtra por estado, puesto, coste o plazo, y se ejecuta lo que queda arriba. Una "
        "acción entra si puede declarar en una línea qué gana el paciente."),
    "otros": (
        "Los documentos que sostienen a los tres troncales: los que se firman, los que se "
        "cuelgan en la pared y los que se rellenan a mano.",
        "Para quien tiene que dar con el papel exacto, hoy y sin preguntar.",
        "Se busca el documento, se imprime o se copia, y se usa. Ninguno depende de los "
        "demás."),
    "numeros": (
        "El instrumento de medida: los indicadores que se cuentan mes a mes, los cinco "
        "números que todavía no se tienen y el puente que lleva de los 720.000 € heredados "
        "al objetivo del tercer ejercicio.",
        "Para Dirección y para la Junta, una vez al mes.",
        "Se rellena una hoja por mes. Sin números propios, cualquier objetivo comercial es "
        "una opinión bien redactada."),
}


def cuanto_ocupa(piezas, propio=""):
    """Palabras y minutos de lectura, contados sobre el texto de verdad.

    Cuenta también lo que la sección trae fuera de sus apartados —los manuales
    de puesto enteros, las cuarenta y tres diapositivas, la tabla de acciones—,
    porque para quien lee eso también es texto que está ahí.
    """
    palabras = sum(len(sin_marcas(p["html"]).split()) for p in piezas)
    palabras += len(sin_marcas(propio).split())
    return palabras, max(1, int(round(palabras / 210.0)))


def reloj_humano(minutos):
    if minutos < 60:
        return "%d minutos" % minutos
    h, m = divmod(minutos, 60)
    if not m:
        return "%d hora%s" % (h, "" if h == 1 else "s")
    return "%d h %02d min" % (h, m)


def que_es(ident, piezas, propio):
    """Las tres líneas de antes de entrar, y la extensión, declarada."""
    if ident not in QUE_ES:
        return ""
    es, quien, hace = QUE_ES[ident]
    palabras, minutos = cuanto_ocupa(piezas, propio)
    # Hay secciones donde el apartado no es la unidad que se lee: la
    # presentación es un apartado y cuarenta y tres diapositivas, y protocolos
    # son tres apartados y seis manuales de puesto enteros.
    cuantos = {"presentacion": "43 diapositivas",
               "protocolos": "6 puestos, con su manual entero"}.get(
                   ident, "%d apartado%s" % (len(piezas), "" if len(piezas) == 1 else "s"))
    return ("""
<div class="lienzo lienzo--que">
  <div class="que">
    <div class="que__c"><p class="rotulillo">Qué es</p><p>%s</p></div>
    <div class="que__c"><p class="rotulillo">Para quién</p><p>%s</p></div>
    <div class="que__c"><p class="rotulillo">Qué se hace con esto</p><p>%s</p></div>
  </div>
  <div class="que__p">
    <p class="letra">La extensión, declarada</p>
    <p class="que__x"><b>%s</b> · unas %s palabras · leerlo entero lleva del orden
      de <b>%s</b>. No hace falta: cada apartado se abre solo y se lee solo, y hay
      <button type="button" class="enlacillo" data-ir-sec="recorridos">diez recorridos</button>
      que llevan por lo que toca a cada uno. Pero si quiere leerlo seguido, de la primera
      línea a la última, está entero aquí abajo.</p>
    <button type="button" class="bt bt--fino" data-seguido>Leerlo entero, seguido</button>
  </div>
</div>
""" % (H.escape(es), H.escape(quien), H.escape(hace), cuantos,
       "{:,}".format(palabras).replace(",", "."), reloj_humano(minutos)))


def frente(ident, rotulillo, titulo, texto, numero=""):
    """La cabecera de una sección: una banda de imagen a sangre con el rótulo.

    Es lo que separa una web de un índice. Debajo empieza el texto; encima,
    solo lo que hace falta para saber dónde se ha entrado.
    """
    pieza, recorte = ARTE[ident]
    return (
        '<header class="frente frente--dia" data-frente>\n'
        '  <div class="frente__i">%s</div>\n'
        '  <div class="frente__c">\n'
        '    %s<p class="letra frente__k">%s</p>\n'
        '    <h1>%s</h1>\n'
        '    <p class="frente__p">%s</p>\n'
        '  </div>\n'
        '</header>'
        % (imagenes.arte(pieza, recorte),
           ('<span class="frente__n" aria-hidden="true">%s</span>' % numero) if numero else "",
           rotulillo, H.escape(titulo), H.escape(texto)))


BLOQUES = {
    "presentacion": bloque_presentacion,
    "primera-visita": bloque_primera_visita,
    "protocolos": bloque_protocolos,
    "marketing": bloque_marketing,
    "numeros": bloque_numeros,
    "operaciones": bloque_operaciones,
}


def monta():
    """Las nueve secciones, con sus documentos enteros y los enlaces resueltos."""
    voces = glosario()
    orden_voces = sorted(voces, key=len, reverse=True)
    anclas_glosario = {a for _d, a, _p in GLOSARIOS}

    rotulos = {i: r for i, r, doc, _l, _n in SECCIONES if doc}
    for i, _r, doc, _l, _n in SECCIONES:
        if doc:
            DOC_A_SEC[doc] = i
            DOC_A_SEC[doc.split("/")[-1]] = i

    # ------------------------------------------------------------------
    #  Primera pasada: recoger, marcar el glosario y prefijar. De aquí sale
    #  el mapa de TODO lo que hay, que es lo que permite que un enlace sepa
    #  a qué sección va antes de que nadie lo pulse.
    # ------------------------------------------------------------------
    porSeccion, mapa = [], {}
    for ident, rotulo, doc, letra, nombre_doc in SECCIONES:
        if doc is None:
            continue
        pre = letra + "-"
        piezas = recoge(doc)
        for p in piezas:
            cuerpo = entabla(p["html"])
            if not any(('id="%s"' % a) in cuerpo for a in anclas_glosario):
                cuerpo = marca_glosario(cuerpo, voces, orden_voces)
            p["html"] = prefija(cuerpo, pre)
            p["clave"] = pre + p["id"]
        bloque = BLOQUES.get(ident)
        propio = bloque(pre) if bloque else ""

        for trozo in [propio] + [p["html"] for p in piezas]:
            for crudo in re.findall(r'id="([^"]+)"', trozo):
                llano = crudo[len(pre):] if crudo.startswith(pre) else crudo
                mapa[ident + "/" + llano] = (crudo, ident)
                # y también con su prefijo puesto: los bloques que se dibujan
                # aquí —el reloj, los carriles, el mapa de fases— ya enlazan al
                # identificador final, y sin esta línea se quedaban sin enlace
                mapa[ident + "/" + crudo] = (crudo, ident)
                if crudo not in ECOS:
                    # un eco no compite con su original: desde fuera se sigue
                    # yendo al documento donde el texto vive
                    mapa.setdefault("@" + llano, []).append((crudo, ident))
        porSeccion.append((ident, rotulo, doc, pre, nombre_doc, piezas, propio))

    # ------------------------------------------------------------------
    #  Segunda pasada: coser los enlaces y montar cada sección
    # ------------------------------------------------------------------
    secciones, menus, indice, orden = [], [], [], []
    for ident, rotulo, doc, pre, nombre_doc, piezas, propio in porSeccion:
        propio = cose(propio, mapa, ident, rotulos)
        for p in piezas:
            p["html"] = cose(p["html"], mapa, ident, rotulos)

        hojas, filas, grupo = [], [], None
        for n, p in enumerate(piezas):
            orden.append((p["clave"], nombre_doc, p["grupo"], p["rotulo"], ident))
            if p["grupo"] != grupo:
                grupo = p["grupo"]
                if grupo:
                    filas.append('<p class="idx__g">%s</p>' % H.escape(grupo))
            filas.append(
                '<a class="idx__a" href="#%s" data-ir="%s"><span>%s</span><b>%s</b></a>'
                % (p["clave"], p["clave"], H.escape(p["n"] or "·"), H.escape(p["rotulo"])))
            hojas.append(
                '<article class="hoja" id="%s" data-hoja="%s" data-sec="%s">\n'
                '  <p class="hoja__k"><span>%s</span>%s%s</p>\n%s\n</article>'
                % (p["clave"], p["clave"], ident, H.escape(p["n"] or "·"),
                   H.escape(nombre_doc), " · " + H.escape(p["grupo"]) if p["grupo"] else "",
                   p["html"]))

        titulo, texto = INTROS[ident]
        indice.append((ident, rotulo, nombre_doc, len(piezas)))
        menus.append('<div class="sub" data-sub="%s" hidden>%s</div>'
                     % (ident, submenu(piezas, pre)))
        secciones.append(
            '<section class="sec" id="%s" data-sec="%s">\n'
            '  %s\n'
            '  %s\n'
            '  <div class="sec__lienzos">%s</div>\n'
            '  <div class="lienzo lienzo--indice">\n'
            '    <div class="lienzo__cab"><h2>Lo que hay en %s</h2>\n'
            '      <p>%d apartados, enteros y en el orden del documento. Pulse uno y se abre '
            'aquí. Un enlace que lleve a otra sección lo dice al lado: nunca se va a ciegas.</p></div>\n'
            '    <div class="idx">%s</div>\n'
            '  </div>\n'
            '  <div class="leyendo" hidden><b></b><span class="leyendo__p"><i></i></span>'
            '<span class="leyendo__n"></span></div>\n'
            '  <div class="hojas">%s</div>\n'
            '</section>'
            % (ident, ident,
               frente(ident, "%s · %d apartados" % (H.escape(nombre_doc), len(piezas)),
                      titulo, texto, "%02d" % len(indice)),
               que_es(ident, piezas, propio),
               propio, H.escape(rotulo.lower()), len(piezas),
               "".join(filas), "\n".join(hojas)))

    return secciones, menus, indice, orden, voces, mapa


# ===========================================================================
#  LOS RECORRIDOS
#  Nadie entra en un sistema documental a leerlo entero. Se entra con una
#  pregunta —«¿qué me pasa a mí?», «¿qué me toca a mí?», «¿qué se decide?»— y
#  se sale con la respuesta. Un recorrido es esa pregunta convertida en camino:
#  cinco a nueve paradas, en orden, cada una con lo que hay que mirar y por qué.
#  Se abre, se avanza, se vuelve. Y el sitio recuerda por dónde iba.
# ===========================================================================
def paradas_de_puesto(p):
    """El recorrido de un puesto sale de su propio modelo, no de una lista."""
    P = PERFILES
    raci = P.raci_de(p)
    suyas = [(i + 1, f) for i, (f, papel) in enumerate(raci) if papel in ("R", "R/A", "A")]
    paradas = [
        ("Quién es y de qué responde", p["manual"],
         "Empiece por su manual de puesto: qué hace, de qué responde y qué puede decidir."),
    ]
    if suyas:
        n, _f = suyas[0]
        if n <= 12:
            paradas.append(("Su primera fase con el paciente", "f%02d" % n,
                            "La primera vez que el paciente pasa por sus manos, minuto a minuto."))
    for rot, anc in p["bloques"][:3]:
        paradas.append((rot, anc, "Uno de sus procedimientos escritos, entero."))
    if p["vanguardia"]:
        rot, anc = p["vanguardia"][0]
        paradas.append((rot, anc,
                        "Una función de vanguardia: lo que este puesto hace y en otros centros "
                        "no se hace."))
    paradas.append(("Con qué se le mide", "m-indicadores-perfil",
                    "Los indicadores por perfil. Un puesto sin número es una opinión."))
    paradas.append(("Qué pasa si no se cumple", "m-pasa-exactamente-cuando-puesto-no-cumple",
                    "La matriz de obligaciones. No es una conversación: es un procedimiento."))
    paradas.append(("Sus primeros treinta días", "m-puesta-marcha",
                    "Qué se espera de usted el primer mes, semana a semana."))
    return paradas


RECORRIDOS_FIJOS = [
    {
        "id": "paciente",
        "quien": "Soy paciente",
        "titulo": "Lo que le pasa a usted, de la llamada al mantenimiento",
        "que": "El recorrido tal y como lo vive quien entra por la puerta: la llamada, la "
               "acogida, las pruebas, el diagnóstico explicado, el presupuesto que se lleva a "
               "casa y lo que ocurre después del alta.",
        "paradas": [
            ("La llamada", "f01", "Todo empieza aquí, y aquí se decide con qué expectativa viene."),
            ("La acogida y el recorrido por la tecnología", "f02",
             "Los primeros minutos en el centro. Nadie espera de pie sin saber qué va a pasar."),
            ("Las pruebas", "f05",
             "CBCT, escaneado intraoral y fotografía clínica. Sin diagnóstico completo no hay plan."),
            ("El diagnóstico, explicado", "f09",
             "En tres dimensiones y en sus palabras. Si no lo entiende, no ha habido diagnóstico."),
            ("El presupuesto", "f10",
             "No es una oferta que caduca: es la consecuencia de un diagnóstico que ya ha aceptado."),
            ("La despedida y el seguimiento", "f12",
             "Qué se lleva, quién le llama y cuándo."),
            ("El mantenimiento", "m14",
             "El alta no es una despedida: es el paso al programa que sostiene el resultado."),
            ("Giraldo Te Cuida", "otros-gtc",
             "El instrumento que convierte «le cuidamos para siempre» en revisiones reales."),
        ],
    },
    {
        "id": "junta",
        "quien": "Soy de la Junta",
        "titulo": "Qué se somete a votación y con qué se sostiene",
        "que": "Una sesión de una hora, en el orden en que conviene leerla: qué se pide, dónde "
               "está parado el centro, de dónde sale el dinero, qué puede salir mal y las "
               "quince decisiones con formato de acuerdo.",
        "paradas": [
            ("Dos minutos", "resumen", "De qué va todo esto, antes de entrar en nada."),
            ("Dónde estamos parados", "posicion", "La posición que se ocupa y por qué esa."),
            ("Qué se ha construido", "sistema",
             "El activo no es la clínica: es el sistema operativo que la hace repetible."),
            ("De dónde sale el dinero", "economia",
             "La economía por paciente y lo que la destruye."),
            ("Qué puede salir mal", "riesgo", "El registro de riesgos, con dueño y con fecha."),
            ("El puente hasta 1,2 M€", "puente",
             "Bloque a bloque, con cada bloque auditable por separado."),
            ("Las quince decisiones", "decisiones",
             "Con formato de acuerdo: qué se aprueba, quién ejecuta y en qué plazo."),
        ],
    },
    {
        "id": "lunes",
        "quien": "Entro a trabajar",
        "titulo": "Lo primero que hay que saber, en este orden",
        "que": "Para quien empieza el lunes. Qué es este sistema, qué se cumple siempre —lo "
               "haga quien lo haga—, cómo se reparte el trabajo y qué se espera de usted los "
               "primeros treinta días.",
        "paradas": [
            ("Qué es este sistema", "m-documento-tres-usos",
             "Un documento con tres usos: formación, operación y auditoría."),
            ("Lo que se cumple siempre", "m-estandares-transversales-ampliacion",
             "Los estándares transversales. Valen para todos y en todo momento."),
            ("El recorrido completo", "m-recorrido-paciente",
             "Las catorce fases. Ninguna se salta «por falta de tiempo»."),
            ("Quién hace qué", "m-matriz-raci",
             "La matriz RACI. Ninguna fase se queda sin alguien que responda."),
            ("Su puesto", "m-manuales-puesto", "Los seis manuales. Busque el suyo."),
            ("Sus primeros treinta días", "m-puesta-marcha", "Semana a semana."),
        ],
    },
    {
        "id": "marketing",
        "quien": "Llevo la captación",
        "titulo": "Cómo llega un paciente, y qué no haremos nunca para que llegue",
        "que": "El plan completo en siete paradas: en qué creemos, qué nos prohibimos, los doce "
               "estados por los que pasa una persona, las setenta y seis acciones con dueño y "
               "la cartera de campañas con sus cifras.",
        "paradas": [
            ("Qué creemos y qué nos prohibimos", "k-creemos-nos-prohibimos-consecuencia",
             "El filtro de todo lo que viene después."),
            ("Las ocho que no haremos nunca", "k-ocho-no-haremos-nunca",
             "Un centro se reconoce antes por sus prohibiciones."),
            ("El marco de la publicidad sanitaria", "k-marco-publicidad-sanitaria",
             "Lo que la ley permite decir, y lo que no."),
            ("Los doce estados", "k-doce-estados",
             "El paciente no recorre un embudo: recorre estados, y en los dos sentidos."),
            ("Las setenta y seis acciones", "k-setenta-seis-acciones",
             "Con dueño, coste, plazo y el número que se mueve si funciona."),
            ("Qué va primero, y con qué dinero", "k-va-primero",
             "El orden de prelación y el techo de gasto."),
            ("Cómo se mide y cuándo se para", "k-como-mide-regla",
             "Las ocho medidas del plan y la regla para retirar una acción."),
        ],
    },
]


def recorridos():
    """Los recorridos: cuatro escritos y seis derivados de los puestos."""
    fuera = list(RECORRIDOS_FIJOS)
    for p in PERFILES.PERFILES:
        # El título de cada recorrido de puesto es lo que ese puesto hace: diez
        # tarjetas que dijeran «todo lo suyo, en orden» no distinguen nada.
        titulo = p["que"].split(". ")[0].rstrip(".")
        fuera.append({
            "id": "puesto-" + p["id"],
            "quien": "Soy " + p["corto"],
            "titulo": titulo,
            "que": "Su recorrido completo: dónde entra en las catorce fases y con qué papel, "
                   "qué procedimientos tiene escritos, qué funciones de vanguardia le tocan, "
                   "con qué se le mide y qué se espera de usted los primeros treinta días.",
            "paradas": paradas_de_puesto(p),
        })
    return fuera


# ===========================================================================
#  EL MAPA Y LOS RECORRIDOS, DIBUJADOS
# ===========================================================================
def mapa_interactivo(mapa):
    """Las catorce fases, en una rejilla que se recorre con el dedo.

    Estuvo dibujado en SVG, con los rótulos colgando de cada nodo, y a catorce
    nodos los rótulos se montaban unos encima de otros. Aquí es marcado
    corriente: el texto se ajusta solo, cada fase es un botón de verdad —se
    llega con el tabulador y se abre con la barra— y en un teléfono la rejilla
    se reordena sola. Pulsar una abre su fase entera en el lector, y del lector
    se vuelve al mapa sin perder el sitio.
    """
    fs = fases("index.html")
    mfs = fases("manual.html")

    def nodo(f, clave, n_total):
        destino = mapa.get("@" + clave)
        ident = destino[0][0] if destino else ""
        return ('<button type="button" class="nodo" data-abre-fase="%s"%s>'
                '<span class="nodo__n">%02d</span>'
                '<b class="nodo__r">%s</b>'
                '<span class="nodo__m">%s</span></button>'
                % (ident, "" if ident else " disabled", f["n"],
                   H.escape(f["label"] or f["titulo"]),
                   ("%d min" % f["min"]) if f["min"] else "&nbsp;"))

    pv = "".join(nodo(f, "f%02d" % f["n"], 12) for f in fs)
    post = "".join(nodo(f, "m%02d" % f["n"], 2) for f in mfs[12:])

    return ("""
<div class="mapa14">
  <div class="mapa14__g">
    <p class="letra mapa14__t">La primera visita · doce fases · @MIN@ minutos</p>
    <div class="nodos">@@PV@@</div>
  </div>
  <div class="mapa14__g mapa14__g--post">
    <p class="letra mapa14__t">Después de la visita · dos fases</p>
    <div class="nodos nodos--post">@@POST@@</div>
  </div>
</div>
""".replace("@@PV@@", pv).replace("@@POST@@", post)
   .replace("@MIN@", str(sum(f["min"] for f in fs))))


def dibuja_recorridos(mapa):
    """Los diez recorridos, con sus paradas resueltas contra todo lo que hay."""
    fuera, tarjetas = [], []
    for r in recorridos():
        paradas, n = [], 0
        for rot, anc, por in r["paradas"]:
            destino = mapa.get("@" + anc)
            if not destino:
                continue
            n += 1
            ident, sec = destino[0]
            paradas.append(
                '<li class="parada"><button type="button" class="parada__b" data-lee="%s" '
                'data-ruta="%s" data-paso="%d">'
                '<span class="parada__n">%02d</span>'
                '<span class="parada__t"><b>%s</b><span>%s</span></span>'
                '<span class="parada__i letra">%s</span></button></li>'
                % (ident, r["id"], n - 1, n, H.escape(rot), H.escape(por),
                   H.escape(SEC_ROTULO.get(sec, sec))))
        if not paradas:
            continue
        fuera.append(
            '<article class="wruta" id="ruta-%s" data-ruta="%s">\n'
            '  <header class="wruta__cab">\n'
            '    <p class="letra">%s · %d paradas</p>\n'
            '    <h3>%s</h3>\n    <p class="wruta__q">%s</p>\n'
            '    <button type="button" class="bt bt--fuerte" data-empieza="%s">'
            'Empezar el recorrido</button>\n'
            '  </header>\n  <ol class="paradas">%s</ol>\n</article>'
            % (r["id"], r["id"], H.escape(r["quien"]), n, H.escape(r["titulo"]),
               H.escape(r["que"]), r["id"], "".join(paradas)))
        # cada tarjeta lleva su trozo de imagen: el mismo dibujo cortado por
        # sitios distintos, para que diez tarjetas no parezcan la misma
        k = len(tarjetas)
        tarjetas.append(
            '<button type="button" class="rutacard" data-ve-ruta="%s">'
            '<span class="rutacard__i">%s</span>'
            '<span class="letra">%s</span><b>%s</b>'
            '<span class="rutacard__m letra">%d paradas</span></button>'
            % (r["id"], imagenes.arte(("campo", "campo2", "arcos")[k % 3],
                                      "%d %d 420 260" % (60 + (k * 97) % 700,
                                                         40 + (k * 61) % 300)),
               H.escape(r["quien"]), H.escape(r["titulo"]), n))
    return "\n".join(fuera), "".join(tarjetas)


SEC_ROTULO = {}


# ---------------------------------------------------------------------------
#  La rueda: una sola pantalla, y todo el sistema alrededor
# ---------------------------------------------------------------------------
#  Un índice en columna obliga a leer diez nombres en fila para elegir uno. Una
#  rueda no: se ve entera de un vistazo, cada cosa está a la misma distancia de
#  la mano y el centro dice qué es lo que se está señalando. Es blanca, con una
#  línea de un pelo por radio, y no hay nada más.
#
#  Las posiciones se calculan aquí, no en el navegador: sin JavaScript la rueda
#  sigue estando donde tiene que estar y cada círculo sigue siendo un enlace.
RUEDA_R = 352.0        # el radio de la órbita, sobre un lienzo de mil
RUEDA_S = 82.0         # el radio de cada círculo de fuera
RUEDA_C = 134.0        # el radio del círculo del centro


def rueda(indice, total):
    nodos = [(i, r, n, c) for i, r, n, c in indice]
    nodos.append(("recorridos", "Recorridos",
                  "Diez maneras de entrar", len(RECORRIDOS_FIJOS) + len(PERFILES.PERFILES)))
    nodos.append(("mapa", "El mapa", "Las catorce fases del recorrido", 14))

    # Debajo de cada nombre va el número que de verdad describe lo que hay
    # dentro, no el número de apartados de todo. «1 apartado» en la
    # presentación es cierto y no dice nada; «43 diapositivas» sí.
    CUENTA = {
        "presentacion": "43 diapositivas",
        "protocolos": "6 puestos",
        "primera-visita": "12 fases",
        "marketing": "%d acciones" % CATALOGO["total"],
        "recorridos": "10 recorridos",
        "mapa": "14 fases",
    }

    QUE = {
        "recorridos": "Diez recorridos guiados: se elige quién es usted y la web lleva parada "
                      "por parada por lo que le toca leer.",
        "mapa": "Las catorce fases del recorrido del paciente, de la primera llamada al "
                "mantenimiento. Se pulsa una y se abre entera.",
    }

    piezas, radios = [], []
    n = len(nodos)
    for k, (ident, rotulo, nombre, cuantos) in enumerate(nodos):
        ang = math.radians(-90 + k * (360.0 / n))
        cx = 500 + RUEDA_R * math.cos(ang)
        cy = 500 + RUEDA_R * math.sin(ang)
        # el radio va del borde del círculo del centro al borde del de fuera
        radios.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" '
                      'data-radio="%s"/>'
                      % (500 + RUEDA_C * math.cos(ang), 500 + RUEDA_C * math.sin(ang),
                         500 + (RUEDA_R - RUEDA_S) * math.cos(ang),
                         500 + (RUEDA_R - RUEDA_S) * math.sin(ang), ident))
        piezas.append(
            '<button type="button" class="orbe" data-ir-sec="%s" data-orbe="%s"\n'
            '        style="left:%.2f%%;top:%.2f%%"\n'
            '        data-que="%s">\n'
            '  <span class="orbe__n letra">%02d</span>\n'
            '  <b class="orbe__r">%s</b>\n'
            '  <span class="orbe__m letra">%s</span>\n'
            '</button>'
            % (ident, ident, cx / 10.0, cy / 10.0,
               H.escape(QUE.get(ident) or INTROS[ident][1].split(". ")[0] + "."),
               k + 1, H.escape(rotulo),
               CUENTA.get(ident) or ("%d apartados" % cuantos)))

    return ("""
<div class="ruedero">
<div class="rueda" data-rueda>
  <svg class="rueda__l" viewBox="0 0 1000 1000" aria-hidden="true" focusable="false">
    <circle cx="500" cy="500" r="@ORB@" class="rueda__o"/>
    <g class="rueda__r">@RADIOS@</g>
  </svg>

  <div class="rueda__c">
    <p class="letra rueda__k">Centro de Excelencia<br>Implantológica Giraldo</p>
    <p class="rueda__m">No medias<em>sonrisas</em></p>
    <p class="letra rueda__h">Vigo</p>
  </div>

  @ORBES@
</div>
<p class="rueda__q" id="ruedaq" role="status">@APARTADOS@ apartados, ocho documentos y catorce
  fases, en esta misma página. Señale un círculo para saber qué hay dentro; púlselo para entrar.</p>
</div>
<p class="rueda__pie letra">Rúa Bolivia nº 2 · Vigo · Uso interno y confidencial ·
  Versión @VERSION@</p>
""".replace("@RADIOS@", "".join(radios))
   .replace("@ORBES@", "\n".join(piezas))
   .replace("@ORB@", "%.0f" % RUEDA_R)
   .replace("@APARTADOS@", str(total)))


def sec_inicio(indice, total, voces, mapa_svg, tarjetas):
    hechos = "".join(
        '<div class="hecho"><b>%s</b><span class="letra">%s</span><p>%s</p></div>'
        % (n.replace("@TOTAL@", str(total)).replace("@ACC@", str(CATALOGO["total"])),
           H.escape(r), H.escape(q))
        for n, r, q in HECHOS)
    ideas = "".join(
        '<article class="idea"><p class="letra">%s</p><h3>%s</h3><p class="idea__q">%s</p>%s</article>'
        % (H.escape(k), H.escape(t), H.escape(q), cifras(c))
        for k, t, q, c in INICIO_BLOQUES)
    puertas = "".join(
        '<button type="button" class="puerta" data-ir-sec="%s">'
        '<span class="letra">%02d</span><b>%s</b><span class="puerta__q">%s</span>'
        '<span class="puerta__m letra">%d apartados</span></button>'
        % (i, n + 1, H.escape(nombre), H.escape(INTROS[i][0]), cuantos)
        for n, (i, _rot, nombre, cuantos) in enumerate(indice))

    return """
<section class="sec" id="inicio" data-sec="inicio">

  @@RUEDA@@

  <div class="portada" data-frente>
    <div class="portada__i">@@ARTE@@</div>
    <div class="portada__c">
      <p class="letra portada__k">Lo que hay detrás de la rueda</p>
      <h1>No medias<br><em>sonrisas</em></h1>
      <p class="portada__l">Le devolvemos su sonrisa completa, en el menor tiempo posible,
        y le cuidamos para siempre. Todo lo que sigue explica cómo se cumple esa frase, y
        quién responde de cada parte.</p>
      <div class="portada__b">
        <button type="button" class="bt bt--fuerte" data-ir-sec="recorridos">Elegir un recorrido</button>
        <button type="button" class="bt" data-ir-sec="mapa">Ver el mapa</button>
      </div>
    </div>
    <p class="portada__pie letra">Rúa Bolivia nº 2 · Vigo · Uso interno y confidencial</p>
    <span class="portada__baja" aria-hidden="true"><i></i></span>
  </div>

  <div class="banda">
    <div class="banda__c">
      <p class="letra">Por dónde empezar</p>
      <h2>Nadie lee un sistema entero.<br>Se entra con una pregunta.</h2>
      <p class="banda__q">Diez recorridos, cada uno con sus paradas en orden. Se abre uno, se
        avanza parada a parada y se vuelve donde estaba. Nada se pierde de vista.</p>
    </div>
    <div class="rutas">@@TARJETAS@@</div>
  </div>

  <div class="banda banda--mapa" data-frente>
    <div class="banda__c">
      <p class="letra">El recorrido del paciente</p>
      <h2>Catorce fases, y ninguna se salta</h2>
      <p class="banda__q">Pulse cualquier fase y se abre entera, con sus minutos, su responsable
        y lo que produce. Del lector se vuelve al mapa sin perder el sitio.</p>
    </div>
    @@MAPA@@
  </div>

  <div class="banda banda--noche" data-frente>
    <div class="banda__i">@@ARTE2@@</div>
    <div class="banda__c">
      <p class="letra">Los hechos</p>
      <h2>Lo que hay debajo de esas dos frases</h2>
    </div>
    <div class="hechos">@@HECHOS@@</div>
  </div>

  <div class="banda">
    <div class="banda__c">
      <p class="letra">Cuatro cosas antes de entrar</p>
      <h2>El método, el equipo, la tecnología y el cuidado</h2>
      <p class="banda__q">No están en ningún documento porque en un documento no hacen falta.
        En un sitio son lo primero que se busca.</p>
    </div>
    <div class="ideas">@@IDEAS@@</div>
  </div>

  <div class="banda">
    <div class="banda__c">
      <p class="letra">Lo que no haremos nunca</p>
      <h2>Un centro se reconoce antes por sus prohibiciones</h2>
      <p class="banda__q">Estas seis están escritas y son las que se auditan primero cuando algo
        va mal.</p>
    </div>
    <ol class="prohibido">@@PRINCIPIOS@@</ol>
  </div>

  <div class="banda">
    <div class="banda__c">
      <p class="letra">Preguntas</p>
      <h2>Contestadas con lo que el sistema dice</h2>
    </div>
    <div class="faq">@@PREGUNTAS@@</div>
  </div>

  <div class="banda">
    <div class="banda__c">
      <p class="letra">Los ocho documentos</p>
      <h2>Cada uno es una sección, con su documento entero dentro</h2>
    </div>
    <div class="puertas">@@PUERTAS@@</div>
  </div>

  <div class="banda banda--pie" data-frente>
    <div class="banda__i">@@ARTE3@@</div>
    <div class="contacto">
      <div><p class="letra">El centro</p><p>Centro de Excelencia Implantológica Giraldo<br>
        Rúa Bolivia nº 2 · 36203 Vigo · Pontevedra</p></div>
      <div><p class="letra">Esta edición</p><p>Versión @VERSION@ · @FECHA@<br>
        Los ocho documentos comparten número y fecha</p></div>
      <div><p class="letra">Uso</p><p>Interno y confidencial. Contiene información económica,
        laboral y estratégica; no se difunde fuera de la organización sin autorización expresa
        de la Dirección General.</p></div>
    </div>
  </div>

</section>
""".replace("@@RUEDA@@", rueda(indice, total)) \
   .replace("@@ARTE@@", imagenes.arte("campo", "0 0 1200 600", "arte--hero")) \
   .replace("@@ARTE2@@", imagenes.arte("trama", "150 60 900 480")) \
   .replace("@@ARTE3@@", imagenes.arte("campo2", "0 240 1200 360")) \
   .replace("@@TARJETAS@@", tarjetas).replace("@@MAPA@@", mapa_svg) \
   .replace("@@HECHOS@@", hechos).replace("@@IDEAS@@", ideas) \
   .replace("@@PUERTAS@@", puertas) \
   .replace("@@PRINCIPIOS@@", "".join(
       '<li><b>%s</b><p>%s</p></li>' % (H.escape(k), H.escape(q)) for k, q in PRINCIPIOS)) \
   .replace("@@PREGUNTAS@@", "".join(
       '<details class="faq__p"><summary>%s</summary><p>%s</p></details>'
       % (H.escape(k), H.escape(q)) for k, q in PREGUNTAS)) \
   .replace("@TOTAL@", str(total))


def sec_recorridos(rutas):
    return """
<section class="sec" id="recorridos" data-sec="recorridos">
  @@FRENTE@@
  <div class="rutas rutas--todas">@@RUTAS@@</div>
</section>
""".replace("@@RUTAS@@", rutas).replace("@@FRENTE@@", frente(
        "recorridos", "Diez maneras de entrar",
        "Elija por dónde quiere empezar",
        "Un recorrido es una pregunta convertida en camino. Cinco a nueve paradas, en orden, "
        "cada una con lo que hay que mirar y por qué. Se abre una parada, se lee entera, se "
        "pasa a la siguiente y se vuelve cuando se quiere: el recorrido no se pierde.", "10"))


def sec_mapa(mapa_svg):
    return """
<section class="sec" id="mapa" data-sec="mapa">
  @@FRENTE@@
  @@MAPA@@
</section>
""".replace("@@MAPA@@", mapa_svg).replace("@@FRENTE@@", frente(
        "mapa", "El recorrido del paciente",
        "Catorce fases, de la llamada al mantenimiento",
        "Cada fase construye sobre la anterior: la información recogida en la llamada "
        "personaliza la recepción, la anamnesis alimenta la presentación y el cierre abre el "
        "circuito de producción. La cadena es tan fuerte como su eslabón más débil, y por eso "
        "ninguna fase se salta «por falta de tiempo». Pulse una y se abre entera; del lector "
        "se vuelve aquí.", "14"))


CSS = """
/* ===========================================================================
   EL CENTRO GIRALDO · LA WEB

   Blanco, mucho blanco. Una tipografía ligera, la letra espaciada en los
   rótulos pequeños y el aire suficiente entre bloques para que ninguno tenga
   que competir con el de al lado. Un solo color, y solo para lo que se puede
   pulsar. Ni sombras, ni esquinas redondeadas, ni cajas dentro de cajas: si
   hay que separar dos cosas, se separan con espacio.

   La paleta del sistema visual de los documentos se reescribe entera aquí
   —incluidos los colores de puesto y los del semáforo, que la literatura trae
   dentro— para que ni un documento se salga del acuerdo.
   =========================================================================== */
:root{
  --negro:#111112; --tinta:#111112; --ink:#1A1A1D; --ink-2:#55555E;
  --muted:#8E8E97; --linea:#E6E6E9; --linea-2:#F1F1F3;
  --papel:#FFFFFF; --blanco:#FFFFFF; --gris:#FAFAFB;
  --azul:#1F45FF; --azul-o:#0A2ED6; --azul-p:#EDF0FF;

  --paper:var(--papel); --surface:var(--blanco); --surface-2:var(--gris);
  --line:var(--linea); --line-soft:var(--linea-2);
  --accent:var(--azul); --accent-ink:var(--azul-o); --accent-fuerte:var(--azul-o);
  --accent-soft:var(--azul-p); --acido:var(--azul-p); --acido-ink:var(--azul-o);
  --signal:var(--tinta); --alerta:var(--negro);
  --rol-recepcion:var(--muted); --rol-doctor:var(--ink-2); --rol-higienista:var(--muted);
  --rol-auxiliar:var(--muted); --rol-rac:var(--ink-2); --rol-direccion:var(--tinta);
  --sem-verde:var(--azul); --sem-amarillo:var(--muted); --sem-naranja:var(--ink-2);
  --sem-rojo:var(--negro);
  --radio:0px; --radio-s:0px; --sombra-1:none; --sombra-2:none;

  --nav:4.2rem; --texto:66ch; --ancho:78rem; --aire:clamp(5rem,10vw,10rem);
  /* el margen de la columna de lectura, para que lo que se sale a sangre
     vuelva a alinearse con el texto por dentro */
  --marco:max(2rem,calc(50vw - 37rem));
  /* lo que hay que subir una banda para que empiece en el borde de arriba:
     el aire de la sección y la barra, que ocupa sitio por ser pegajosa */
  --saca:calc((var(--aire) + var(--nav)) * -1);
  --e:cubic-bezier(.16,.84,.44,1);
}
html{-webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale}
body{background:var(--blanco);color:var(--tinta);font-weight:400}
*:focus-visible{outline:1px solid var(--azul);outline-offset:3px}
::selection{background:var(--azul);color:#fff}

/* La letra espaciada: el único gesto tipográfico de la casa. Va en los
   rótulos pequeños, nunca en el texto largo, que se leería peor. */
.letra{font-family:var(--f-mono);font-size:.6rem;letter-spacing:.28em;text-transform:uppercase;
  color:var(--muted);display:block}

h1,h2,h3,h4{font-weight:400;letter-spacing:-.02em}
.avance{position:fixed;inset:0 auto auto 0;height:1px;width:0;background:var(--azul);z-index:70;
  transition:width .12s linear}

/* --- la barra ------------------------------------------------------------- */
.nav{position:sticky;top:0;z-index:60;background:rgba(255,255,255,.92);
  backdrop-filter:saturate(1.4) blur(12px);border-bottom:1px solid var(--linea-2)}
/* La barra ocupa el ancho de la pantalla, no el de la columna de lectura: con
   el tope de setenta y ocho unidades, nueve entradas y dos botones no cabían
   ni en una pantalla de mil novecientos. */
.nav__f{display:flex;align-items:center;gap:1.2rem;height:var(--nav);padding:0 2.4rem}
.nav__m{display:flex;align-items:baseline;gap:.5rem;text-decoration:none;color:var(--negro);
  font-size:.88rem;font-weight:500;letter-spacing:.12em;text-transform:uppercase;flex:none;
  cursor:pointer;background:none;border:0;font-family:inherit}
.nav__m em{font-style:normal;font-family:var(--f-mono);font-size:.55rem;letter-spacing:.16em;
  color:var(--muted)}
.nav__l{display:flex;gap:0;flex:1 1 auto;min-width:0;overflow-x:auto;scrollbar-width:none;
  height:100%;justify-content:center}
.nav__l::-webkit-scrollbar{display:none}
.nav__l button{font:inherit;font-size:.6rem;letter-spacing:.1em;text-transform:uppercase;
  cursor:pointer;border:0;background:none;color:var(--ink-2);padding:0 .55rem;white-space:nowrap;
  position:relative;height:100%;transition:color .2s var(--e)}
.nav__l button::after{content:"";position:absolute;inset:auto .55rem 1.2rem .55rem;height:1px;
  background:var(--azul);transform:scaleX(0);transform-origin:left;
  transition:transform .28s var(--e)}
.nav__l button:hover{color:var(--negro)}
.nav__l button.es-on{color:var(--negro)}
.nav__l button.es-on::after,.nav__l button.es-abierto::after{transform:scaleX(1)}
.nav__b{display:flex;gap:.2rem;flex:none;align-items:center}
/* Las dos maneras nuevas de entrar, siempre a mano y fuera del índice: el
   índice es el de los documentos y no se toca. */
.nav__ruta{font:inherit;font-size:.6rem;letter-spacing:.12em;text-transform:uppercase;
  cursor:pointer;background:none;border:0;color:var(--negro);padding:.5rem .55rem;
  transition:color .2s var(--e)}
.nav__ruta:hover{color:var(--azul)}
.nav__ruta:first-child{color:var(--azul)}
.nav__sep{width:1px;height:1.1rem;background:var(--linea);margin:0 .5rem}
.abrepal{display:flex;align-items:center;gap:.5rem;padding:.4rem .6rem;background:none;
  border:0;color:var(--muted);font:inherit;font-size:.62rem;letter-spacing:.16em;
  text-transform:uppercase;cursor:pointer}
.abrepal:hover{color:var(--negro)}
.icono{font:inherit;cursor:pointer;display:inline-flex;align-items:center;justify-content:center;
  width:2rem;height:2rem;border:0;background:none;color:var(--muted);line-height:1}
.icono:hover:not(:disabled){color:var(--negro)}
.icono:disabled{opacity:.25;cursor:default}
.paneles{border-top:1px solid var(--linea-2);background:var(--blanco);
  max-height:min(62vh,32rem);overflow-y:auto}
.paneles[hidden]{display:none}
.sub{max-width:var(--ancho);margin:0 auto;padding:2.4rem 2rem 3rem;columns:3;column-gap:3rem}
.sub__g{break-inside:avoid;margin:1.4rem 0 .6rem;font-family:var(--f-mono);font-size:.58rem;
  letter-spacing:.22em;text-transform:uppercase;color:var(--azul)}
.sub__g:first-child{margin-top:0}
.sub a{break-inside:avoid;display:flex;gap:.9rem;align-items:baseline;text-decoration:none;
  color:var(--ink-2);font-size:.88rem;line-height:1.5;padding:.32rem 0}
.sub a span{font-family:var(--f-mono);font-size:.6rem;color:var(--muted);flex:none;min-width:1.5rem}
.sub a:hover{color:var(--azul)}

/* --- las secciones -------------------------------------------------------- */
.sec{max-width:var(--ancho);margin:0 auto;padding:var(--aire) 2rem calc(var(--aire) * 1.2)}
.sitio--vivo .sec{display:none}
.sitio--vivo .sec.es-on{display:block;animation:entra .3s var(--e)}
@keyframes entra{from{opacity:0}to{opacity:1}}
@media(prefers-reduced-motion:reduce){.sitio--vivo .sec.es-on{animation:none}}

.cab{position:relative;max-width:54rem;padding-bottom:var(--aire);margin-bottom:0}
.cab__n{position:absolute;top:-2.4rem;right:0;font-size:clamp(7rem,16vw,14rem);line-height:.75;
  font-weight:300;letter-spacing:-.06em;color:var(--linea-2);pointer-events:none;user-select:none}
.cab > *{position:relative;z-index:1}
.cab h1{font-size:clamp(2.6rem,6vw,4.6rem);line-height:1.06;letter-spacing:-.035em;
  margin:1.8rem 0 0;font-weight:300;max-width:17ch}
.cab h1 em{font-style:normal;color:var(--azul);display:block}
.cab__p{margin:2.4rem 0 0;font-size:1.02rem;line-height:1.85;color:var(--ink-2);max-width:60ch;
  font-weight:400}
.cab__p b{color:var(--negro);font-weight:500}

.banda{padding:var(--aire) 0;border-top:1px solid var(--linea-2)}
.banda:first-child{border-top:0}
.banda__c{max-width:52rem;margin:0 auto calc(var(--aire) * .55);text-align:center}
.banda__c h2{font-size:clamp(1.7rem,3.6vw,2.7rem);line-height:1.18;letter-spacing:-.028em;
  margin:1.2rem 0 0;font-weight:300}
.banda__q{margin:1.6rem 0 0;color:var(--ink-2);line-height:1.85;max-width:52ch;
  margin-left:auto;margin-right:auto}
.lienzo{margin-bottom:calc(var(--aire) * .9)}
.lienzo__cab{margin-bottom:2.6rem;max-width:54rem}
.lienzo__cab h2{font-size:clamp(1.3rem,2.4vw,1.8rem);letter-spacing:-.024em;margin:0;
  font-weight:400}
.lienzo__cab p{margin:.9rem 0 0;color:var(--ink-2);line-height:1.8;max-width:58ch}
.rotulillo{font-family:var(--f-mono);font-size:.58rem;letter-spacing:.26em;text-transform:uppercase;
  color:var(--muted);margin:0 0 1.2rem}
.cifras{display:flex;flex-wrap:wrap;gap:2.6rem;margin:2rem 0 0}
.cifras b{display:block;font-size:1.5rem;font-weight:300;letter-spacing:-.02em;color:var(--negro)}
.cifras span{display:block;margin-top:.4rem;font-family:var(--f-mono);font-size:.56rem;
  letter-spacing:.2em;text-transform:uppercase;color:var(--muted)}

/* --- portada -------------------------------------------------------------- */
.portada{text-align:center;padding:calc(var(--aire) * .9) 0 var(--aire)}
.portada__k{margin:0 0 3rem}
.portada h1{font-size:clamp(3.4rem,11vw,8rem);line-height:.96;letter-spacing:-.05em;
  font-weight:300;margin:0}
.portada h1 em{font-style:normal;color:var(--azul)}
.portada__l{margin:3rem auto 0;max-width:34ch;font-size:clamp(1rem,1.9vw,1.28rem);
  line-height:1.75;color:var(--ink-2);font-weight:300}
.portada__b{display:flex;flex-wrap:wrap;gap:.6rem;justify-content:center;margin-top:3.4rem}
.portada__pie{margin-top:4rem}
.bt{font:inherit;font-size:.66rem;letter-spacing:.2em;text-transform:uppercase;cursor:pointer;
  padding:1rem 2rem;border:1px solid var(--linea);background:none;color:var(--negro);
  transition:border-color .24s var(--e),background .24s var(--e),color .24s var(--e)}
.bt:hover{border-color:var(--negro)}
.bt--fuerte{background:var(--negro);border-color:var(--negro);color:#fff}
.bt--fuerte:hover{background:var(--azul);border-color:var(--azul)}

/* --- los recorridos -------------------------------------------------------- */
/* Sin rejilla de fondo: con diez tarjetas en cuatro columnas quedaban dos
   huecos grises al final que parecían un error. Cada tarjeta lleva su raya. */
.rutas{display:grid;grid-template-columns:repeat(auto-fill,minmax(17rem,1fr));gap:1.6rem 2.6rem}
.rutacard{font:inherit;text-align:left;cursor:pointer;border:0;background:none;
  padding:1.6rem 0 1.8rem;display:flex;flex-direction:column;gap:.9rem;
  border-top:1px solid var(--negro);transition:opacity .26s var(--e)}
.rutacard::after{content:"";display:block;height:1px;background:var(--azul);width:0;margin-top:.9rem;
  transition:width .3s var(--e)}
.rutacard:hover::after{width:100%}
.rutacard b{font-size:1.06rem;font-weight:400;line-height:1.4;color:var(--negro)}
.rutacard__m{padding-top:1.4rem;margin-top:auto}
.rutacard:hover b{color:var(--azul)}
.rutas--todas{display:block;background:none;border:0}
.wruta{padding:var(--aire) 0;border-top:1px solid var(--linea-2)}
.wruta:first-child{border-top:0;padding-top:calc(var(--aire) * .6)}
.wruta__cab{max-width:52rem;margin-bottom:3rem}
.wruta__cab h3{font-size:clamp(1.5rem,3vw,2.2rem);line-height:1.16;letter-spacing:-.028em;
  margin:1.2rem 0 0;font-weight:300}
.wruta__q{margin:1.4rem 0 2.2rem;color:var(--ink-2);line-height:1.85;max-width:56ch}
.paradas{list-style:none;margin:0;padding:0;border-top:1px solid var(--linea-2)}
.parada__b{display:flex;align-items:baseline;gap:1.6rem;width:100%;text-align:left;font:inherit;
  cursor:pointer;background:none;border:0;border-bottom:1px solid var(--linea-2);
  padding:1.5rem .4rem;transition:padding .26s var(--e),background .26s var(--e)}
.parada__b:hover{background:var(--gris);padding-left:1rem}
.parada__n{font-family:var(--f-mono);font-size:.62rem;color:var(--azul);flex:none;min-width:2rem}
.parada__t{flex:1;min-width:0}
.parada__t b{display:block;font-size:1.05rem;font-weight:400;color:var(--negro);line-height:1.4}
.parada__t span{display:block;margin-top:.5rem;font-size:.88rem;line-height:1.7;color:var(--ink-2);
  max-width:62ch}
.parada__i{flex:none;text-align:right}

/* --- el mapa de las catorce fases ------------------------------------------ */
.mapa14{display:flex;flex-direction:column;gap:calc(var(--aire) * .5)}
.mapa14__t{margin:0 0 1.8rem;text-align:center}
.nodos{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:1px;
  background:var(--linea);border-top:1px solid var(--linea);border-left:1px solid var(--linea)}
.nodos--post{grid-template-columns:repeat(2,minmax(0,1fr));max-width:34rem;margin:0 auto}
.nodo{font:inherit;text-align:left;cursor:pointer;background:var(--blanco);border:0;
  border-right:1px solid var(--linea);border-bottom:1px solid var(--linea);margin:0 -1px -1px 0;
  padding:1.6rem 1.3rem 1.7rem;display:flex;flex-direction:column;gap:.6rem;min-height:8.5rem;
  transition:background .26s var(--e)}
.nodo:hover:not(:disabled),.nodo:focus-visible{background:var(--negro)}
.nodo:hover:not(:disabled) .nodo__r,.nodo:focus-visible .nodo__r{color:#fff}
.nodo:hover:not(:disabled) .nodo__m,.nodo:focus-visible .nodo__m{color:rgba(255,255,255,.5)}
.nodo:disabled{cursor:default;opacity:.5}
.nodo__n{font-family:var(--f-mono);font-size:.58rem;letter-spacing:.2em;color:var(--azul)}
.nodo__r{font-size:.9rem;font-weight:400;color:var(--negro);line-height:1.4}
.nodo__m{margin-top:auto;font-family:var(--f-mono);font-size:.55rem;letter-spacing:.16em;
  text-transform:uppercase;color:var(--muted)}

/* --- hechos, ideas, prohibiciones, preguntas, puertas ---------------------- */
.hechos{display:grid;grid-template-columns:repeat(auto-fill,minmax(15rem,1fr));gap:3rem 2.6rem}
.hecho b{display:block;font-size:2.4rem;font-weight:300;letter-spacing:-.035em;color:var(--negro);
  line-height:1}
.hecho .letra{margin-top:.9rem;color:var(--azul)}
.hecho p{margin:1rem 0 0;font-size:.86rem;line-height:1.75;color:var(--ink-2)}
.ideas{display:grid;grid-template-columns:repeat(auto-fit,minmax(20rem,1fr));gap:4rem 3.6rem}
.idea h3{margin:1.2rem 0 0;font-size:1.4rem;letter-spacing:-.022em;font-weight:400;max-width:20ch}
.idea__q{margin:1.3rem 0 0;color:var(--ink-2);line-height:1.85}
.idea .cifras{gap:1.8rem;margin-top:2rem;padding-top:1.6rem;border-top:1px solid var(--linea-2)}
.idea .cifras b{font-size:1.05rem}
.prohibido{list-style:none;margin:0;padding:0;counter-reset:p;display:grid;
  grid-template-columns:repeat(auto-fit,minmax(20rem,1fr));gap:3.4rem 3rem}
.prohibido li{counter-increment:p}
.prohibido li::before{content:counter(p,decimal-leading-zero);font-family:var(--f-mono);
  font-size:.58rem;letter-spacing:.24em;color:var(--azul);display:block;margin-bottom:1rem}
.prohibido b{display:block;font-size:1.06rem;font-weight:400;color:var(--negro);line-height:1.4}
.prohibido p{margin:.9rem 0 0;font-size:.88rem;line-height:1.8;color:var(--ink-2)}
.faq{max-width:52rem;margin:0 auto;border-top:1px solid var(--linea)}
.faq__p{border-bottom:1px solid var(--linea-2)}
.faq__p summary{cursor:pointer;list-style:none;padding:1.6rem 2.6rem 1.6rem 0;position:relative;
  font-size:1.05rem;font-weight:400;color:var(--negro)}
.faq__p summary::-webkit-details-marker{display:none}
.faq__p summary::after{content:"";position:absolute;right:.5rem;top:2.1rem;width:11px;height:1px;
  background:var(--azul)}
.faq__p summary::before{content:"";position:absolute;right:1rem;top:1.6rem;width:1px;height:11px;
  background:var(--azul);transition:transform .24s var(--e)}
.faq__p[open] summary::before{transform:scaleY(0)}
.faq__p summary:hover{color:var(--azul)}
.faq__p p{margin:0 0 1.8rem;font-size:.95rem;line-height:1.85;color:var(--ink-2);max-width:58ch}
.puertas{display:grid;grid-template-columns:repeat(auto-fill,minmax(16rem,1fr));gap:1px;
  background:var(--linea);border-top:1px solid var(--linea);border-left:1px solid var(--linea)}
.puerta{font:inherit;text-align:left;cursor:pointer;border:0;background:var(--blanco);
  padding:2rem 1.7rem 2.2rem;display:flex;flex-direction:column;gap:.8rem;
  border-right:1px solid var(--linea);border-bottom:1px solid var(--linea);margin:0 -1px -1px 0;
  transition:background .26s var(--e)}
.puerta b{font-size:1.05rem;font-weight:400;color:var(--negro);line-height:1.4}
.puerta__q{font-size:.85rem;line-height:1.7;color:var(--ink-2)}
.puerta__m{margin-top:auto;padding-top:1.4rem}
.puerta:hover{background:var(--negro)}
.puerta:hover b,.puerta:hover .puerta__q{color:#fff}
.puerta:hover .letra{color:rgba(255,255,255,.55)}
.banda--pie{border-top:1px solid var(--negro)}
.contacto{display:grid;grid-template-columns:repeat(auto-fit,minmax(15rem,1fr));gap:3rem}
.contacto p:not(.letra){margin:1rem 0 0;font-size:.88rem;line-height:1.85;color:var(--ink-2)}

/* --- los bloques de datos de cada sección --------------------------------- */
.reloj__barra{display:flex;border-top:1px solid var(--linea);border-bottom:1px solid var(--linea);
  height:5rem}
.reloj__t{display:flex;flex-direction:column;justify-content:space-between;align-items:flex-start;
  padding:.7rem .6rem;text-decoration:none;color:var(--ink-2);border-right:1px solid var(--linea-2);
  overflow:hidden;min-width:0;box-sizing:border-box;flex-shrink:1;
  transition:background .24s var(--e),color .24s var(--e)}
.reloj__t:last-child{border-right:0}
.reloj__t:hover{background:var(--negro);color:#fff}
.reloj__t:hover .reloj__n{color:var(--azul-p)}
.reloj__t:hover .reloj__m{color:rgba(255,255,255,.6)}
.reloj__n{font-family:var(--f-mono);font-size:.58rem;letter-spacing:.14em;color:var(--azul)}
.reloj__r{font-size:.72rem;line-height:1.25;overflow:hidden;text-overflow:ellipsis;
  display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;white-space:normal}
.reloj__m{font-family:var(--f-mono);font-size:.56rem;color:var(--muted)}
.reloj__eje{position:relative;height:1.4rem;margin-top:.6rem}
.reloj__eje span{position:absolute;transform:translateX(-50%);font-family:var(--f-mono);
  font-size:.56rem;letter-spacing:.14em;color:var(--muted)}
.reloj__eje span:first-child{transform:none}
.reloj__eje span:last-child{transform:translateX(-100%)}
.carriles{display:flex;flex-direction:column;gap:.5rem}
.carril{display:grid;grid-template-columns:9rem minmax(0,1fr);gap:1.4rem;align-items:center}
.carril__q{margin:0;font-size:.78rem;color:var(--ink-2);text-align:right}
.carril__p{position:relative;height:1.9rem;border-bottom:1px solid var(--linea-2)}
.carril__b{position:absolute;top:.25rem;bottom:.25rem;background:var(--linea-2);border:0;
  font-family:var(--f-mono);font-size:.56rem;color:var(--muted);display:flex;align-items:center;
  justify-content:center;text-decoration:none;transition:background .24s var(--e)}
.carril__b.es-jefe{background:var(--negro);color:#fff}
.carril__b:hover{background:var(--azul);color:#fff}
.puestosel{display:flex;flex-wrap:wrap;gap:0;border-bottom:1px solid var(--linea);
  margin-bottom:3.6rem}
.puestobt{font:inherit;cursor:pointer;text-align:left;background:none;border:0;
  padding:1.1rem 1.5rem 1.2rem;flex:1 1 auto;position:relative;
  transition:color .24s var(--e)}
.puestobt::after{content:"";position:absolute;inset:auto 0 -1px 0;height:1px;background:var(--negro);
  transform:scaleX(0);transition:transform .28s var(--e)}
.puestobt b{display:block;font-size:.92rem;font-weight:400;color:var(--ink-2)}
.puestobt span{display:block;margin-top:.4rem;font-family:var(--f-mono);font-size:.55rem;
  letter-spacing:.18em;text-transform:uppercase;color:var(--muted)}
.puestobt:hover b{color:var(--negro)}
.puestobt.es-on::after{transform:scaleX(1)}
.puestobt.es-on b{color:var(--negro)}
.puesto h3{margin:1.2rem 0 0;font-size:clamp(1.5rem,3vw,2.1rem);letter-spacing:-.026em;
  font-weight:300}
.puesto__q{margin:1.4rem 0 0;font-size:1rem;line-height:1.85;color:var(--ink-2);max-width:54ch}
.puesto .cifras{margin:2.6rem 0 3.4rem;padding:1.8rem 0;border-top:1px solid var(--linea-2);
  border-bottom:1px solid var(--linea-2)}
.wraci{display:grid;grid-template-columns:repeat(14,minmax(0,1fr));gap:4px}
.wraci__c{aspect-ratio:1;display:flex;flex-direction:column;align-items:center;
  justify-content:center;background:var(--gris);cursor:help}
.wraci__f{font-family:var(--f-mono);font-size:.5rem;color:var(--muted)}
.wraci__p{font-family:var(--f-mono);font-size:.68rem;color:var(--muted)}
.wraci__c.wes-ra{background:var(--negro)}
.wraci__c.wes-r{background:var(--azul)}
.wraci__c.wes-a{background:var(--ink-2)}
.wraci__c.wes-ra .wraci__p,.wraci__c.wes-r .wraci__p,.wraci__c.wes-a .wraci__p,
.wraci__c.wes-ra .wraci__f,.wraci__c.wes-r .wraci__f,.wraci__c.wes-a .wraci__f{color:#fff}
.wraci__c.wes-c{background:var(--azul-p)}
.wraci__c.wes-c .wraci__p{color:var(--azul-o)}
.wraci__c.wes-i{background:var(--blanco);border:1px solid var(--linea)}
.wraci__c.wes-no{background:none;border:1px dashed var(--linea-2)}
.wraci__c.wes-no .wraci__p{color:var(--linea)}
.leyenda{margin:1.4rem 0 0;font-size:.76rem;color:var(--muted);line-height:1.8}
.leyenda b{font-family:var(--f-mono);color:var(--negro)}
.puesto__cols{display:grid;grid-template-columns:repeat(auto-fit,minmax(19rem,1fr));gap:3.4rem;
  margin-top:3.6rem}
.lista2{list-style:none;margin:0;padding:0}
.lista2 li{font-size:.88rem;line-height:1.6;color:var(--ink-2);padding:.7rem 0;
  border-bottom:1px solid var(--linea-2)}
.lista2 li:last-child{border-bottom:0}
.lista2 .es-vacio{color:var(--muted)}
.puesto__ir{margin:3rem 0 0}
.wmapa{display:grid;grid-template-columns:repeat(auto-fill,minmax(11rem,1fr));gap:1px;
  background:var(--linea);border-top:1px solid var(--linea);border-left:1px solid var(--linea)}
.mfase{background:var(--blanco);padding:1.2rem 1.2rem 1.4rem;text-decoration:none;display:flex;
  flex-direction:column;gap:.3rem;border-right:1px solid var(--linea);
  border-bottom:1px solid var(--linea);margin:0 -1px -1px 0;transition:background .24s var(--e)}
.mfase:hover{background:var(--negro)}
.mfase:hover b{color:#fff}
.mfase:hover .mfase__r{color:rgba(255,255,255,.5)}
.mfase__n{font-family:var(--f-mono);font-size:.58rem;letter-spacing:.16em;color:var(--azul)}
.mfase b{font-size:.88rem;font-weight:400;color:var(--negro);line-height:1.4;margin-top:.4rem}
.mfase__r{font-family:var(--f-mono);font-size:.54rem;letter-spacing:.14em;text-transform:uppercase;
  color:var(--muted);margin-top:.6rem}
.estados{display:grid;grid-template-columns:repeat(auto-fill,minmax(13rem,1fr));gap:1px;
  background:var(--linea);border-top:1px solid var(--linea);border-left:1px solid var(--linea)}
.estado{font:inherit;text-align:left;cursor:pointer;background:var(--blanco);border:0;
  padding:1.3rem 1.3rem 1.5rem;border-right:1px solid var(--linea);
  border-bottom:1px solid var(--linea);margin:0 -1px -1px 0;transition:background .24s var(--e)}
.estado:hover{background:var(--gris)}
.estado.es-on{background:var(--negro)}
.estado.es-on b,.estado.es-on p{color:#fff}
.estado.es-on .estado__n{color:var(--azul-p)}
.estado__n{font-family:var(--f-mono);font-size:.56rem;letter-spacing:.18em;color:var(--azul)}
.estado b{display:block;margin-top:.5rem;font-size:.95rem;font-weight:400;color:var(--negro)}
.estado p{margin:.6rem 0 0;font-size:.79rem;line-height:1.65;color:var(--ink-2)}
.filtros{display:flex;flex-wrap:wrap;gap:1.4rem;align-items:flex-end;margin-bottom:2rem}
.filtro{display:flex;flex-direction:column;gap:.5rem}
.filtro span{font-family:var(--f-mono);font-size:.55rem;letter-spacing:.22em;
  text-transform:uppercase;color:var(--muted)}
.filtro select{font:inherit;font-size:.84rem;padding:.5rem .2rem;border:0;
  border-bottom:1px solid var(--linea);background:none;color:var(--tinta)}
.filtro select:focus{border-bottom-color:var(--azul);outline:none}
.limpiar{font:inherit;font-size:.6rem;letter-spacing:.2em;text-transform:uppercase;cursor:pointer;
  border:0;border-bottom:1px solid var(--linea);background:none;color:var(--muted);padding:.5rem 0}
.limpiar:hover{color:var(--negro);border-bottom-color:var(--negro)}
.cuentafiltro{font-family:var(--f-mono);font-size:.6rem;letter-spacing:.16em;color:var(--muted);
  margin-left:auto}
.tablawrap{overflow-x:auto}
.acciones{width:100%;border-collapse:collapse;font-size:.86rem;min-width:52rem}
.acciones th{font-family:var(--f-mono);font-size:.55rem;letter-spacing:.22em;text-transform:uppercase;
  color:var(--muted);text-align:left;padding:1rem .8rem;border-bottom:1px solid var(--negro);
  background:var(--blanco);position:sticky;top:0}
.acciones td{padding:1.1rem .8rem;border-bottom:1px solid var(--linea-2);vertical-align:top}
.acciones tr:hover td{background:var(--gris)}
.acc__cod{font-family:var(--f-mono);font-size:.66rem;letter-spacing:.12em;color:var(--azul);
  white-space:nowrap}
.acc__q b{display:block;font-weight:400;color:var(--negro);line-height:1.55}
.acc__q span{display:block;margin-top:.5rem;font-size:.74rem;color:var(--muted);line-height:1.6}
.acc__gana{color:var(--ink-2);line-height:1.6;max-width:22rem}
.acc__meta{white-space:nowrap}
.etq{display:inline-block;font-family:var(--f-mono);font-size:.55rem;letter-spacing:.1em;
  color:var(--ink-2);border:1px solid var(--linea);padding:.2rem .45rem;margin:0 .3rem .3rem 0}
.etq--verde{border-color:var(--azul);color:var(--azul)}
.etq--naranja{background:var(--negro);border-color:var(--negro);color:#fff}
.acc__ef{white-space:nowrap;font-family:var(--f-mono);font-size:.68rem;color:var(--muted)}
.barrita{display:inline-block;width:2.6rem;height:1px;background:var(--linea);margin-right:.6rem;
  position:relative;vertical-align:middle}
.barrita::before{content:"";position:absolute;inset:-1px auto -1px 0;width:var(--v);
  background:var(--azul)}
.wcampanas{display:grid;grid-template-columns:repeat(auto-fill,minmax(18rem,1fr));gap:3.4rem 3rem}
.wcampana__k{margin:0;font-family:var(--f-mono);font-size:.56rem;letter-spacing:.22em;
  color:var(--azul)}
.wcampana h4{margin:.7rem 0 0;font-size:1.05rem;letter-spacing:-.014em;font-weight:400}
.wcampana__r{margin:.9rem 0 0;font-size:.85rem;line-height:1.75;color:var(--ink-2)}
.wcampana__c{display:flex;gap:1.8rem;margin:1.6rem 0 0;padding-top:1.2rem;
  border-top:1px solid var(--linea-2)}
.wcampana__c dt{font-family:var(--f-mono);font-size:.52rem;letter-spacing:.2em;
  text-transform:uppercase;color:var(--muted)}
.wcampana__c dd{margin:.4rem 0 0;font-size:1rem;font-weight:400;color:var(--negro)}
.puente{display:flex;flex-direction:column;gap:.8rem}
.puente__t{height:3.2rem;padding:.6rem 1.2rem;background:var(--gris);
  border-left:1px solid var(--azul);width:max(var(--w),13rem);display:flex;flex-direction:column;
  justify-content:center}
.puente__r{font-size:.88rem;color:var(--negro)}
.puente__v{font-family:var(--f-mono);font-size:.66rem;letter-spacing:.1em;color:var(--ink-2)}
.puente__pie{margin:2rem 0 0;font-size:.88rem;line-height:1.8;color:var(--ink-2)}
.puente__pie b{color:var(--negro)}
.lienzo--indice .idx{columns:2;column-gap:3.6rem;border-top:1px solid var(--linea);
  padding-top:2.2rem}
.idx__g{break-inside:avoid;margin:1.8rem 0 .7rem;font-family:var(--f-mono);font-size:.56rem;
  letter-spacing:.24em;text-transform:uppercase;color:var(--azul)}
.idx__g:first-child{margin-top:0}
.idx__a{break-inside:avoid;display:flex;gap:1rem;align-items:baseline;text-decoration:none;
  color:var(--ink-2);padding:.45rem 0}
.idx__a span{font-family:var(--f-mono);font-size:.62rem;color:var(--muted);flex:none;min-width:1.6rem}
.idx__a b{font-size:.92rem;font-weight:400;line-height:1.55}
.idx__a:hover b{color:var(--azul)}
/* Los apartados se leen en el lector, no en la página. Sin guiones se ven
   todos seguidos, que es el documento entero. */
.sitio--vivo .hojas{display:none}
.ref{color:var(--ink-2)}
.gl{font:inherit;cursor:help;background:none;border:0;padding:0;color:inherit;
  border-bottom:1px solid var(--azul-p)}
.gl:hover{border-bottom-color:var(--azul);color:var(--azul)}
.salta{text-decoration:none;color:var(--azul)}
.salta__d{font-style:normal;font-family:var(--f-mono);font-size:.55rem;letter-spacing:.16em;
  text-transform:uppercase;color:var(--muted);margin-left:.5rem;white-space:nowrap}
.salta__d::before{content:"→ "}

/* ===========================================================================
   EL LECTOR
   Cualquier cosa se abre encima de lo que se estaba haciendo, se lee entera y
   se cierra: se vuelve exactamente donde se estaba. Si se abrió desde un
   recorrido, las flechas avanzan por sus paradas y arriba se ve cuántas
   quedan; si se abrió desde el mapa, avanzan por las catorce fases.
   =========================================================================== */
.lector{position:fixed;inset:0;z-index:90;display:flex;flex-direction:column;background:#fff;
  animation:sube .28s var(--e)}
.lector[hidden]{display:none}
@keyframes sube{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
@media(prefers-reduced-motion:reduce){.lector{animation:none}}
.lector__cab{display:flex;align-items:center;gap:1.4rem;padding:0 2rem;height:var(--nav);
  border-bottom:1px solid var(--linea-2);flex:none}
.lector__volver{font:inherit;font-size:.62rem;letter-spacing:.2em;text-transform:uppercase;
  cursor:pointer;background:none;border:0;color:var(--negro);display:flex;align-items:center;
  gap:.7rem;padding:0}
.lector__volver:hover{color:var(--azul)}
.lector__q{flex:1;min-width:0;text-align:center;font-family:var(--f-mono);font-size:.6rem;
  letter-spacing:.2em;text-transform:uppercase;color:var(--muted);white-space:nowrap;
  overflow:hidden;text-overflow:ellipsis}
.lector__nav{display:flex;gap:.2rem;align-items:center;flex:none}
.lector__paso{font-family:var(--f-mono);font-size:.6rem;letter-spacing:.16em;color:var(--muted);
  margin-right:.7rem;white-space:nowrap}
.lector__barra{height:1px;background:var(--linea-2);flex:none}
.lector__barra i{display:block;height:100%;background:var(--azul);width:0;
  transition:width .3s var(--e)}
.lector__cuerpo{flex:1;overflow-y:auto;overscroll-behavior:contain}
.lector__in{max-width:var(--texto);margin:0 auto;padding:calc(var(--aire) * .6) 2rem
  calc(var(--aire) * .9)}
/* El rótulo del apartado ya está en la cabecera del lector, con su documento
   y su parte: repetirlo dentro es decir dos veces lo mismo. */
.lector__in .hoja__k{display:none}
.lector__k{margin:0 0 2.4rem}
.lector__in h2,.lector__in h3{font-weight:300;letter-spacing:-.028em}
.lector__in .wrap{padding:0;max-width:none}
.lector__in .section{padding:0;background:none;border:0}
.lector__in .section + .section{margin-top:4rem;padding-top:4rem;border-top:1px solid var(--linea-2)}
.lector__in .reveal{opacity:1!important;transform:none!important}
.lector__in .phase__grid{grid-template-columns:minmax(0,1fr)}
.lector__in .phase__meta{position:static}
.lector__in .tablewrap{overflow-x:auto}
.lector__in a:not(.salta):not(.gl){color:var(--negro);text-decoration:none;
  border-bottom:1px solid var(--azul-p);transition:border-color .2s var(--e),color .2s var(--e)}
.lector__in a:not(.salta):not(.gl):hover{color:var(--azul);border-bottom-color:var(--azul)}
.lector__pie{border-top:1px solid var(--linea-2);padding:2.4rem 2rem;max-width:var(--texto);
  margin:0 auto;display:flex;gap:1rem;justify-content:space-between;align-items:center;
  flex-wrap:wrap}
.lector__sig{font:inherit;font-size:.9rem;cursor:pointer;background:none;border:0;
  color:var(--negro);text-align:left;padding:0;display:flex;flex-direction:column;gap:.4rem}
.lector__sig .letra{color:var(--azul)}
.lector__sig:hover b{color:var(--azul)}
.lector__sig b{font-weight:400}

/* --- lo que flota ---------------------------------------------------------- */
.velo{position:fixed;inset:0;z-index:95;display:flex;align-items:flex-start;justify-content:center;
  padding:10vh 1.2rem 1.2rem;background:rgba(17,17,18,.5);animation:vela .18s ease}
@keyframes vela{from{opacity:0}to{opacity:1}}
.velo[hidden]{display:none}
.flota{width:min(42rem,100%);max-height:78vh;display:flex;flex-direction:column;overflow:hidden;
  background:var(--blanco);animation:sube .22s var(--e)}
.flota__cab{display:flex;align-items:center;gap:.8rem;padding:1.2rem 1.4rem;
  border-bottom:1px solid var(--linea-2)}
.flota__cab h2{margin:0;font-size:.68rem;letter-spacing:.22em;text-transform:uppercase;
  font-weight:400;flex:1;color:var(--muted)}
.flota__cuerpo{overflow-y:auto;padding:1.6rem 1.6rem 2rem}
.flota__pie{padding:.9rem 1.4rem;border-top:1px solid var(--linea-2);font-family:var(--f-mono);
  font-size:.56rem;letter-spacing:.16em;color:var(--muted);display:flex;gap:1.4rem;flex-wrap:wrap}
.flota__pie kbd{border:1px solid var(--linea);padding:.12rem .35rem;font-family:inherit}
.pal__campo{display:flex;align-items:center;gap:.9rem;padding:1.3rem 1.4rem;
  border-bottom:1px solid var(--linea-2)}
.pal__campo input{flex:1;border:0;outline:none;background:none;font:inherit;font-size:1.05rem;
  font-weight:300;color:var(--tinta)}
.pal__lista{overflow-y:auto;padding:.4rem;max-height:52vh}
.pal__g{margin:1rem .8rem .4rem;font-family:var(--f-mono);font-size:.55rem;letter-spacing:.24em;
  text-transform:uppercase;color:var(--muted)}
.pal__i{display:flex;gap:1rem;align-items:baseline;width:100%;text-align:left;font:inherit;
  cursor:pointer;background:none;border:0;padding:.7rem .8rem;color:var(--ink-2)}
.pal__i span{font-family:var(--f-mono);font-size:.58rem;color:var(--muted);flex:none;min-width:1.4rem}
.pal__i b{font-weight:400;font-size:.92rem;line-height:1.45}
.pal__i i{font-style:normal;font-family:var(--f-mono);font-size:.55rem;letter-spacing:.14em;
  text-transform:uppercase;color:var(--muted);margin-left:auto;flex:none;padding-left:1rem}
.pal__i mark{background:var(--azul-p);color:var(--azul-o)}
.pal__i:hover{background:var(--gris)}
.pal__i.es-aqui{background:var(--negro);color:#fff}
.pal__i.es-aqui b,.pal__i.es-aqui span,.pal__i.es-aqui i{color:#fff}
.pal__i b .pal__ctx{display:block;font-family:inherit;font-size:.78rem;font-weight:400;
  color:var(--muted);margin-top:.4rem;line-height:1.7;letter-spacing:0}
.pal__i.es-aqui .pal__ctx{color:rgba(255,255,255,.7)}
.pal__nada{padding:2.4rem 1rem;text-align:center;color:var(--muted);font-size:.9rem}
.voz{position:absolute;z-index:99;width:min(22rem,calc(100vw - 2rem));background:var(--blanco);
  border:1px solid var(--negro);padding:1.3rem 1.4rem}
.voz[hidden]{display:none}
.voz b{display:block;font-size:.98rem;font-weight:400;color:var(--negro)}
.voz p{margin:.7rem 0 0;font-size:.86rem;line-height:1.75;color:var(--ink-2)}
.voz small{display:block;margin-top:1rem;padding-top:.8rem;border-top:1px solid var(--linea-2);
  font-family:var(--f-mono);font-size:.54rem;letter-spacing:.18em;text-transform:uppercase;
  color:var(--muted)}
.rec__g{margin:0 0 2.2rem}
.rec__g:last-child{margin-bottom:0}
.rec__t{margin:0 0 1rem;font-family:var(--f-mono);font-size:.55rem;letter-spacing:.24em;
  text-transform:uppercase;color:var(--azul)}
.rec__i{display:flex;gap:1.2rem;align-items:flex-start;padding:.9rem .4rem;text-decoration:none;
  color:inherit;width:100%;text-align:left;font:inherit;background:none;border:0;cursor:pointer;
  border-bottom:1px solid var(--linea-2)}
.rec__i:hover{background:var(--gris)}
.rec__i em{font-style:normal;font-family:var(--f-mono);font-size:.55rem;letter-spacing:.16em;
  color:var(--azul);flex:none;min-width:2.8rem;padding-top:.2rem}
.rec__i b{display:block;font-size:.92rem;font-weight:400;color:var(--negro)}
.rec__i p{margin:.4rem 0 0;font-size:.8rem;line-height:1.7;color:var(--ink-2)}
.tec{display:grid;grid-template-columns:auto 1fr;gap:.9rem 1.6rem;align-items:baseline}
.tec dt{font-family:var(--f-mono);font-size:.66rem;color:var(--negro);white-space:nowrap}
.tec dt kbd{border:1px solid var(--linea);padding:.16rem .45rem;font-family:inherit}
.tec dd{margin:0;font-size:.86rem;color:var(--ink-2);line-height:1.7}
.lupa{align-items:center;padding:4vh 4vw}
.lupa .flota{width:min(70rem,100%);max-height:92vh}
.lupa__lienzo{padding:2.4rem;overflow:auto}
.lupa__lienzo > *{max-width:100%;margin:0}
.lupa__lienzo svg{width:100%;height:auto}
.ampliable{cursor:zoom-in}
.pito{position:fixed;left:50%;bottom:2.4rem;transform:translateX(-50%);z-index:99;
  background:var(--negro);color:#fff;padding:.8rem 1.6rem;font-size:.62rem;letter-spacing:.2em;
  text-transform:uppercase;animation:sube .2s ease}
.pito[hidden]{display:none}

/* ====================================================================
   EL DESPLEGABLE
   Un titular que se pulsa y debajo aparece lo que hay. Sin JavaScript no
   hay nada que pulsar: todo queda abierto y el documento se lee entero.
   ==================================================================== */
.desp{border-top:1px solid var(--linea-2)}
.desp:last-child{border-bottom:1px solid var(--linea-2)}
.desp__h{margin:0;font:inherit;font-weight:400}
.desp__b{width:100%;display:flex;align-items:baseline;gap:1.6rem;padding:1.5rem .4rem;
  font:inherit;text-align:left;background:none;border:0;cursor:default;
  transition:background .2s var(--e),padding .26s var(--e)}
.sitio--vivo .desp__b{cursor:pointer}
.sitio--vivo .desp__b:hover{background:var(--gris);padding-left:1rem}
.desp__n{font-family:var(--f-mono);font-size:.6rem;letter-spacing:.1em;color:var(--azul);
  flex:none;min-width:3.2rem}
.desp__t{flex:1;min-width:0}
.desp__t b{display:block;font-size:1.05rem;font-weight:400;color:var(--negro);line-height:1.45}
.desp__t i{display:block;margin-top:.5rem;font-style:normal;font-family:var(--f-mono);
  font-size:.54rem;letter-spacing:.22em;text-transform:uppercase;color:var(--muted)}
.desp__x{display:none;flex:none;position:relative;width:12px;height:12px;
  align-self:center;margin-left:1rem}
.sitio--vivo .desp__x{display:block}
.desp__x::before,.desp__x::after{content:"";position:absolute;background:var(--negro);
  transition:transform .32s var(--e),background .2s var(--e)}
.desp__x::before{left:0;right:0;top:5px;height:1px}
.desp__x::after{top:0;bottom:0;left:5px;width:1px}
.desp.es-ab .desp__x::after{transform:scaleY(0)}
.sitio--vivo .desp__b:hover .desp__x::before,
.sitio--vivo .desp__b:hover .desp__x::after{background:var(--azul)}
.sitio--vivo .desp__c{display:grid;grid-template-rows:0fr;
  transition:grid-template-rows .34s var(--e)}
.sitio--vivo .desp.es-ab .desp__c{grid-template-rows:1fr}
.sitio--vivo .desp__in{min-height:0;overflow:hidden}
.desp__in{padding:.2rem 0 2.6rem}
.sitio--vivo .desp__in{padding:0}
.sitio--vivo .desp.es-ab .desp__in{padding:.2rem 0 2.6rem}
@media(prefers-reduced-motion:reduce){.sitio--vivo .desp__c{transition:none}}
.desp__in > section,.desp__in > div{max-width:none}

/* el grupo de desplegables, con su rótulo y su «abrir todo» */
.grupod{margin-top:calc(var(--aire) * .5)}
.grupod__cab{margin-bottom:1.4rem;padding-bottom:1.2rem;
  border-bottom:1px solid var(--negro);display:grid;gap:.9rem 2.6rem;
  grid-template-columns:minmax(0,1fr) auto}
.grupod__cab .rotulillo{margin:0;grid-column:1/-1}
.grupod__q{margin:0;flex:1;min-width:18rem;max-width:58ch;font-size:.92rem;line-height:1.75;
  color:var(--ink-2)}
.grupod__t{display:none;align-self:end;justify-self:end;font:inherit;font-family:var(--f-mono);font-size:.54rem;
  letter-spacing:.22em;text-transform:uppercase;color:var(--azul);background:none;border:0;
  border-bottom:1px solid var(--linea);padding:.35rem 0;cursor:pointer;flex:none}
.sitio--vivo .grupod__t{display:block}
.grupod__t:hover{border-color:var(--azul)}

/* el índice de un puesto: todo lo suyo, de un vistazo */
.puesto__idx{display:grid;grid-template-columns:repeat(auto-fill,minmax(17rem,1fr));
  gap:0 2.6rem;margin:2.6rem 0 0;border-top:1px solid var(--linea-2)}
.puesto__idx a{display:flex;gap:.8rem;align-items:baseline;padding:.9rem .1rem;
  border-bottom:1px solid var(--linea-2);text-decoration:none;font-size:.88rem;
  line-height:1.5;color:var(--ink-2)}
.puesto__idx a span{flex:none;min-width:1.5rem;font-family:var(--f-mono);font-size:.54rem;
  color:var(--azul)}
.puesto__idx a:hover{color:var(--azul)}
.leyenda--pista{color:var(--muted)}
.leyenda + .rotulillo,.wraci + .rotulillo,.fases-p + .rotulillo{margin-top:3rem}
.puesto .rotulillo{margin-top:3.2rem}
.puesto .cifras + .rotulillo{margin-top:3.4rem}
.sitio--vivo .wraci__c{cursor:pointer}
.wraci__c{font:inherit;border:0;padding:0}

/* las fases del puesto, con su nombre y su papel */
.fases-p{display:grid;grid-template-columns:repeat(auto-fill,minmax(20rem,1fr));
  gap:0 2.6rem;border-top:1px solid var(--linea-2)}
.fasep{display:flex;align-items:baseline;gap:.9rem;width:100%;padding:.85rem .1rem;
  font:inherit;text-align:left;background:none;border:0;border-bottom:1px solid var(--linea-2);
  cursor:default;transition:padding .22s var(--e),background .2s var(--e)}
.sitio--vivo .fasep{cursor:pointer}
.sitio--vivo .fasep:hover{background:var(--gris);padding-left:.7rem}
.fasep__n{flex:none;font-family:var(--f-mono);font-size:.54rem;color:var(--azul)}
.fasep__r{flex:1;min-width:0;font-size:.9rem;line-height:1.5;color:var(--negro)}
.fasep__p{flex:none;font-family:var(--f-mono);font-size:.5rem;letter-spacing:.14em;
  text-transform:uppercase;color:var(--muted)}
.fasep__p.wes-ra,.fasep__p.wes-r,.fasep__p.wes-a{color:var(--negro)}

/* el selector de puesto se queda arriba: se cambia de puesto sin subir */
.puestosel{position:sticky;top:calc(var(--nav) - 1px);z-index:6;background:var(--blanco)}

/* ====================================================================
   LA PRESENTACIÓN
   Las cuarenta y tres, legibles: cada una con su minuto, su parte y el
   guion del ponente debajo.
   ==================================================================== */
.presfil{display:flex;flex-wrap:wrap;align-items:center;gap:1rem 1.8rem;margin:2.8rem 0 0;
  padding-bottom:1.4rem;border-bottom:1px solid var(--linea)}
.presfil__b{font:inherit;font-family:var(--f-mono);font-size:.56rem;letter-spacing:.22em;
  text-transform:uppercase;background:none;cursor:pointer;color:var(--muted);
  border:1px solid var(--linea);padding:.7rem 1.2rem;transition:.2s var(--e)}
.presfil__b:hover{color:var(--negro);border-color:var(--negro)}
.presfil__b.es-on{background:var(--negro);border-color:var(--negro);color:#fff}
.presfil__q{margin:0;flex:1;min-width:16rem;font-size:.86rem;line-height:1.7;color:var(--muted)}
.presidx{display:grid;grid-template-columns:repeat(auto-fill,minmax(16rem,1fr));
  gap:0 2.6rem;margin:2.6rem 0 0}
.presidx a{display:block;padding:1.3rem .1rem 1.4rem;text-decoration:none;
  border-top:1px solid var(--negro)}
.presidx a span{display:block;font-family:var(--f-mono);font-size:.54rem;letter-spacing:.22em;
  text-transform:uppercase;color:var(--azul)}
.presidx a b{display:block;margin-top:.7rem;font-size:.98rem;font-weight:400;line-height:1.45;
  color:var(--negro)}
.presidx a i{display:block;margin-top:.7rem;font-style:normal;font-family:var(--f-mono);
  font-size:.54rem;letter-spacing:.16em;color:var(--muted)}
.presidx a:hover b{color:var(--azul)}
.parte{padding:var(--aire) 0 0}
.parte__k{margin:0;font-family:var(--f-mono);font-size:.56rem;letter-spacing:.24em;
  text-transform:uppercase;color:var(--azul)}
.parte h3{margin:1.1rem 0 0;font-size:clamp(1.4rem,2.8vw,2rem);font-weight:300;
  letter-spacing:-.026em;line-height:1.2;max-width:26ch;color:var(--negro)}
.parte__q{margin:1.2rem 0 2.4rem;max-width:60ch;font-size:.96rem;line-height:1.8;
  color:var(--ink-2)}
.parte .grupod__l{margin-top:2rem}
.parte[hidden]{display:none}

/* la diapositiva, dentro de la página: ni absoluta ni oculta */
#sitio .dia{margin:0 0 2.4rem}
#sitio .dia .slide{position:static;display:block;inset:auto;width:auto;height:auto;
  min-height:0;animation:none;border:1px solid var(--linea);background:var(--blanco);
  padding:clamp(1.8rem,3vw,2.8rem);overflow:visible}
#sitio .dia .slide--stmt{background:var(--negro);border-color:var(--negro)}
#sitio .dia .slide h2{font-size:clamp(1.3rem,2.3vw,1.85rem);max-width:32ch;
  font-weight:400;line-height:1.2}
#sitio .dia .slide--portada h1,#sitio .dia .slide--stmt h2{
  font-size:clamp(1.5rem,2.8vw,2.3rem);max-width:26ch}
#sitio .dia .slide--div .rom{font-size:clamp(2.2rem,5vw,4rem)}
#sitio .dia .slide .lede{max-width:64ch}
#sitio .deck--sitio,#lector .deck--sitio{display:block;position:static;height:auto;
  overflow:visible}
#sitio .deck--sitio .slide,#lector .deck--sitio .slide{position:static;display:block;
  inset:auto;width:auto;height:auto;min-height:0;animation:none;
  border:1px solid var(--linea);background:var(--blanco);
  padding:clamp(1.8rem,3vw,2.8rem);margin:0 0 1.6rem;overflow:visible}
#sitio .deck--sitio .slide--stmt,#lector .deck--sitio .slide--stmt{
  background:var(--negro);border-color:var(--negro)}
#sitio .deck--sitio .slide h2,#lector .deck--sitio .slide h2{
  font-size:clamp(1.3rem,2.3vw,1.85rem);max-width:32ch;font-weight:400;line-height:1.2}

/* el guion del ponente: lo que hasta ahora vivía escondido en las notas */
.guion{border-left:2px solid var(--azul);padding:.2rem 0 .2rem 1.8rem;margin:0 0 1rem;
  max-width:64ch}
.guion .rotulillo{margin-top:0}
.guion > div{margin-top:1.2rem}
.guion b{display:block;font-family:var(--f-mono);font-size:.56rem;letter-spacing:.2em;
  text-transform:uppercase;font-weight:400;color:var(--muted)}
.guion p{margin:.5rem 0 0;font-size:.95rem;line-height:1.85;color:var(--ink-2)}
.guion .nota__q{color:var(--negro)}

/* ====================================================================
   LA IMAGEN
   No hay fotografías del centro, así que la imagen se dibuja: cinco
   piezas de SVG definidas una sola vez en la página, recortadas por un
   sitio distinto en cada banda y coloreadas desde aquí. En noche la
   tinta es blanca sobre negro; en día, negra sobre blanco.
   ==================================================================== */
:root{--arte-a:var(--azul)}
.artes{position:absolute;width:0;height:0;overflow:hidden}
/* «a sangre»: la banda se sale de la columna de lectura hasta el borde de la
   pantalla. El recorte de body evita que la barra de desplazamiento cuente dos
   veces; es clip y no hidden porque hidden rompería lo que se queda pegado
   arriba al bajar. */
body{overflow-x:clip}
.portada,.frente,.banda--noche,.banda--pie{margin-inline:calc(50% - 50vw)}
.arte{display:block;width:100%;height:100%}

/* la portada: a pantalla, como se abre una web y no un documento */
.portada{position:relative;text-align:left;min-height:min(72vh,44rem);display:flex;
  flex-direction:column;justify-content:center;
  padding:var(--aire) var(--marco);
  background:var(--blanco);color:var(--negro);overflow:hidden;isolation:isolate;
  margin-top:0}
.portada__k{margin:0}
.portada__l{margin-left:0;margin-right:0;font-weight:300}
.portada__b{justify-content:flex-start}
.portada__pie{margin-top:0}

.portada__i{position:absolute;inset:0;z-index:-2;color:var(--negro)}
.portada__i .arte{transform:scale(1.06);transition:transform 1.2s var(--e)}
.portada::after{content:"";position:absolute;inset:0;z-index:-1;
  background:linear-gradient(105deg,rgba(255,255,255,.96) 0 34%,rgba(255,255,255,.66) 64%,
    rgba(255,255,255,.34) 100%)}
.portada__c{position:relative;max-width:46rem}
.portada__k{color:var(--muted)}
.portada h1{margin:2.2rem 0 0;font-size:clamp(2.4rem,6.4vw,5.2rem);font-weight:200;line-height:.94;
  letter-spacing:-.045em;color:var(--negro)}
.portada h1 em{font-style:normal;color:var(--azul)}
.portada__l{margin:2.4rem 0 0;max-width:34ch;font-size:clamp(1rem,1.6vw,1.24rem);
  line-height:1.75;color:var(--ink-2)}
.portada__b{margin-top:3.2rem;display:flex;flex-wrap:wrap;gap:1rem}
.portada__pie{position:absolute;left:var(--marco);bottom:2.2rem;color:var(--muted)}
.portada__baja{display:none}
@keyframes baja{0%{transform:translateY(-100%)}60%,100%{transform:translateY(100%)}}
@media(prefers-reduced-motion:reduce){.portada__baja i{animation:none}}

/* la cabecera de cada sección: la misma banda, en día o en noche */
.frente{position:relative;display:flex;align-items:flex-end;overflow:hidden;isolation:isolate;
  min-height:min(60vh,36rem);padding:calc(var(--nav) + 5rem) var(--marco) 3.6rem;
  margin-top:var(--saca);margin-bottom:var(--aire)}
.frente__i{position:absolute;inset:0;z-index:-2}
.frente::after{content:"";position:absolute;inset:0;z-index:-1}
.frente--dia{background:var(--blanco);color:var(--negro)}
.frente--dia .frente__i{color:var(--negro)}
.frente--dia::after{background:linear-gradient(180deg,rgba(255,255,255,.96) 0,
    rgba(255,255,255,0) 22%),
  linear-gradient(100deg,rgba(255,255,255,.95) 0 32%,rgba(255,255,255,.62) 66%,
  rgba(255,255,255,.30) 100%)}
.frente__c{position:relative;max-width:44rem}
.frente__n{display:block;font-family:var(--f-mono);font-size:.7rem;letter-spacing:.3em;
  opacity:.45;margin-bottom:1.4rem}
.frente__k{opacity:.7}
.frente h1{margin:1.4rem 0 0;font-size:clamp(1.9rem,4.6vw,3.7rem);font-weight:200;
  line-height:1.06;letter-spacing:-.036em}
.frente__p{margin:1.8rem 0 0;max-width:56ch;font-size:1rem;line-height:1.85;opacity:.82}

/* una banda de la portada puede llevar imagen debajo */
.banda--noche{position:relative;background:var(--gris);overflow:hidden;
  isolation:isolate;padding:var(--aire) var(--marco)}
.banda__i{position:absolute;inset:0;z-index:-2;color:var(--negro);opacity:.14}
.banda--noche::after{content:"";position:absolute;inset:0;z-index:-1;
  background:linear-gradient(180deg,var(--gris) 0,rgba(250,250,251,.6) 40%,var(--gris) 100%)}
.banda--pie{position:relative;overflow:hidden;isolation:isolate;padding:var(--aire) var(--marco) calc(var(--aire) * .7)}
.banda--pie .banda__i{opacity:.22;color:var(--negro)}

/* el retrato de cada puesto */
.arte--cara{border-radius:50%}
.puestobt{display:flex;align-items:center;gap:.9rem}
.puestobt__c{flex:none;width:2.2rem;height:2.2rem;color:var(--ink-2);opacity:.85;
  transition:color .24s var(--e),opacity .24s var(--e)}
.puestobt:hover .puestobt__c{opacity:1;color:var(--negro)}
.puestobt.es-on .puestobt__c{color:var(--azul);opacity:1}
.puestobt__t{min-width:0}
.puesto__cab{display:flex;align-items:flex-start;gap:2.2rem;flex-wrap:wrap}
.puesto__cara{flex:none;width:clamp(5rem,9vw,7.6rem);height:clamp(5rem,9vw,7.6rem);
  color:var(--negro)}
.puesto__cab > div:last-child{flex:1;min-width:16rem}

/* la tarjeta de un recorrido, con su trozo de dibujo */
.rutacard__i{display:block;height:7.5rem;margin-bottom:1.3rem;color:var(--ink-2);
  background:var(--gris);opacity:.62;transition:opacity .3s var(--e)}
.rutacard:hover .rutacard__i{opacity:1;color:var(--azul)}

/* que aparezcan al llegar, no de golpe */
[data-frente]{--sube:1}
.sitio--vivo [data-frente]:not(.es-ve) .frente__c,
.sitio--vivo [data-frente]:not(.es-ve) .portada__c,
.sitio--vivo [data-frente]:not(.es-ve) .banda__c{opacity:0;transform:translateY(14px)}
.frente__c,.portada__c,.banda__c{transition:opacity .7s var(--e),transform .7s var(--e)}
@media(prefers-reduced-motion:reduce){
  .frente__c,.portada__c,.banda__c{transition:none}
  .sitio--vivo [data-frente]:not(.es-ve) .frente__c,
  .sitio--vivo [data-frente]:not(.es-ve) .portada__c,
  .sitio--vivo [data-frente]:not(.es-ve) .banda__c{opacity:1;transform:none}
}

/* ====================================================================
   LA RUEDA
   Una sola pantalla, blanca, y el sistema entero alrededor. El centro
   dice dónde está uno; cada círculo, adónde lleva. Nada más.
   ==================================================================== */
.ruedero{min-height:calc(100svh - var(--nav));display:grid;place-items:center;
  align-content:center;margin-top:var(--saca);padding:calc(var(--nav) + 2rem) 0 2.4rem}
.rueda{position:relative;width:min(64vmin,41rem);aspect-ratio:1;margin:0 auto;
  isolation:isolate}
.rueda__l{position:absolute;inset:0;width:100%;height:100%;overflow:visible}
.rueda__o{fill:none;stroke:var(--linea);stroke-width:1}
.rueda__r line{stroke:var(--linea);stroke-width:1;
  transition:stroke .3s var(--e),stroke-width .3s var(--e)}
.rueda__r line.es-ve{stroke:var(--azul);stroke-width:1.6}

.rueda__c{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);
  width:28%;aspect-ratio:1;border-radius:50%;border:1px solid var(--negro);
  background:var(--blanco);display:flex;flex-direction:column;align-items:center;
  justify-content:center;text-align:center;padding:1.2rem;z-index:2}
.rueda__k{font-size:.46rem;letter-spacing:.22em;color:var(--muted);line-height:1.8}
.rueda__m{margin:1rem 0 0;font-size:clamp(1rem,2.4vmin,1.55rem);font-weight:300;
  line-height:1.14;letter-spacing:-.03em;color:var(--negro)}
.rueda__m em{display:block;font-style:normal;color:var(--azul)}
.rueda__h{margin:1rem 0 0;font-size:.46rem;letter-spacing:.28em;color:var(--muted)}
.rueda__q{margin:2.2rem auto 0;max-width:56ch;text-align:center;font-size:.94rem;
  line-height:1.8;color:var(--ink-2);min-height:5.4em;
  transition:color .3s var(--e)}
.rueda__q b{font-weight:400;color:var(--negro)}

.orbe{position:absolute;transform:translate(-50%,-50%);width:17.4%;aspect-ratio:1;
  border-radius:50%;border:1px solid var(--linea);background:var(--blanco);
  display:flex;flex-direction:column;align-items:center;justify-content:center;
  gap:.35rem;padding:.6rem;text-align:center;font:inherit;cursor:pointer;z-index:2;
  transition:border-color .3s var(--e),transform .35s var(--e),box-shadow .35s var(--e)}
.orbe__n{font-size:.44rem;letter-spacing:.2em;color:var(--muted)}
.orbe__r{font-size:clamp(.62rem,1.34vmin,.88rem);font-weight:400;line-height:1.2;
  color:var(--negro);letter-spacing:-.01em}
.orbe__m{font-size:.42rem;letter-spacing:.16em;color:var(--muted)}
.orbe:hover,.orbe:focus-visible,.orbe.es-ve{border-color:var(--azul);
  transform:translate(-50%,-50%) scale(1.07);
  box-shadow:0 1px 2px rgba(17,17,18,.04),0 14px 30px -18px rgba(17,17,18,.35)}
.orbe:hover .orbe__r,.orbe:focus-visible .orbe__r,.orbe.es-ve .orbe__r{color:var(--azul)}
.orbe:focus-visible{outline:none}
.rueda__pie{text-align:center;margin:2.6rem 0 0;color:var(--muted)}
.ruedero + .portada{margin-top:0;border-top:1px solid var(--linea-2)}

@media(max-width:820px){
  /* En una pantalla estrecha una rueda de diez es ilegible: los mismos diez
     círculos, en dos columnas, y el centro arriba. */
  .rueda{width:100%;aspect-ratio:auto;display:grid;
    grid-template-columns:repeat(2,minmax(0,1fr));gap:.9rem}
  .rueda__l{display:none}
  .rueda__c{position:static;transform:none;width:auto;aspect-ratio:auto;
    border-radius:1.6rem;grid-column:1/-1;padding:2.4rem 1.6rem;margin-bottom:.6rem}
  .rueda__k{font-size:.5rem;max-width:none}
  .rueda__m{font-size:1.7rem}
  .rueda__q{font-size:.82rem;max-width:34ch;min-height:0}
  .orbe{position:static;transform:none;width:auto;aspect-ratio:1;padding:1rem}
  .orbe:hover,.orbe:focus-visible{transform:scale(1.02)}
  .orbe__n,.orbe__m{font-size:.5rem}
  .orbe__r{font-size:.86rem}
}

/* qué es esto, para quién y qué se hace: tres líneas antes de entrar */
.lienzo--que{margin-top:calc(var(--aire) * -.35)}
.que{display:grid;grid-template-columns:repeat(auto-fit,minmax(15rem,1fr));gap:0 3.4rem;
  border-top:1px solid var(--negro);padding-top:1.8rem}
.que__c p:last-child{margin:.2rem 0 0;font-size:.95rem;line-height:1.85;color:var(--ink-2);
  max-width:42ch}
.que__p{margin-top:3rem;padding-top:1.6rem;border-top:1px solid var(--linea-2);
  display:flex;flex-wrap:wrap;align-items:flex-start;gap:1.4rem 3.4rem}
.que__p > .letra{flex:none;width:11rem;color:var(--muted);margin:.3rem 0 0}
.que__x{flex:1;min-width:20rem;max-width:64ch;margin:0;font-size:.95rem;line-height:1.85;
  color:var(--ink-2)}
.que__x b{font-weight:400;color:var(--negro)}
.enlacillo{font:inherit;font-size:inherit;color:var(--azul);background:none;border:0;
  padding:0;cursor:pointer;border-bottom:1px solid var(--azul-p)}
.enlacillo:hover{border-color:var(--azul)}
.bt--fino{flex:none;padding:.8rem 1.4rem;font-size:.58rem}
.sitio--vivo .sec.es-seguido .hojas{display:block}
.sec.es-seguido .hoja{border-top:1px solid var(--linea-2);padding-top:2.6rem;
  margin-top:3.4rem}

@media(max-width:900px){
  /* En el teléfono la barra se parte en dos o tres filas y su alto deja de ser
     un número: por eso aquí las bandas no se meten debajo de ella ni calculan
     nada con «auto», que invalidaría la regla entera. */
  :root{--nav:auto;--aire:clamp(3.2rem,9vw,5rem);--saca:-2.6rem}
  .portada{min-height:auto;padding:4.5rem 1.6rem 3.5rem}
  .portada__pie{position:static;margin-top:3rem}
  .portada__baja{display:none}
  .frente{min-height:auto;padding:3.6rem 1.6rem 2.6rem;margin-bottom:calc(var(--aire) * .8)}
  .frente h1{font-size:clamp(1.7rem,7vw,2.3rem)}
  .banda--noche,.banda--pie{padding-left:1.6rem;padding-right:1.6rem}
  .nav__f{flex-wrap:wrap;height:auto;padding:.8rem 1.1rem;gap:.6rem 1rem}
  .nav__m{flex:1 1 auto}
  .nav__l{order:3;flex:1 0 100%;min-width:100%;height:2.6rem;justify-content:flex-start}
  .abrepal span{display:none}
  .sub{columns:1;padding:1.6rem 1.1rem 2rem}
  .sec{padding:2.6rem 1.1rem 4rem}
  .cab__n{font-size:5rem;top:-1rem}
  .reloj__barra{height:auto;flex-direction:column}
  .reloj__t{width:100%!important;flex-direction:row;gap:.9rem;align-items:center;
    border-right:0;border-bottom:1px solid var(--linea-2)}
  .reloj__r{-webkit-line-clamp:1;flex:1}
  .reloj__eje{display:none}
  .carril{grid-template-columns:5rem minmax(0,1fr);gap:.7rem}
  .wraci{grid-template-columns:repeat(7,minmax(0,1fr))}
  .lienzo--indice .idx{columns:1}
  .puestosel{flex-wrap:nowrap;overflow-x:auto;scrollbar-width:none}
  .puestosel::-webkit-scrollbar{display:none}
  .puestobt{flex:0 0 auto;min-width:8.5rem}
  .grupod__cab{grid-template-columns:minmax(0,1fr)}
  .grupod__t{justify-self:start}
  .desp__b{gap:1rem;padding:1.2rem .2rem}
  .desp__n{min-width:2.6rem}
  .fasep{flex-wrap:wrap}
  .fasep__p{width:100%;padding-left:1.7rem}
  #sitio .dia .slide{padding:1.4rem 1.2rem}
  .lector__cab{padding:.8rem 1.1rem;height:auto;flex-wrap:wrap}
  .lector__in,.lector__pie{padding-left:1.1rem;padding-right:1.1rem}
  .velo{padding:5vh .8rem .8rem}
  .mapa14{overflow-x:auto}
  .mapa14 svg{min-width:44rem}
  .nodos{grid-template-columns:repeat(2,minmax(0,1fr))}
  .nodo{min-height:7rem;padding:1.2rem 1rem 1.3rem}
}
@media print{
  .nav,.paneles,.velo,.voz,.avance,.pito,.lector{display:none}
  .sitio--vivo .sec,.sitio--vivo .hojas{display:block}
}

/* ====================================================================
   REJILLAS SIN HUECOS GRISES
   Varias rejillas dibujaban sus líneas dejando ver el fondo por una
   separación de un píxel. Cuando la última fila no se llena, ese fondo
   se ve como un bloque gris vacío. Aquí la línea la lleva cada celda,
   así que donde no hay celda no hay nada: blanco.
   ==================================================================== */
#sitio .cards, #sitio .cinco, #sitio .entradas, #sitio .estados, #sitio .kpis,
#sitio .mini, #sitio .nodos, #sitio .puertas, #sitio .quees, #sitio .saydont,
#sitio .special, #sitio .specs, #sitio .wmapa,
#lector .cards, #lector .cinco, #lector .entradas, #lector .estados, #lector .kpis,
#lector .mini, #lector .quees, #lector .saydont, #lector .special, #lector .specs{
  background:none;gap:0}
#sitio .cards > *, #sitio .cinco > *, #sitio .entradas > *, #sitio .estados > *,
#sitio .kpis > *, #sitio .mini > *, #sitio .nodos > *, #sitio .puertas > *,
#sitio .quees > *, #sitio .saydont > *, #sitio .special > *, #sitio .specs > *,
#sitio .wmapa > *,
#lector .cards > *, #lector .cinco > *, #lector .entradas > *, #lector .estados > *,
#lector .kpis > *, #lector .mini > *, #lector .quees > *, #lector .saydont > *,
#lector .special > *, #lector .specs > *{
  box-shadow:0 0 0 1px var(--linea)}

/* ====================================================================
   UNA SOLA PALETA
   Los documentos vienen con la suya —verdes, ámbares, rojos—. Aquí
   dentro mandan el negro, el gris, el blanco y el azul: lo importante
   se ve azul, lo que avisa se ve negro, y lo demás es escala de gris.
   No se toca una letra: solo el color con que se dibuja.
   Va con «html:root» para ganar a los «:root» que traen los documentos,
   estén antes o después en la hoja.
   ==================================================================== */
html:root{
  --paper:#FAFAFB; --surface:#FFFFFF; --surface-2:#F1F1F3;
  --tinta:#111112; --ink:#1A1A1D; --ink-2:#55555E; --muted:#8E8E97;
  --line:#E6E6E9; --line-soft:#F1F1F3; --rule:#D9D9DE;
  --accent:#1F45FF; --accent-ink:#0A2ED6; --accent-fuerte:#0A2ED6;
  --accent-soft:rgba(31,69,255,.07);
  --acido:#EDF0FF; --acido-ink:#0A2ED6;
  --signal:#55555E; --signal-soft:rgba(17,17,18,.06);
  --alerta:#111112; --alerta-soft:rgba(17,17,18,.07);
  --sem-verde:#1F45FF; --sem-amarillo:#8E8E97;
  --sem-naranja:#55555E; --sem-rojo:#111112;
  --rol-direccion:#111112; --rol-doctor:#1F45FF; --rol-rac:#3A3A42;
  --rol-recepcion:#55555E; --rol-higienista:#7A7A84; --rol-auxiliar:#9A9AA2;
  --sombra-1:0 1px 2px rgba(17,17,18,.05);
  --sombra-2:0 1px 3px rgba(17,17,18,.06), 0 10px 24px -18px rgba(17,17,18,.30);
  --sombra-3:0 2px 6px rgba(17,17,18,.07), 0 20px 40px -24px rgba(17,17,18,.30);
}
"""


JS = """
<script>
(function(){
  "use strict";
  var D = document;
  var sitio = D.getElementById("sitio");
  if(!sitio) return;

  var secs   = [].slice.call(D.querySelectorAll(".sec"));
  var hojas  = [].slice.call(D.querySelectorAll(".hoja"));
  var orden  = window.__ORDEN__ || [];
  var VOCES  = window.__VOCES__ || {};
  var GRUPO  = window.__GRUPOESTADO__ || {};
  var RUTAS  = window.__RUTAS__ || {};
  var FASES  = window.__FASES__ || [];
  var paneles= D.getElementById("paneles");
  var avance = D.getElementById("avance");
  if(!secs.length) return;

  sitio.classList.add("sitio--vivo");

  var porHoja = {};
  hojas.forEach(function(h){ porHoja[h.dataset.hoja] = h; });

  var LLAVE = "giraldo.web.v9";
  var memo = {sec:"inicio", ruta:"", paso:0};
  try { var g = localStorage.getItem(LLAVE); if(g) memo = JSON.parse(g) || memo; } catch(e){}
  function recuerda(){ try { localStorage.setItem(LLAVE, JSON.stringify(memo)); } catch(e){} }
  function esc(s){ return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;"); }
  function rotulo(clave){
    for(var i=0;i<orden.length;i++){ if(orden[i][0] === clave) return orden[i][3]; }
    return "";
  }
  function seccionDe(clave){
    for(var i=0;i<orden.length;i++){ if(orden[i][0] === clave) return orden[i][4]; }
    return "";
  }
  function docDe(clave){
    for(var i=0;i<orden.length;i++){ if(orden[i][0] === clave) return orden[i][1]; }
    return "";
  }

  /* ---------------------------------------------------------------- */
  /*  Ir a una sección                                                  */
  /* ---------------------------------------------------------------- */
  function veSec(id, arriba){
    var s = secs.filter(function(x){ return x.dataset.sec === id; })[0] || secs[0];
    secs.forEach(function(x){ x.classList.toggle("es-on", x === s); });
    [].slice.call(D.querySelectorAll(".nav__l button")).forEach(function(b){
      b.classList.toggle("es-on", b.dataset.irSec === s.dataset.sec);
    });
    memo.sec = s.dataset.sec; recuerda();
    if(arriba !== false) window.scrollTo(0, 0);
    return s;
  }

  /* ================================================================ */
  /*  EL LECTOR: se abre encima, se lee, se vuelve                     */
  /* ================================================================ */
  var lector = D.getElementById("lector");
  var lecCuerpo = D.getElementById("leccuerpo");
  var lecQ = D.getElementById("lecq");
  var lecPaso = D.getElementById("lecpaso");
  var lecBarra = D.getElementById("lecbarra");
  var lecAnt = D.getElementById("lecant");
  var lecSig = D.getElementById("lecsig");
  var lecVolver = D.getElementById("lecvolver");
  var viaje = null;      // {claves:[], i:0, nombre:""}
  var scrollAntes = 0;

  function claveDeParada(ruta, n){
    var r = RUTAS[ruta];
    return r && r.paradas[n] ? r.paradas[n] : null;
  }

  function abreLector(clave, ruta, paso){
    var h = porHoja[clave];
    if(!h) return false;
    scrollAntes = window.scrollY;

    if(ruta && RUTAS[ruta]){
      viaje = {claves: RUTAS[ruta].paradas, i: paso || 0, nombre: RUTAS[ruta].quien, ruta: ruta};
      memo.ruta = ruta; memo.paso = viaje.i; recuerda();
    } else if(FASES.indexOf(clave) > -1){
      viaje = {claves: FASES, i: FASES.indexOf(clave), nombre: "Las catorce fases", ruta: ""};
    } else {
      viaje = null;
    }

    pintaLector(clave);
    lector.hidden = false;
    D.documentElement.style.overflow = "hidden";
    lecCuerpo.scrollTop = 0;
    if(lecVolver) lecVolver.focus();
    return true;
  }

  function pintaLector(clave){
    var h = porHoja[clave];
    if(!h) return;
    var copia = h.cloneNode(true);
    /* Se quitan los identificadores de la copia: el original sigue en su
       sección y no puede haber dos elementos con el mismo nombre. */
    copia.removeAttribute("id");
    [].slice.call(copia.querySelectorAll("[id]")).forEach(function(e){
      e.dataset.era = e.id; e.removeAttribute("id");
    });
    lecCuerpo.innerHTML = "";
    var caja = D.createElement("div");
    caja.className = "lector__in";
    caja.appendChild(copia);
    lecCuerpo.appendChild(caja);

    lecQ.textContent = docDe(clave) + " · " + rotulo(clave);
    if(viaje){
      lecPaso.textContent = viaje.nombre + " · " + (viaje.i + 1) + " / " + viaje.claves.length;
      lecBarra.style.width = (100 * (viaje.i + 1) / viaje.claves.length) + "%";
      lecAnt.disabled = viaje.i <= 0;
      lecSig.disabled = viaje.i >= viaje.claves.length - 1;
    } else {
      lecPaso.textContent = "";
      lecBarra.style.width = "0";
      lecAnt.disabled = true; lecSig.disabled = true;
    }

    var pie = D.createElement("div");
    pie.className = "lector__pie";
    if(viaje && viaje.i < viaje.claves.length - 1){
      var sigClave = viaje.claves[viaje.i + 1];
      pie.innerHTML = '<button type="button" class="lector__sig" data-lec-sig>'
        + '<span class="letra">Siguiente parada</span><b>' + esc(rotulo(sigClave)) + "</b></button>"
        + '<button type="button" class="bt" data-lec-cierra>Volver</button>';
    } else {
      pie.innerHTML = '<span class="letra">' + (viaje ? "Final del recorrido" : "Fin del apartado")
        + "</span>" + '<button type="button" class="bt bt--fuerte" data-lec-cierra>Volver</button>';
    }
    lecCuerpo.appendChild(pie);
    try { history.replaceState(null, "", "#" + clave); } catch(e){}
  }

  function mueveLector(paso){
    if(!viaje) return;
    var j = viaje.i + paso;
    if(j < 0 || j >= viaje.claves.length) return;
    viaje.i = j;
    if(viaje.ruta){ memo.paso = j; recuerda(); }
    pintaLector(viaje.claves[j]);
    lecCuerpo.scrollTop = 0;
  }

  function cierraLector(){
    if(!lector || lector.hidden) return false;
    lector.hidden = true;
    D.documentElement.style.overflow = "";
    lecCuerpo.innerHTML = "";
    viaje = null;
    window.scrollTo(0, scrollAntes);
    return true;
  }

  if(lecAnt) lecAnt.addEventListener("click", function(){ mueveLector(-1); });
  if(lecSig) lecSig.addEventListener("click", function(){ mueveLector(1); });
  if(lecVolver) lecVolver.addEventListener("click", cierraLector);
  if(lecCuerpo) lecCuerpo.addEventListener("click", function(e){
    if(e.target.closest("[data-lec-sig]")){ mueveLector(1); return; }
    if(e.target.closest("[data-lec-cierra]")){ cierraLector(); return; }
  });

  /* ---------------------------------------------------------------- */
  /*  Todo lo que se pulsa                                              */
  /* ---------------------------------------------------------------- */
  function abreDestino(id, ruta, paso){
    if(porHoja[id]) return abreLector(id, ruta, paso);
    var el = D.getElementById(id);
    if(!el) return false;
    var dueno = el.closest(".hoja");
    if(dueno) return abreLector(dueno.dataset.hoja, ruta, paso);
    var sec = el.closest(".sec");
    if(sec){
      cierraLector(); veSec(sec.dataset.sec, false);
      /* si lo que se busca está dentro de un puesto que no es el que se ve, o
         dentro de un desplegable cerrado, se abre antes de ir: nadie tiene que
         adivinar dónde estaba */
      var ficha = el.closest(".puesto");
      if(ficha && ficha.hidden) vePuesto(ficha.dataset.puesto);
      var caja = el.closest(".desp"), movio = false;
      while(caja){
        movio = abreDesp(caja) || movio;
        var g = caja.closest(".grupod");
        if(g) cuentaGrupo(g);
        caja = caja.parentElement && caja.parentElement.closest(".desp");
      }
      var ve = function(){ el.scrollIntoView({block:"start", behavior:"smooth"}); };
      if(movio) setTimeout(ve, 380); else ve();
      return true;
    }
    return false;
  }

  D.addEventListener("click", function(e){
    var b;
    if((b = e.target.closest("[data-lee]"))){
      e.preventDefault();
      abreLector(b.dataset.lee, b.dataset.ruta || "", parseInt(b.dataset.paso || "0", 10));
      return;
    }
    if((b = e.target.closest("[data-empieza]"))){
      e.preventDefault();
      var r = RUTAS[b.dataset.empieza];
      if(r && r.paradas.length) abreLector(r.paradas[0], b.dataset.empieza, 0);
      return;
    }
    if((b = e.target.closest("[data-ve-ruta]"))){
      e.preventDefault(); cierraPanel(); veSec("recorridos", false);
      var d = D.getElementById("ruta-" + b.dataset.veRuta);
      if(d) d.scrollIntoView({block:"start", behavior:"smooth"});
      return;
    }
    if((b = e.target.closest("[data-abre-fase]"))){
      e.preventDefault();
      if(b.dataset.abreFase) abreDestino(b.dataset.abreFase);
      return;
    }
    var nb = e.target.closest(".nav__l button[data-ir-sec]");
    if(nb){
      var abierto = !paneles.hidden && nb.classList.contains("es-abierto");
      cierraLector(); veSec(nb.dataset.irSec, true);
      if(abierto) cierraPanel(); else abrePanel(nb.dataset.irSec);
      return;
    }
    if((b = e.target.closest("[data-ir-sec]"))){
      e.preventDefault(); cierraPanel(); cierraLector(); veSec(b.dataset.irSec, true);
      return;
    }
    var a = e.target.closest("a[data-ir], a[href^='#']");
    if(a){
      var clave = a.dataset.ir || a.getAttribute("href").slice(1);
      if(D.getElementById(clave) || porHoja[clave]){
        e.preventDefault(); cierraPanel();
        abreDestino(clave);
      }
      return;
    }
    if(!e.target.closest(".nav")) cierraPanel();
  });

  /* el mapa también se recorre con el teclado */
  D.addEventListener("keydown", function(e){
    if(e.key !== "Enter" && e.key !== " ") return;
    var n = e.target.closest("[data-abre-fase]");
    if(!n) return;
    e.preventDefault();
    if(n.dataset.abreFase) abreDestino(n.dataset.abreFase);
  });

  /* ---------------------------------------------------------------- */
  /*  El índice desplegable                                             */
  /* ---------------------------------------------------------------- */
  function abrePanel(id){
    var hay = false;
    [].slice.call(D.querySelectorAll(".sub")).forEach(function(p){
      var si = p.dataset.sub === id;
      p.hidden = !si;
      if(si) hay = true;
    });
    paneles.hidden = !hay;
    [].slice.call(D.querySelectorAll(".nav__l button")).forEach(function(b){
      b.classList.toggle("es-abierto", hay && b.dataset.irSec === id);
    });
  }
  function cierraPanel(){
    if(paneles) paneles.hidden = true;
    [].slice.call(D.querySelectorAll(".nav__l button")).forEach(function(b){
      b.classList.remove("es-abierto");
    });
  }

  /* ---------------------------------------------------------------- */
  /*  Puestos y marketing                                               */
  /* ---------------------------------------------------------------- */
  function vePuesto(id){
    [].slice.call(D.querySelectorAll(".puestobt")).forEach(function(x){
      x.classList.toggle("es-on", x.dataset.puesto === id);
    });
    [].slice.call(D.querySelectorAll(".puesto")).forEach(function(p){
      p.hidden = p.dataset.puesto !== id;
    });
  }

  D.addEventListener("click", function(e){
    var b = e.target.closest(".puestobt");
    if(!b) return;
    vePuesto(b.dataset.puesto);
    var sel = b.closest(".puestosel");
    if(sel && sel.getBoundingClientRect().top < 0)
      sel.scrollIntoView({block:"start", behavior:"smooth"});
  });

  var tabla = D.getElementById("tablaacciones");
  var cuentaAcc = D.getElementById("cuentaacc");
  function filtra(){
    if(!tabla) return;
    var f = {};
    [].slice.call(D.querySelectorAll("[data-filtro]")).forEach(function(s){
      if(s.value) f[s.dataset.filtro] = s.value;
    });
    var filas = [].slice.call(tabla.querySelectorAll("tbody tr")), vivas = 0;
    filas.forEach(function(tr){
      var ok = Object.keys(f).every(function(k){ return tr.dataset[k] === f[k]; });
      tr.hidden = !ok;
      if(ok) vivas++;
    });
    if(cuentaAcc) cuentaAcc.textContent = vivas === filas.length
      ? (filas.length + " acciones") : (vivas + " de " + filas.length);
  }
  function apagaEstados(){
    [].slice.call(D.querySelectorAll(".estado")).forEach(function(b){ b.classList.remove("es-on"); });
  }
  [].slice.call(D.querySelectorAll("[data-filtro]")).forEach(function(s){
    s.addEventListener("change", function(){ filtra(); apagaEstados(); });
  });
  var limpia = D.getElementById("limpiafiltros");
  if(limpia) limpia.addEventListener("click", function(){
    [].slice.call(D.querySelectorAll("[data-filtro]")).forEach(function(s){ s.value = ""; });
    filtra(); apagaEstados();
  });
  D.addEventListener("click", function(e){
    var b = e.target.closest(".estado");
    if(!b) return;
    var sel = D.querySelector('[data-filtro="grupo"]');
    var g = GRUPO[b.dataset.estado];
    if(!sel || !g) return;
    var ya = b.classList.contains("es-on");
    apagaEstados();
    sel.value = ya ? "" : g;
    if(!ya) b.classList.add("es-on");
    filtra();
    if(!ya && tabla) tabla.closest(".lienzo").scrollIntoView({block:"start", behavior:"smooth"});
  });
  filtra();

  /* ---------------------------------------------------------------- */
  /*  Lo que flota: paleta, recursos, teclas, glosario, lupa            */
  /* ---------------------------------------------------------------- */
  var velos = {}, ultimoFoco = null;
  [].slice.call(D.querySelectorAll(".velo")).forEach(function(v){ velos[v.dataset.velo] = v; });
  function abre(cual){
    cierra(); cierraPanel();
    var v = velos[cual];
    if(!v) return;
    ultimoFoco = D.activeElement;
    v.hidden = false;
    D.documentElement.style.overflow = "hidden";
    var f = v.querySelector("input, button, a");
    if(f) f.focus();
    if(cual === "paleta") pinta_paleta("");
  }
  function cierra(){
    var abierto = false;
    Object.keys(velos).forEach(function(k){ if(!velos[k].hidden){ velos[k].hidden = true; abierto = true; } });
    tapaVoz();
    if(lector && lector.hidden) D.documentElement.style.overflow = "";
    if(abierto && ultimoFoco && ultimoFoco.focus) ultimoFoco.focus();
    return abierto;
  }
  Object.keys(velos).forEach(function(k){
    velos[k].addEventListener("click", function(e){
      if(e.target === velos[k] || e.target.closest("[data-cerrar]")) cierra();
    });
  });
  D.addEventListener("click", function(e){
    var b = e.target.closest("[data-abre]");
    if(b) abre(b.dataset.abre);
  });

  var campo = D.getElementById("palq"), lista = D.getElementById("pallista");
  var cache = null, elegido = 0;
  var CON = "\\u00e1\\u00e0\\u00e4\\u00e2\\u00e3\\u00e9\\u00e8\\u00eb\\u00ea\\u00ed\\u00ec\\u00ef\\u00ee"
          + "\\u00f3\\u00f2\\u00f6\\u00f4\\u00f5\\u00fa\\u00f9\\u00fc\\u00fb\\u00f1\\u00e7";
  var SIN = "aaaaaeeeeiiiiooooouuuunc";
  function llano(s){
    s = String(s).toLowerCase();
    var f = "";
    for(var i=0;i<s.length;i++){ var j = CON.indexOf(s[i]); f += j<0 ? s[i] : SIN[j]; }
    return f;
  }
  function indexa(){
    if(cache) return cache;
    cache = [];
    [].slice.call(D.querySelectorAll(".nav__l button")).forEach(function(b){
      cache.push({id:b.dataset.irSec, doc:"Sección", rot:b.textContent.trim(), seccion:true});
    });
    Object.keys(RUTAS).forEach(function(k){
      cache.push({id:"ruta:" + k, doc:"Recorrido", rot:RUTAS[k].quien + " · " + RUTAS[k].titulo,
                  ruta:true});
    });
    hojas.forEach(function(h){
      var crudo = (h.innerText || h.textContent || "").replace(/\\s+/g," ");
      cache.push({id:h.dataset.hoja, doc:docDe(h.dataset.hoja), rot:rotulo(h.dataset.hoja),
                  crudo:crudo, txt:llano(crudo), rotll:llano(rotulo(h.dataset.hoja))});
    });
    return cache;
  }
  function trozo(d, q){
    var i = d.txt.indexOf(q);
    if(i < 0) return "";
    var a = Math.max(0, i-60), b = Math.min(d.crudo.length, i+q.length+110);
    return (a?"…":"") + esc(d.crudo.slice(a,i)) + "<mark>" + esc(d.crudo.slice(i,i+q.length))
         + "</mark>" + esc(d.crudo.slice(i+q.length,b)) + (b<d.crudo.length?"…":"");
  }
  function fila(d, q){
    return '<button type="button" class="pal__i" data-va="' + esc(d.id) + '">'
         + "<span>" + (d.seccion ? "&#8594;" : d.ruta ? "&#9679;" : "&middot;") + "</span>"
         + "<b>" + esc(d.rot)
         + (q && !d.seccion && !d.ruta ? '<span class="pal__ctx">' + trozo(d,q) + "</span>" : "")
         + "</b><i>" + esc(d.doc) + "</i></button>";
  }
  function pinta_paleta(q){
    q = llano((q||"").trim());
    var datos = indexa();
    var ss = datos.filter(function(d){ return d.seccion; });
    var rr = datos.filter(function(d){ return d.ruta; });
    var aa = datos.filter(function(d){ return !d.seccion && !d.ruta; });
    if(!q){
      lista.innerHTML = '<p class="pal__g">Recorridos</p>' + rr.map(function(d){ return fila(d,""); }).join("")
        + '<p class="pal__g">Secciones</p>' + ss.map(function(d){ return fila(d,""); }).join("");
    } else {
      var s1 = ss.filter(function(d){ return llano(d.rot).indexOf(q) > -1; });
      var r1 = rr.filter(function(d){ return llano(d.rot).indexOf(q) > -1; });
      var t1 = aa.filter(function(d){ return d.rotll.indexOf(q) > -1; });
      var t2 = aa.filter(function(d){ return d.rotll.indexOf(q) < 0 && d.txt.indexOf(q) > -1; });
      function entera(d){
        var i = d.txt.indexOf(q);
        if(i < 0) return false;
        var a = i ? d.txt[i-1] : " ", b = i+q.length < d.txt.length ? d.txt[i+q.length] : " ";
        return !/[a-z0-9]/.test(a) && !/[a-z0-9]/.test(b);
      }
      t2.sort(function(m,n){ return (entera(n)?1:0) - (entera(m)?1:0); });
      if(!s1.length && !r1.length && !t1.length && !t2.length){
        lista.innerHTML = '<p class="pal__nada">Nada con «' + esc(q) + '» en el sistema.</p>';
      } else {
        lista.innerHTML =
          (r1.length ? '<p class="pal__g">Recorridos</p>' + r1.map(function(d){ return fila(d,""); }).join("") : "")
          + (s1.length ? '<p class="pal__g">Secciones</p>' + s1.map(function(d){ return fila(d,""); }).join("") : "")
          + (t1.length ? '<p class="pal__g">' + t1.length + ' en el rótulo</p>' + t1.map(function(d){ return fila(d,""); }).join("") : "")
          + (t2.length ? '<p class="pal__g">' + t2.length + ' en el texto</p>' + t2.map(function(d){ return fila(d,q); }).join("") : "");
      }
    }
    elegido = 0; marca();
  }
  function marca(){
    var todos = [].slice.call(lista.querySelectorAll(".pal__i"));
    todos.forEach(function(b,n){ b.classList.toggle("es-aqui", n === elegido); });
    if(todos[elegido]) todos[elegido].scrollIntoView({block:"nearest"});
  }
  if(campo){
    campo.addEventListener("input", function(){ pinta_paleta(campo.value); });
    campo.addEventListener("keydown", function(e){
      var todos = [].slice.call(lista.querySelectorAll(".pal__i"));
      if(e.key === "ArrowDown"){ e.preventDefault(); elegido = Math.min(elegido+1, todos.length-1); marca(); }
      if(e.key === "ArrowUp"){ e.preventDefault(); elegido = Math.max(elegido-1, 0); marca(); }
      if(e.key === "Enter" && todos[elegido]){ e.preventDefault(); todos[elegido].click(); }
    });
  }
  if(lista) lista.addEventListener("click", function(e){
    var b = e.target.closest(".pal__i");
    if(!b) return;
    cierra(); campo.value = "";
    var v = b.dataset.va;
    if(v.indexOf("ruta:") === 0){
      var k = v.slice(5);
      veSec("recorridos", false);
      var d = D.getElementById("ruta-" + k);
      if(d) d.scrollIntoView({block:"start"});
      return;
    }
    if(porHoja[v]) abreLector(v, "", 0);
    else veSec(v, true);
  });

  var voz = D.getElementById("voz");
  function tapaVoz(){ if(voz) voz.hidden = true; }
  D.addEventListener("click", function(e){
    var b = e.target.closest("[data-gl]");
    if(!b){
      if(voz && !voz.hidden && !e.target.closest(".voz")) tapaVoz();
      return;
    }
    e.preventDefault();
    var d = VOCES[b.dataset.gl];
    if(!d || !voz) return;
    voz.innerHTML = "<b>" + esc(b.dataset.gl) + "</b><p>" + esc(d[0]) + "</p><small>" + esc(d[1]) + "</small>";
    voz.hidden = false;
    var r = b.getBoundingClientRect(), an = voz.offsetWidth, al = voz.offsetHeight;
    var x = Math.min(Math.max(8, r.left + window.scrollX), window.scrollX + window.innerWidth - an - 8);
    var y = r.bottom + window.scrollY + 8;
    if(r.bottom + al + 16 > window.innerHeight) y = r.top + window.scrollY - al - 8;
    voz.style.left = x + "px"; voz.style.top = Math.max(8, y) + "px";
  });

  var lienzoLupa = D.getElementById("lupalienzo");
  D.addEventListener("click", function(e){
    var f = e.target.closest("figure, .fig, .t-fig, .tablewrap, .tablawrap, .mapa14");
    if(!f || !lienzoLupa) return;
    if(e.target.closest("a, button, input, select, [data-abre-fase]")) return;
    lienzoLupa.innerHTML = "";
    lienzoLupa.appendChild(f.cloneNode(true));
    abre("lupa");
  });

  D.addEventListener("keydown", function(e){
    var t = e.target;
    var escribiendo = t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA"
                            || t.tagName === "SELECT" || t.isContentEditable);
    if(e.key === "Escape"){
      if(cierra()){ e.preventDefault(); return; }
      if(cierraLector()){ e.preventDefault(); return; }
      cierraPanel(); return;
    }
    if((e.metaKey || e.ctrlKey) && (e.key === "k" || e.key === "K")){ e.preventDefault(); abre("paleta"); return; }
    if(escribiendo || e.ctrlKey || e.metaKey || e.altKey) return;
    if(e.key === "/"){ e.preventDefault(); abre("paleta"); return; }
    if(e.key === "?"){ e.preventDefault(); abre("teclas"); return; }
    if(e.key === "r" || e.key === "R"){ e.preventDefault(); abre("recursos"); return; }
    if(lector && !lector.hidden){
      if(e.key === "ArrowRight") mueveLector(1);
      if(e.key === "ArrowLeft") mueveLector(-1);
      return;
    }
    if(e.key === "g"){ veSec("inicio", true); }
  });

  function dibujaAvance(){
    if(!avance) return;
    var alto = D.documentElement.scrollHeight - window.innerHeight;
    avance.style.width = alto > 0 ? (100 * window.scrollY / alto) + "%" : "0";
  }
  window.addEventListener("scroll", dibujaAvance, {passive:true});
  window.addEventListener("resize", dibujaAvance);

  window.addEventListener("hashchange", function(){
    var h = (location.hash || "").slice(1);
    if(!h) return;
    if(lector && !lector.hidden && porHoja[h]) return;
    abreDestino(h);
  });

  /* ---------------------------------------------------------------- */
  /*  Los desplegables                                                  */
  /*  Se cierran al arrancar —sin JavaScript quedan abiertos, que es    */
  /*  como se lee un documento— y se abren de uno en uno o de golpe.    */
  /* ---------------------------------------------------------------- */
  function pintaDesp(d, abierto){
    d.classList.toggle("es-ab", abierto);
    var b = d.querySelector(".desp__b");
    if(b) b.setAttribute("aria-expanded", abierto ? "true" : "false");
  }
  function abreDesp(d){
    if(!d || d.classList.contains("es-ab")) return false;
    pintaDesp(d, true);
    return true;
  }
  [].slice.call(D.querySelectorAll(".desp")).forEach(function(d){ pintaDesp(d, false); });

  function cuentaGrupo(g){
    var b = g.querySelector("[data-abre-todo]");
    if(!b) return;
    var dd = [].slice.call(g.querySelectorAll(".desp"));
    var abiertos = dd.filter(function(d){ return d.classList.contains("es-ab"); }).length;
    b.textContent = (abiertos === dd.length ? "Cerrar los " : "Abrir los ") + dd.length;
  }

  D.addEventListener("click", function(e){
    var t = e.target.closest("[data-abre-todo]");
    if(t){
      var g = t.closest(".grupod");
      var dd = [].slice.call(g.querySelectorAll(".desp"));
      var cerrar = dd.every(function(d){ return d.classList.contains("es-ab"); });
      dd.forEach(function(d){ pintaDesp(d, !cerrar); });
      cuentaGrupo(g);
      return;
    }
    var b = e.target.closest(".desp__b");
    if(!b) return;
    var d = b.closest(".desp");
    pintaDesp(d, !d.classList.contains("es-ab"));
    var g = d.closest(".grupod");
    if(g) cuentaGrupo(g);
    if(d.classList.contains("es-ab")){
      var arriba = d.getBoundingClientRect().top;
      if(arriba < 0) d.scrollIntoView({block:"start", behavior:"smooth"});
    }
  });

  /* ---------------------------------------------------------------- */
  /*  La presentación: las cuarenta y tres o las doce esenciales        */
  /* ---------------------------------------------------------------- */
  D.addEventListener("click", function(e){
    var b = e.target.closest("[data-pres]");
    if(!b) return;
    var solo = b.dataset.pres === "esencial";
    [].slice.call(D.querySelectorAll("[data-pres]")).forEach(function(x){
      x.classList.toggle("es-on", x === b);
    });
    [].slice.call(D.querySelectorAll(".desp[data-esencial]")).forEach(function(d){
      d.hidden = solo && d.dataset.esencial !== "1";
    });
    [].slice.call(D.querySelectorAll(".parte")).forEach(function(p){
      p.hidden = !p.querySelector(".desp:not([hidden])");
    });
  });

  /* ---------------------------------------------------------------- */
  /*  Las bandas de imagen                                              */
  /*  Aparecen al llegar a ellas, y el dibujo de la portada se mueve un  */
  /*  poco más despacio que la página. Nada de esto hace falta para      */
  /*  leer: si el navegador no lo trae, todo queda quieto y visible.     */
  /* ---------------------------------------------------------------- */
  var bandas = [].slice.call(D.querySelectorAll("[data-frente]"));
  if (window.IntersectionObserver) {
    var ojo = new IntersectionObserver(function(entradas){
      entradas.forEach(function(e){
        if (e.isIntersecting) { e.target.classList.add("es-ve"); ojo.unobserve(e.target); }
      });
    }, {rootMargin: "0px 0px -12% 0px"});
    bandas.forEach(function(b){ ojo.observe(b); });
  } else {
    bandas.forEach(function(b){ b.classList.add("es-ve"); });
  }

  var quieto = window.matchMedia("(prefers-reduced-motion: reduce)");
  var dibujo = D.querySelector(".portada__i .arte");
  if (dibujo && !quieto.matches) {
    var pendiente = false;
    window.addEventListener("scroll", function(){
      if (pendiente) return;
      pendiente = true;
      requestAnimationFrame(function(){
        pendiente = false;
        var y = Math.min(window.scrollY, 900);
        dibujo.style.transform = "scale(1.06) translateY(" + (y * 0.16) + "px)";
      });
    }, {passive: true});
  }

  /* ---------------------------------------------------------------- */
  /*  La rueda                                                          */
  /*  Al señalar un círculo se enciende su radio y debajo se lee qué    */
  /*  hay dentro. Al quitar el dedo vuelve la frase de siempre.         */
  /* ---------------------------------------------------------------- */
  var ruedaQ = D.getElementById("ruedaq");
  var ruedaDicho = ruedaQ ? ruedaQ.innerHTML : "";
  function pintaRueda(id, texto){
    [].slice.call(D.querySelectorAll(".rueda__r line")).forEach(function(l){
      l.classList.toggle("es-ve", l.dataset.radio === id);
    });
    [].slice.call(D.querySelectorAll(".orbe")).forEach(function(o){
      o.classList.toggle("es-ve", o.dataset.orbe === id);
    });
    if (ruedaQ) ruedaQ.innerHTML = texto || ruedaDicho;
  }
  [].slice.call(D.querySelectorAll(".orbe")).forEach(function(o){
    var dentro = function(){
      pintaRueda(o.dataset.orbe,
                 "<b>" + o.querySelector(".orbe__r").textContent + ".</b> " + o.dataset.que);
    };
    var fuera = function(){ pintaRueda("", ""); };
    o.addEventListener("mouseenter", dentro);
    o.addEventListener("focus", dentro);
    o.addEventListener("mouseleave", fuera);
    o.addEventListener("blur", fuera);
  });

  /* ---------------------------------------------------------------- */
  /*  Leerlo entero, seguido                                            */
  /*  Por defecto cada apartado se abre en el lector, que es como se     */
  /*  consulta. Pero un documento también se lee de la primera línea a   */
  /*  la última, y eso no puede depender de ir abriendo ciento treinta   */
  /*  y cinco veces: esto lo despliega entero, en orden, aquí mismo.     */
  /* ---------------------------------------------------------------- */
  D.addEventListener("click", function(e){
    var b = e.target.closest("[data-seguido]");
    if(!b) return;
    var sec = b.closest(".sec");
    if(!sec) return;
    var abierto = sec.classList.toggle("es-seguido");
    b.textContent = abierto ? "Volver al índice" : "Leerlo entero, seguido";
    if(abierto){
      var h = sec.querySelector(".hojas");
      if(h) setTimeout(function(){ h.scrollIntoView({block:"start", behavior:"smooth"}); }, 40);
    } else {
      b.scrollIntoView({block:"center", behavior:"smooth"});
    }
  });

  /* ---- arranque ---------------------------------------------------- */
  var h0 = (location.hash || "").slice(1);
  if(h0 && secs.some(function(s){ return s.dataset.sec === h0; })) veSec(h0, false);
  else { veSec(memo.sec || "inicio", false); if(h0) abreDestino(h0); }
  dibujaAvance();
})();
</script>
"""


MARCO = """
@@ARTES@@
<a class="saltar" href="#sitio">Saltar al contenido</a>
<div class="avance" id="avance" aria-hidden="true"></div>

<header class="nav">
  <div class="nav__f">
    <button class="nav__m" type="button" data-ir-sec="inicio">Giraldo <em>v@VERSION@</em></button>
    <nav class="nav__l" aria-label="Secciones">@@NAV@@</nav>
    <div class="nav__b">
      <button class="nav__ruta" type="button" data-ir-sec="recorridos">Recorridos</button>
      <button class="nav__ruta" type="button" data-ir-sec="mapa">Mapa</button>
      <span class="nav__sep"></span>
      <button class="abrepal" type="button" data-abre="paleta"><span>Buscar</span>
        <svg width="13" height="13" viewBox="0 0 16 16" aria-hidden="true">
          <circle cx="7" cy="7" r="4.4" fill="none" stroke="currentColor" stroke-width="1.4"/>
          <path d="M10.4 10.4 L14.2 14.2" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
        </svg></button>
      <button class="icono" type="button" data-abre="recursos" aria-label="Recursos" title="Recursos (R)">&#9781;</button>
      <button class="icono" type="button" data-abre="teclas" aria-label="Cómo se usa" title="Cómo se usa (?)">?</button>
    </div>
  </div>
  <div class="paneles" id="paneles" hidden>@@PANELES@@</div>
</header>

<div id="sitio">
@@SECCIONES@@
</div>

<!-- ------------------------------------------------------------------
     El lector. Cualquier apartado se abre aquí encima, se lee entero y se
     vuelve exactamente donde se estaba. Si viene de un recorrido, las
     flechas avanzan por sus paradas.
     ------------------------------------------------------------------ -->
<div class="lector" id="lector" role="dialog" aria-modal="true" aria-label="Lector" hidden>
  <div class="lector__cab">
    <button class="lector__volver" type="button" id="lecvolver">&#8592; Volver</button>
    <p class="lector__q" id="lecq"></p>
    <div class="lector__nav">
      <span class="lector__paso" id="lecpaso"></span>
      <button class="icono" type="button" id="lecant" aria-label="Parada anterior">&#8592;</button>
      <button class="icono" type="button" id="lecsig" aria-label="Parada siguiente">&#8594;</button>
    </div>
  </div>
  <div class="lector__barra"><i id="lecbarra"></i></div>
  <div class="lector__cuerpo" id="leccuerpo"></div>
</div>

<div class="velo" data-velo="paleta" role="dialog" aria-modal="true" aria-label="Buscar" hidden>
  <div class="flota">
    <div class="pal__campo">
      <svg width="15" height="15" viewBox="0 0 16 16" aria-hidden="true" style="color:var(--muted);flex:none">
        <circle cx="7" cy="7" r="4.4" fill="none" stroke="currentColor" stroke-width="1.4"/>
        <path d="M10.4 10.4 L14.2 14.2" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
      </svg>
      <input id="palq" type="search" autocomplete="off" spellcheck="false"
             placeholder="Recorridos, secciones, apartados y texto" aria-label="Buscar">
      <button class="icono" type="button" data-cerrar aria-label="Cerrar">&#10005;</button>
    </div>
    <div class="pal__lista" id="pallista"></div>
    <div class="flota__pie"><span><kbd>&#8593;</kbd><kbd>&#8595;</kbd> moverse</span>
      <span><kbd>&#8629;</kbd> abrir</span><span><kbd>Esc</kbd> cerrar</span></div>
  </div>
</div>

<div class="velo" data-velo="recursos" role="dialog" aria-modal="true" aria-label="Recursos" hidden>
  <div class="flota">
    <div class="flota__cab"><h2>Recursos</h2>
      <button class="icono" type="button" data-cerrar aria-label="Cerrar">&#10005;</button></div>
    <div class="flota__cuerpo">@@RECURSOS@@</div>
  </div>
</div>

<div class="velo" data-velo="teclas" role="dialog" aria-modal="true" aria-label="Cómo se usa" hidden>
  <div class="flota" style="width:min(31rem,100%)">
    <div class="flota__cab"><h2>Cómo se usa</h2>
      <button class="icono" type="button" data-cerrar aria-label="Cerrar">&#10005;</button></div>
    <div class="flota__cuerpo">
      <p style="margin:0 0 1.8rem;font-size:.95rem;line-height:1.85;color:var(--ink-2)">
        Hay dos maneras de entrar. Por <b>recorrido</b>: se elige quién es usted y el sitio le
        lleva parada a parada, con las flechas y una barra que dice cuánto queda. O por
        <b>sección</b>: el índice de arriba despliega los apartados de cada documento. En las dos,
        cualquier cosa se abre encima de lo que estaba haciendo y al volver sigue donde estaba.
      </p>
      <dl class="tec">
        <dt><kbd>&#8984;K</kbd> &middot; <kbd>/</kbd></dt><dd>Buscar recorridos, secciones y texto</dd>
        <dt><kbd>&#8594;</kbd> &middot; <kbd>&#8592;</kbd></dt><dd>Dentro del lector, parada siguiente y anterior</dd>
        <dt><kbd>G</kbd></dt><dd>Volver al inicio</dd>
        <dt><kbd>R</kbd></dt><dd>Recursos y descargas</dd>
        <dt><kbd>?</kbd></dt><dd>Esta ventana</dd>
        <dt><kbd>Esc</kbd></dt><dd>Volver / cerrar</dd>
      </dl>
      <p style="margin:1.8rem 0 0;font-size:.86rem;line-height:1.8;color:var(--muted)">
        Las siglas subrayadas —@EJEMPLO@— abren su definición, que es la que está escrita en el
        Manual. Las figuras, las tablas anchas y el mapa se ven de cerca pulsando encima.
      </p>
    </div>
  </div>
</div>

<div class="velo lupa" data-velo="lupa" role="dialog" aria-modal="true" aria-label="De cerca" hidden>
  <div class="flota">
    <div class="flota__cab"><h2>De cerca</h2>
      <button class="icono" type="button" data-cerrar aria-label="Cerrar">&#10005;</button></div>
    <div class="lupa__lienzo" id="lupalienzo"></div>
  </div>
</div>

<div class="voz" id="voz" role="tooltip" hidden></div>
<div class="pito" id="pito" role="status" hidden></div>
"""


COBALTO = (0x1F, 0x45, 0xFF)


def _luz(r, g, b):
    """Luminancia percibida, 0 negro y 1 blanco."""
    return (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255.0


def _tono(r, g, b):
    """El matiz en grados, para saber si el color tira a verde o a rojo."""
    mx, mn = max(r, g, b), min(r, g, b)
    if mx == mn:
        return 0.0
    d = float(mx - mn)
    if mx == r:
        h = ((g - b) / d) % 6
    elif mx == g:
        h = (b - r) / d + 2
    else:
        h = (r - g) / d + 4
    return h * 60.0


def _mezcla(color, luz):
    """El color llevado a esa luminancia: hacia el blanco o hacia el negro."""
    base = _luz(*color)
    if luz >= base:
        k = 0 if base >= 1 else (luz - base) / (1 - base)
        return tuple(int(round(c + (255 - c) * k)) for c in color)
    k = 0 if base <= 0 else (base - luz) / base
    return tuple(int(round(c * (1 - k))) for c in color)


def monocroma(css):
    """Una sola paleta.

    Los documentos traen su propia gama —verdes, ambares, rojos—. Aqui
    dentro mandan el negro, el gris, el blanco y el azul. Lo que en los
    documentos era el color de acento (los verdes y azulados) pasa a ser
    el azul; todo lo demas pasa a ser el gris de su misma claridad. Se
    cambia el color con que se dibuja, nunca lo que dice.
    """
    def pinta(r, g, b):
        d = max(r, g, b) - min(r, g, b)
        if d < 14:                                # ya es neutro: se deja igual
            return (r, g, b)
        if d < 40:                                # apenas teñido: se apaga
            gris = int(round(_luz(r, g, b) * 255))
            return (gris, gris, gris)
        h = _tono(r, g, b)
        luz = _luz(r, g, b)
        if 200 <= h <= 265:                       # el azul propio, intacto
            return (r, g, b)
        if 110 <= h < 200:                        # verdes y azulados: acento
            return _mezcla(COBALTO, luz)
        gris = int(round(min(0.98, max(0.07, luz)) * 255))
        return (gris, gris, gris)

    def enhex(m):
        s = m.group(1)
        if len(s) == 3:
            s = "".join(c * 2 for c in s)
        if len(s) == 8:                            # #rrggbbaa
            cola, s = s[6:], s[:6]
        else:
            cola = ""
        r, g, b = int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)
        return "#%02X%02X%02X%s" % (pinta(r, g, b) + (cola,))

    def enrgb(m):
        partes = [x.strip() for x in m.group(2).split(",")]
        if len(partes) < 3 or any("%" in x for x in partes[:3]):
            return m.group(0)
        try:
            r, g, b = (int(round(float(x))) for x in partes[:3])
        except ValueError:
            return m.group(0)
        nuevos = ["%d" % c for c in pinta(r, g, b)] + partes[3:]
        return "%s(%s)" % (m.group(1), ",".join(nuevos))

    css = re.sub(r"#([0-9A-Fa-f]{8}|[0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})\b", enhex, css)
    return re.sub(r"\b(rgba?)\(([^)]*)\)", enrgb, css)


def hoja_propia(doc, marca):
    for b in re.findall(r"<style>(.*?)</style>", fuente(doc), re.S):
        if marca in b:
            return b
    raise SystemExit("  %s: no se encuentra su hoja propia (%s)" % (doc, marca))


def main():
    secciones, menus, indice, orden, voces, mapa = monta()
    total = len(orden)
    for i, r, doc, _l, _n in SECCIONES:
        if doc:
            SEC_ROTULO[i] = r
    SEC_ROTULO["recorridos"] = "Recorridos"
    SEC_ROTULO["mapa"] = "El mapa"

    svg = mapa_interactivo(mapa)
    rutas_html, tarjetas = dibuja_recorridos(mapa)
    inicio = sec_inicio(indice, total, voces, svg, tarjetas)
    recorridos_html = sec_recorridos(rutas_html)
    mapa_html = sec_mapa(svg)

    nav = ('<button type="button" data-ir-sec="inicio">Inicio</button>'
           + "".join('<button type="button" data-ir-sec="%s">%s</button>' % (i, H.escape(r))
                     for i, r, doc, _l, _n in SECCIONES if doc))

    recursos = (
        '<div class="rec__g"><p class="rec__t">La entrega</p>'
        + "".join(
            ('<div class="rec__i" style="opacity:.55"><em>%s</em><div><b>%s</b>'
             '<p>%s Es la que está viendo.</p></div></div>' % (k, H.escape(n), H.escape(q)))
            if r == "centro.html" else
            ('<a class="rec__i" href="%s"%s><em>%s</em><div><b>%s</b><p>%s</p></div></a>'
             % (r, " download" if d else "", k, H.escape(n), H.escape(q)))
            for r, k, n, q, d in ENTREGA)
        + '</div><div class="rec__g"><p class="rec__t">Los ocho documentos</p>'
        + "".join(
            '<a class="rec__i" href="%s"><em>%02d</em><div><b>%s</b><p>%s</p></div></a>'
            % (doc, n + 1, H.escape(nombre), H.escape(INTROS[i][0]))
            for n, (i, _r, doc, _l, nombre) in enumerate([s for s in SECCIONES if s[2]]))
        + '</div><div class="rec__g"><p class="rec__t">El glosario</p>'
        + "".join(
            '<button class="rec__i" type="button" data-gl="%s"><em>voz</em>'
            '<div><b>%s</b><p>%s</p></div></button>'
            % (H.escape(k), H.escape(k), H.escape(voces[k][0]))
            for k in sorted(voces))
        + "</div>")

    grupo_de = {}
    for cod, estados, _n, _q in CATALOGO["grupos"]:
        for e in re.findall(r"E\d+", estados):
            grupo_de[e] = cod

    # Los recorridos, resueltos a identificadores reales, para el guion.
    rutas_datos = {}
    for r in recorridos():
        paradas = []
        for _rot, anc, _por in r["paradas"]:
            d = mapa.get("@" + anc)
            if d:
                paradas.append(d[0][0])
        if paradas:
            rutas_datos[r["id"]] = {"quien": r["quien"], "titulo": r["titulo"], "paradas": paradas}

    fases_datos = []
    for n in range(1, 13):
        d = mapa.get("@f%02d" % n)
        if d:
            fases_datos.append(d[0][0])
    for n in (13, 14):
        d = mapa.get("@m%02d" % n)
        if d:
            fases_datos.append(d[0][0])

    cuerpo = (MARCO.replace("@@NAV@@", nav)
                   .replace("@@PANELES@@", "\n".join(menus))
                   .replace("@@SECCIONES@@",
                            inicio + "\n" + recorridos_html + "\n" + mapa_html + "\n"
                            + "\n".join(secciones))
                   .replace("@@RECURSOS@@", recursos)
                   .replace("@EJEMPLO@", ", ".join(sorted(voces)[:3])))

    manual = fuente("manual.html")
    i = manual.index("<body>")
    cabecera = manual[:i + len("<body>")]
    cabecera = cabecera.replace("<title>Manual Maestro Giraldo</title>",
                                "<title>Centro de Excelencia Implantológica Giraldo</title>")
    cabecera = re.sub(
        r'<meta name="description" content="[^"]*">',
        '<meta name="description" content="Centro de Excelencia Implantológica Giraldo. Diez '
        'recorridos guiados, el mapa de las catorce fases y los ocho documentos del sistema con '
        'sus %d apartados, completos." >' % total, cabecera, count=1)
    extra = (CSS + "\n" + hoja_propia("protocolos.html", "PROTOCOLOS POR PUESTO")
             + "\n" + hoja_propia("instrumentos/captura.html", "HOJA DE CAPTURA")
             + "\n" + hoja_propia("deck.html", ".slide{"))
    k = cabecera.rindex("</style>")
    cabecera = cabecera[:k] + extra + "\n" + cabecera[k:]

    datos = ("<script>window.__ORDEN__ = "
             + json.dumps([[c, d, g, r, s] for c, d, g, r, s in orden], ensure_ascii=False)
             + ";\nwindow.__VOCES__ = " + json.dumps(voces, ensure_ascii=False)
             + ";\nwindow.__GRUPOESTADO__ = " + json.dumps(grupo_de, ensure_ascii=False)
             + ";\nwindow.__RUTAS__ = " + json.dumps(rutas_datos, ensure_ascii=False)
             + ";\nwindow.__FASES__ = " + json.dumps(fases_datos, ensure_ascii=False)
             + ";</script>")

    salida = RAIZ / "centro.html"
    texto = (cabecera + "\n" + cuerpo + "\n" + datos + "\n" + JS + "\n</body>\n</html>\n")
    texto = texto.replace("@@ARTES@@", imagenes.defensa())
    texto = texto.replace("@VERSION@", VERSION).replace("@FECHA@", FECHA)
    texto = re.sub(r"(<style[^>]*>)(.*?)(</style>)",
                   lambda m: m.group(1) + monocroma(m.group(2)) + m.group(3),
                   texto, flags=re.S)
    texto = re.sub(r'(style=")([^"]*)(")',
                   lambda m: m.group(1) + monocroma(m.group(2)) + m.group(3), texto)
    texto = re.sub(r'\b(fill|stroke|stop-color|flood-color|lighting-color)="([^"]*)"',
                   lambda m: '%s="%s"' % (m.group(1), monocroma(m.group(2))), texto)
    salida.write_text(texto, encoding="utf-8")

    cuerpo_html = re.sub(r"<script\b.*?</script>", "",
                         texto[texto.index('<div id="sitio">'):], flags=re.S)
    ids = set(re.findall(r'id="([^"]+)"', texto))
    muertos = sorted({h for h in re.findall(r'href="#([^"]+)"', cuerpo_html) if h not in ids})
    muertos += sorted({f for f in re.findall(r'data-abre-fase="([^"]+)"', cuerpo_html)
                       if f and f not in ids})
    if muertos:
        raise SystemExit("  enlaces muertos en centro.html: %s" % ", ".join(muertos[:8]))

    # Un identificador repetido rompe cualquier enlace que apunte a él. Se
    # admite una sola repetición conocida: la hoja de un apartado lleva el
    # mismo identificador que el apartado que envuelve, y es a la hoja a la que
    # se va. Cualquier otra para la construcción.
    cuenta = collections.Counter(re.findall(r'id="([^"]+)"', cuerpo_html))
    hojas = set(re.findall(r'<article class="hoja" id="([^"]+)"', cuerpo_html))
    sobra = sorted(k for k, v in cuenta.items() if v > 2 or (v == 2 and k not in hojas))
    if sobra:
        raise SystemExit("  identificadores repetidos en centro.html: %s"
                         % ", ".join(sobra[:8]))

    print("centro.html · %d recorridos · %d secciones · %d apartados · %d KB"
          % (len(rutas_datos), len(indice) + 3, total, salida.stat().st_size // 1024))


if __name__ == "__main__":
    main()
