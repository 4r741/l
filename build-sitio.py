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
import json
import pathlib
import re
import sys

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


def sin_marcas(html):
    """El texto llano, para el buscador y para contar."""
    t = re.sub(r"<(script|style)\b.*?</\1>", " ", html, flags=re.S | re.I)
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


def bloque_protocolos(pre):
    P = PERFILES
    botones, fichas = [], []
    for n, p in enumerate(P.PERFILES):
        raci = P.raci_de(p)
        activas = sum(1 for _f, papel in raci if papel != "—")
        botones.append(
            '<button type="button" class="puestobt%s" data-puesto="%s">'
            '<b>%s</b><span>%d de 14 fases</span></button>'
            % (" es-on" if n == 0 else "", p["id"], H.escape(p["corto"]), activas))
        celdas = "".join(
            '<div class="wraci__c %s" title="Fase %02d · %s · %s">'
            '<span class="wraci__f">%02d</span><span class="wraci__p">%s</span></div>'
            % (CLASE_RACI[papel], i + 1, H.escape(fase), H.escape(P.QUE_ES[papel][0]),
               i + 1, H.escape(papel))
            for i, (fase, papel) in enumerate(raci))
        bloques = "".join('<li><a href="manual.html#%s">%s</a></li>' % (a, H.escape(r))
                          for r, a in p["bloques"])
        vang = "".join('<li><a href="manual.html#%s">%s</a></li>' % (a, H.escape(r))
                       for r, a in p["vanguardia"])
        fichas.append(
            '<article class="puesto" data-puesto="%s"%s>\n'
            '  <p class="puesto__k">Puesto %d de 6 · columna %s de la matriz</p>\n'
            '  <h3>%s</h3>\n  <p class="puesto__q">%s</p>\n'
            '  %s\n'
            '  <p class="rotulillo">Su papel en las catorce fases del recorrido</p>\n'
            '  <div class="wraci">%s</div>\n'
            '  <p class="leyenda">%s</p>\n'
            '  <div class="puesto__cols">\n'
            '    <div><p class="rotulillo">Sus procedimientos escritos</p><ul class="lista2">%s</ul></div>\n'
            '    <div><p class="rotulillo">Sus funciones de vanguardia</p><ul class="lista2">%s</ul></div>\n'
            '  </div>\n'
            '  <p class="puesto__ir"><a href="manual.html#%s">Su manual de puesto, completo</a></p>\n'
            '</article>'
            % (p["id"], "" if n == 0 else " hidden", n + 1, p.get("wraci") or "—",
               H.escape(p["nombre"]), H.escape(p["que"]),
               cifras([(str(activas), "fases en las que interviene"),
                       (str(len(p["bloques"])), "procedimientos escritos"),
                       (str(len(p["vanguardia"])), "funciones de vanguardia")]),
               celdas,
               " · ".join("<b>%s</b> %s" % (k, H.escape(v[0])) for k, v in P.QUE_ES.items()),
               bloques or '<li class="es-vacio">Su manual no se numera en procedimientos: su '
                          'trabajo es de gobierno y está escrito en el manual del puesto.</li>',
               vang or '<li class="es-vacio">Ninguna propia: las suyas son de gobierno del '
                       'sistema.</li>', p["manual"]))
    return ("""
<div class="lienzo">
  <div class="lienzo__cab">
    <h2>Elija su puesto</h2>
    <p>Seis. Al elegir uno aparece lo suyo: dónde entra en las catorce fases y con qué papel,
      qué tiene escrito y qué funciones de vanguardia le tocan. Todo ocurre en esta página.</p>
  </div>
  <div class="puestosel">@@B@@</div>
  <div class="puestos">@@F@@</div>
</div>
""".replace("@@B@@", "".join(botones)).replace("@@F@@", "\n".join(fichas)))


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


BLOQUES = {
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
            '  <header class="cab">\n'
            '    <span class="cab__n" aria-hidden="true">%02d</span>\n'
            '    <p class="cab__k">%s · %d apartados</p>\n'
            '    <h1>%s</h1>\n'
            '    <p class="cab__p">%s</p>\n'
            '  </header>\n'
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
            % (ident, ident, len(indice), H.escape(nombre_doc), len(piezas), H.escape(titulo),
               H.escape(texto), propio, H.escape(rotulo.lower()), len(piezas),
               "".join(filas), "\n".join(hojas)))

    return secciones, menus, indice, orden, voces


def sec_inicio(indice, total, voces):
    hechos = "".join(
        '<div class="hecho"><b>%s</b><p class="hecho__r">%s</p><p class="hecho__q">%s</p></div>'
        % (n.replace("@TOTAL@", str(total)).replace("@ACC@", str(CATALOGO["total"])),
           H.escape(r), H.escape(q))
        for n, r, q in HECHOS)

    bloques = "".join(
        '<article class="idea"><p class="idea__k">%s</p><h3>%s</h3><p class="idea__q">%s</p>%s</article>'
        % (H.escape(k), H.escape(t), H.escape(q), cifras(c))
        for k, t, q, c in INICIO_BLOQUES)

    puertas = "".join(
        '<button type="button" class="puerta" data-ir-sec="%s">'
        '<span class="puerta__n">%02d</span><b>%s</b>'
        '<span class="puerta__q">%s</span>'
        '<span class="puerta__m">%d apartados</span></button>'
        % (i, n + 1, H.escape(nombre), H.escape(INTROS[i][0]), cuantos)
        for n, (i, _rot, nombre, cuantos) in enumerate(indice))

    return """
<section class="sec" id="inicio" data-sec="inicio">
  <div class="whero">
    <p class="whero__k">Centro de Excelencia Implantológica Giraldo · Rúa Bolivia nº 2 · Vigo</p>
    <h1>No medias<br><em>sonrisas</em></h1>
    <p class="whero__lema">«Le devolvemos su sonrisa completa, en el menor tiempo posible,
      y le cuidamos para siempre.»</p>
    <div class="whero__b">
      <button type="button" class="bt bt--fuerte" data-ir-sec="primera-visita">La primera visita</button>
      <button type="button" class="bt" data-abre="paleta">Buscar en todo el sistema</button>
    </div>
  </div>

  <div class="lienzo">
    <div class="lienzo__cab">
      <h2>Qué es esto</h2>
      <p>La promesa de arriba tiene dos mitades. La primera es el resultado y la fija el
        posicionamiento: ningún tratamiento se deja a medias. La segunda es la relación, y tiene
        instrumento propio. Debajo de esas dos frases hay ocho documentos, @TOTAL@ apartados y un
        sistema que se puede describir, enseñar, auditar y repetir. Están aquí enteros: esta
        página no resume nada.</p>
    </div>
    <div class="hechos">@@HECHOS@@</div>
  </div>

  <div class="lienzo">
    <div class="lienzo__cab">
      <h2>Cuatro cosas que conviene saber antes de entrar</h2>
      <p>No están en ningún documento porque en un documento no hacen falta. En un sitio son lo
        primero que se busca.</p>
    </div>
    <div class="ideas">@@IDEAS@@</div>
  </div>

  <div class="lienzo">
    <div class="lienzo__cab">
      <h2>Los ocho documentos</h2>
      <p>Cada uno es una sección, con su documento entero dentro. En el índice de arriba se
        despliegan sus apartados.</p>
    </div>
    <div class="puertas">@@PUERTAS@@</div>
  </div>

  <div class="lienzo">
    <div class="lienzo__cab">
      <h2>Lo que no haremos nunca</h2>
      <p>Un centro se reconoce antes por sus prohibiciones que por su catálogo. Estas seis están
        escritas y son las que se auditan primero cuando algo va mal.</p>
    </div>
    <ol class="prohibido">@@PRINCIPIOS@@</ol>
  </div>

  <div class="lienzo">
    <div class="lienzo__cab">
      <h2>Preguntas que nos hacen</h2>
      <p>Contestadas con lo que el sistema dice, no con lo que suena bien.</p>
    </div>
    <div class="faq">@@PREGUNTAS@@</div>
  </div>

  <div class="lienzo lienzo--contacto">
    <div class="contacto">
      <div>
        <p class="rotulillo">El centro</p>
        <p class="contacto__d">Centro de Excelencia Implantológica Giraldo<br>
          Rúa Bolivia nº 2 · 36203 Vigo · Pontevedra</p>
      </div>
      <div>
        <p class="rotulillo">Esta edición</p>
        <p class="contacto__d">Versión @VERSION@ · @FECHA@<br>
          Los ocho documentos comparten número y fecha</p>
      </div>
      <div>
        <p class="rotulillo">Uso</p>
        <p class="contacto__d">Interno y confidencial. Contiene información económica, laboral y
          estratégica; no se difunde fuera de la organización sin autorización expresa de la
          Dirección General.</p>
      </div>
    </div>
  </div>
</section>
""".replace("@@HECHOS@@", hechos).replace("@@IDEAS@@", bloques) \
   .replace("@@PRINCIPIOS@@", "".join(
       '<li><b>%s</b><p>%s</p></li>' % (H.escape(k), H.escape(q)) for k, q in PRINCIPIOS)) \
   .replace("@@PREGUNTAS@@", "".join(
       '<details class="faq__p"><summary>%s</summary><p>%s</p></details>'
       % (H.escape(k), H.escape(q)) for k, q in PREGUNTAS)) \
   .replace("@@PUERTAS@@", puertas).replace("@TOTAL@", str(total))


CSS = """
/* ===========================================================================
   EL CENTRO GIRALDO · LA WEB

   Negro, gris y blanco. Un solo color, y solo para lo que importa: el azul de
   trabajo señala lo que se puede pulsar, lo que está abierto y lo que manda en
   un dato. Todo lo demás es tipografía, aire y una regla de un píxel.

   La paleta del sistema visual anterior se reescribe entera aquí —incluidos
   los colores de puesto y los del semáforo, que la literatura trae dentro—
   para que ni un documento se salga del acuerdo.
   =========================================================================== */
:root{
  --negro:#0B0B0C; --tinta:#111113; --ink:#111113; --ink-2:#4A4A52;
  --muted:#8A8A93; --linea:#E2E2E5; --linea-2:#EFEFF1;
  --papel:#FAFAFA; --blanco:#FFFFFF; --gris:#F3F3F4;
  --azul:#1F45FF; --azul-o:#0A2ED6; --azul-s:rgba(31,69,255,.08); --azul-p:#E8ECFF;

  /* el sistema anterior, remapeado: la literatura viaja con estos nombres */
  --paper:var(--papel); --surface:var(--blanco); --surface-2:var(--gris);
  --line:var(--linea); --line-soft:var(--linea-2);
  --accent:var(--azul); --accent-ink:var(--azul-o); --accent-fuerte:var(--azul-o);
  --accent-soft:var(--azul-s); --acido:var(--azul-p); --acido-ink:var(--azul-o);
  --signal:var(--tinta); --alerta:var(--negro);
  --rol-recepcion:var(--muted); --rol-doctor:var(--ink-2); --rol-higienista:var(--muted);
  --rol-auxiliar:var(--muted); --rol-rac:var(--ink-2); --rol-direccion:var(--tinta);
  --sem-verde:var(--azul); --sem-amarillo:var(--muted); --sem-naranja:var(--ink-2);
  --sem-rojo:var(--negro);
  --radio:0px; --radio-s:0px;
  --sombra-1:none; --sombra-2:none;
  --nav:3.6rem; --texto:70ch; --ancho:80rem;
  --e:cubic-bezier(.2,.7,.3,1);
}
body{background:var(--papel);color:var(--tinta)}
*:focus-visible{outline:2px solid var(--azul);outline-offset:2px}
::selection{background:var(--azul);color:#fff}
.avance{position:fixed;inset:0 auto auto 0;height:2px;width:0;background:var(--azul);z-index:70;
  transition:width .12s linear}

/* --- la barra: nueve entradas y su panel --------------------------------- */
.nav{position:sticky;top:0;z-index:60;background:var(--blanco);
  border-bottom:1px solid var(--linea)}
.nav__f{display:flex;align-items:center;gap:1.2rem;height:var(--nav);padding:0 1.6rem;
  max-width:var(--ancho);margin:0 auto}
/* La marca se queda en el nombre: el descriptor largo se comía las dos últimas
   entradas del índice, y el nombre del centro ya está en la portada, en el pie
   y en cada documento. */
/* y si aun así no caben las nueve, la fila se desplaza sola y se avisa con un
   desvanecido en el borde, que es la única manera honesta de decir «hay más» */
.nav__l{-webkit-mask-image:linear-gradient(90deg,#000 0,#000 calc(100% - 1.4rem),transparent 100%);
  mask-image:linear-gradient(90deg,#000 0,#000 calc(100% - 1.4rem),transparent 100%)}
.nav__m{display:flex;align-items:baseline;gap:.5rem;text-decoration:none;color:var(--negro);
  font-size:.95rem;font-weight:600;letter-spacing:-.01em;flex:none;cursor:pointer;
  background:none;border:0;font-family:inherit}
.nav__m i{font-style:normal;font-weight:400;color:var(--muted)}
.nav__m em{font-style:normal;font-family:var(--f-mono);font-size:.58rem;letter-spacing:.12em;
  color:var(--muted)}
.nav__l{display:flex;gap:0;flex:1 1 auto;min-width:0;overflow-x:auto;scrollbar-width:none;
  height:100%;justify-content:flex-start}
.nav__l::-webkit-scrollbar{display:none}
.nav__l button{
  font:inherit;font-size:.83rem;cursor:pointer;border:0;background:none;color:var(--ink-2);
  padding:0 .7rem;white-space:nowrap;position:relative;height:100%;
}
.nav__l button::after{content:"";position:absolute;inset:auto .7rem 0 .7rem;height:2px;
  background:var(--azul);transform:scaleX(0);transition:transform .18s var(--e)}
.nav__l button:hover{color:var(--negro)}
.nav__l button.es-on{color:var(--negro);font-weight:600}
.nav__l button.es-on::after,.nav__l button.es-abierto::after{transform:scaleX(1)}
.nav__b{display:flex;gap:.3rem;flex:none;align-items:center}
.abrepal{display:flex;align-items:center;gap:.5rem;padding:.36rem .55rem .36rem .7rem;
  background:var(--gris);border:1px solid var(--linea);color:var(--muted);font:inherit;
  font-size:.8rem;cursor:pointer}
.abrepal:hover{border-color:var(--negro);color:var(--negro)}
.abrepal kbd{font-family:var(--f-mono);font-size:.58rem;background:var(--blanco);
  border:1px solid var(--linea);padding:.1rem .28rem;line-height:1}
.icono{font:inherit;cursor:pointer;display:inline-flex;align-items:center;justify-content:center;
  width:1.9rem;height:1.9rem;border:1px solid transparent;background:none;color:var(--muted);
  line-height:1}
.icono:hover:not(:disabled){border-color:var(--linea);color:var(--negro)}
.icono:disabled{opacity:.3;cursor:default}

/* El panel del índice: al pulsar una sección se despliegan sus apartados. */
.paneles{border-top:1px solid var(--linea-2);background:var(--blanco);
  max-height:min(62vh,34rem);overflow-y:auto}
.paneles[hidden]{display:none}
.sub{max-width:var(--ancho);margin:0 auto;padding:1.6rem 1.6rem 2rem;columns:3;column-gap:2.6rem}
.sub__g{break-inside:avoid;margin:1.1rem 0 .4rem;font-family:var(--f-mono);font-size:.6rem;
  letter-spacing:.15em;text-transform:uppercase;color:var(--azul)}
.sub__g:first-child{margin-top:0}
.sub a{break-inside:avoid;display:flex;gap:.7rem;align-items:baseline;text-decoration:none;
  color:var(--ink-2);font-size:.86rem;line-height:1.45;padding:.28rem 0}
.sub a span{font-family:var(--f-mono);font-size:.62rem;color:var(--muted);flex:none;min-width:1.4rem}
.sub a:hover{color:var(--azul)}

/* --- las secciones -------------------------------------------------------- */
.sec{max-width:var(--ancho);margin:0 auto;padding:4rem 1.6rem 8rem}
.sitio--vivo .sec{display:none}
.sitio--vivo .sec.es-on{display:block;animation:entra .2s var(--e)}
@keyframes entra{from{opacity:0}to{opacity:1}}
@media(prefers-reduced-motion:reduce){.sitio--vivo .sec.es-on{animation:none}}

.cab{max-width:56rem;padding-bottom:3rem;margin-bottom:4rem;border-bottom:1px solid var(--negro)}
.cab__k{margin:0;font-family:var(--f-mono);font-size:.64rem;letter-spacing:.18em;
  text-transform:uppercase;color:var(--muted)}
.cab h1{font-size:clamp(2.4rem,5.6vw,4.4rem);line-height:1.02;letter-spacing:-.035em;
  margin:1.4rem 0 0;font-weight:600;max-width:18ch}
.cab__p{margin:1.8rem 0 0;font-size:1.05rem;line-height:1.7;color:var(--ink-2);max-width:64ch}

.lienzo{margin-bottom:5.5rem}
.lienzo__cab{margin-bottom:2rem;max-width:58rem}
.lienzo__cab h2{font-size:clamp(1.35rem,2.4vw,1.8rem);letter-spacing:-.022em;margin:0;
  font-weight:600}
.lienzo__cab p{margin:.7rem 0 0;color:var(--ink-2);line-height:1.65;max-width:62ch}
.rotulillo{font-family:var(--f-mono);font-size:.6rem;letter-spacing:.16em;text-transform:uppercase;
  color:var(--muted);margin:0 0 .9rem}
.cifras{display:flex;flex-wrap:wrap;gap:2.2rem;margin:1.8rem 0 0}
.cifras b{display:block;font-size:1.6rem;font-weight:600;letter-spacing:-.02em;color:var(--negro)}
.cifras span{display:block;margin-top:.2rem;font-family:var(--f-mono);font-size:.6rem;
  letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}

/* --- inicio --------------------------------------------------------------- */
.whero{padding:3.4rem 0 4rem;border-bottom:1px solid var(--negro);margin-bottom:5rem}
.whero__k{margin:0;font-family:var(--f-mono);font-size:.62rem;letter-spacing:.18em;
  text-transform:uppercase;color:var(--muted)}
.whero h1{font-size:clamp(3.4rem,11vw,8.5rem);line-height:.92;letter-spacing:-.045em;
  margin:1.6rem 0 0;font-weight:600}
.whero h1 em{font-style:normal;color:var(--azul)}
.whero__lema{margin:2.4rem 0 0;font-size:clamp(1.05rem,2.1vw,1.4rem);line-height:1.45;
  color:var(--ink-2);max-width:38ch}
.whero__b{display:flex;flex-wrap:wrap;gap:.5rem;margin-top:2.6rem}
.bt{font:inherit;font-size:.88rem;cursor:pointer;padding:.7rem 1.4rem;border:1px solid var(--negro);
  background:none;color:var(--negro);transition:background .16s var(--e),color .16s var(--e)}
.bt:hover{background:var(--negro);color:#fff}
.bt--fuerte{background:var(--azul);border-color:var(--azul);color:#fff}
.bt--fuerte:hover{background:var(--azul-o);border-color:var(--azul-o)}

.hechos{display:grid;grid-template-columns:repeat(auto-fill,minmax(15rem,1fr));
  gap:1px;background:var(--linea);border:1px solid var(--linea)}
.hecho{background:var(--blanco);padding:1.6rem 1.5rem 1.7rem}
.hecho b{display:block;font-size:2.1rem;font-weight:600;letter-spacing:-.03em;color:var(--negro)}
.hecho__r{margin:.2rem 0 0;font-family:var(--f-mono);font-size:.6rem;letter-spacing:.14em;
  text-transform:uppercase;color:var(--azul)}
.hecho__q{margin:.9rem 0 0;font-size:.84rem;line-height:1.55;color:var(--ink-2)}

.ideas{display:grid;grid-template-columns:repeat(auto-fit,minmax(20rem,1fr));gap:3rem 3.4rem}
.idea__k{margin:0;font-family:var(--f-mono);font-size:.6rem;letter-spacing:.16em;
  text-transform:uppercase;color:var(--azul)}
.idea h3{margin:.7rem 0 0;font-size:1.5rem;letter-spacing:-.022em;font-weight:600;max-width:20ch}
.idea__q{margin:1rem 0 0;color:var(--ink-2);line-height:1.68}
.idea .cifras{gap:1.6rem;margin-top:1.6rem;padding-top:1.4rem;border-top:1px solid var(--linea)}
.idea .cifras b{font-size:1.15rem}

.puertas{display:grid;grid-template-columns:repeat(auto-fill,minmax(16rem,1fr));gap:1px;
  background:var(--linea);border:1px solid var(--linea)}
.puerta{font:inherit;text-align:left;cursor:pointer;border:0;background:var(--blanco);
  padding:1.5rem 1.5rem 1.6rem;display:flex;flex-direction:column;gap:.2rem;
  transition:background .16s var(--e)}
.puerta:hover{background:var(--negro)}
.puerta:hover b,.puerta:hover .puerta__q{color:#fff}
.puerta:hover .puerta__n,.puerta:hover .puerta__m{color:var(--azul-p)}
.puerta__n{font-family:var(--f-mono);font-size:.62rem;color:var(--azul)}
.puerta b{font-size:1.1rem;font-weight:600;letter-spacing:-.014em;color:var(--negro);margin-top:.4rem}
.puerta__q{margin-top:.5rem;font-size:.83rem;line-height:1.5;color:var(--ink-2)}
.puerta__m{margin-top:1.2rem;font-family:var(--f-mono);font-size:.6rem;letter-spacing:.1em;
  color:var(--muted)}

/* Lo que no se hará nunca: una lista numerada, en negativo. */
/* Seis en tres columnas: dos filas exactas. Con cuatro columnas quedaban dos
   huecos grises al final, que parecían un error y no un final. */
.prohibido{list-style:none;margin:0;padding:0;counter-reset:p;
  display:grid;grid-template-columns:repeat(auto-fit,minmax(21rem,1fr));gap:1px;
  background:var(--linea);border:1px solid var(--linea)}
.prohibido li{counter-increment:p;background:var(--blanco);padding:1.5rem 1.5rem 1.6rem;
  position:relative}
.prohibido li::before{content:counter(p,decimal-leading-zero);font-family:var(--f-mono);
  font-size:.6rem;color:var(--azul);display:block;margin-bottom:.7rem}
.prohibido b{display:block;font-size:1.02rem;font-weight:600;color:var(--negro);line-height:1.35}
.prohibido p{margin:.6rem 0 0;font-size:.86rem;line-height:1.6;color:var(--ink-2)}

/* Las preguntas: se abren de una en una y sin guion. */
.faq{border-top:1px solid var(--negro);max-width:58rem}
.faq__p{border-bottom:1px solid var(--linea)}
.faq__p summary{cursor:pointer;list-style:none;padding:1.1rem 2.4rem 1.1rem 0;position:relative;
  font-size:1.02rem;font-weight:600;color:var(--negro)}
.faq__p summary::-webkit-details-marker{display:none}
.faq__p summary::after{content:"+";position:absolute;right:.4rem;top:1rem;font-family:var(--f-mono);
  color:var(--azul);font-size:1.1rem;line-height:1}
.faq__p[open] summary::after{content:"−"}
.faq__p summary:hover{color:var(--azul)}
.faq__p p{margin:0 0 1.3rem;font-size:.95rem;line-height:1.68;color:var(--ink-2);max-width:60ch}

.lienzo--contacto{border-top:1px solid var(--negro);padding-top:2.6rem}
.contacto{display:grid;grid-template-columns:repeat(auto-fit,minmax(15rem,1fr));gap:2.4rem}
.contacto__d{margin:0;font-size:.88rem;line-height:1.65;color:var(--ink-2)}

/* --- el reloj y los carriles ---------------------------------------------- */
.reloj__barra{display:flex;height:5.4rem;border:1px solid var(--negro)}
.reloj__t{display:flex;flex-direction:column;justify-content:space-between;align-items:flex-start;
  padding:.6rem .55rem;text-decoration:none;color:var(--ink-2);border-right:1px solid var(--linea);
  overflow:hidden;min-width:0;box-sizing:border-box;flex-shrink:1;
  transition:background .16s var(--e),color .16s var(--e)}
.reloj__t:last-child{border-right:0}
.reloj__t:hover{background:var(--azul);color:#fff}
.reloj__t:hover .reloj__n,.reloj__t:hover .reloj__m{color:rgba(255,255,255,.75)}
.reloj__n{font-family:var(--f-mono);font-size:.6rem;color:var(--azul);font-weight:600}
.reloj__r{font-size:.72rem;line-height:1.2;font-weight:500;overflow:hidden;text-overflow:ellipsis;
  display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;white-space:normal}
.reloj__m{font-family:var(--f-mono);font-size:.58rem;color:var(--muted)}
.reloj__eje{position:relative;height:1.3rem;margin-top:.45rem}
.reloj__eje span{position:absolute;transform:translateX(-50%);font-family:var(--f-mono);
  font-size:.58rem;color:var(--muted)}
.reloj__eje span:first-child{transform:none}
.reloj__eje span:last-child{transform:translateX(-100%)}
.carriles{display:flex;flex-direction:column;gap:.35rem}
.carril{display:grid;grid-template-columns:9rem minmax(0,1fr);gap:1rem;align-items:center}
.carril__q{margin:0;font-size:.8rem;color:var(--ink-2);text-align:right}
.carril__p{position:relative;height:2rem;border:1px solid var(--linea)}
.carril__b{position:absolute;top:.2rem;bottom:.2rem;background:var(--gris);
  border:1px solid var(--linea);font-family:var(--f-mono);font-size:.58rem;color:var(--muted);
  display:flex;align-items:center;justify-content:center;text-decoration:none}
.carril__b.es-jefe{background:var(--azul);border-color:var(--azul);color:#fff}
.carril__b:hover{outline:2px solid var(--negro);outline-offset:1px;z-index:2}

/* --- puestos --------------------------------------------------------------- */
.puestosel{display:flex;flex-wrap:wrap;gap:0;border:1px solid var(--negro);margin-bottom:3rem}
.puestobt{font:inherit;cursor:pointer;text-align:left;background:none;border:0;
  border-right:1px solid var(--linea);padding:.85rem 1.3rem;flex:1 1 auto;
  transition:background .16s var(--e)}
.puestobt:last-child{border-right:0}
.puestobt b{display:block;font-size:.92rem;font-weight:600;color:var(--negro)}
.puestobt span{display:block;margin-top:.15rem;font-family:var(--f-mono);font-size:.58rem;
  color:var(--muted)}
.puestobt:hover{background:var(--gris)}
.puestobt.es-on{background:var(--negro)}
.puestobt.es-on b{color:#fff}
.puestobt.es-on span{color:var(--azul-p)}
.puesto__k{margin:0;font-family:var(--f-mono);font-size:.6rem;letter-spacing:.16em;
  text-transform:uppercase;color:var(--azul)}
.puesto h3{margin:.7rem 0 0;font-size:clamp(1.5rem,3vw,2.1rem);letter-spacing:-.024em;font-weight:600}
.puesto__q{margin:1rem 0 0;font-size:1rem;line-height:1.65;color:var(--ink-2);max-width:56ch}
.puesto .cifras{margin:2rem 0 2.6rem;padding:1.4rem 0;border-top:1px solid var(--linea);
  border-bottom:1px solid var(--linea)}
.wraci{display:grid;grid-template-columns:repeat(14,minmax(0,1fr));gap:2px}
.wraci__c{aspect-ratio:1;display:flex;flex-direction:column;align-items:center;justify-content:center;
  background:var(--gris);cursor:help}
.wraci__f{font-family:var(--f-mono);font-size:.52rem;color:var(--muted)}
.wraci__p{font-family:var(--f-mono);font-size:.7rem;font-weight:600;color:var(--muted)}
.wraci__c.wes-ra{background:var(--azul)}
.wraci__c.wes-r{background:var(--azul);opacity:.72}
.wraci__c.wes-a{background:var(--negro)}
.wraci__c.wes-ra .wraci__p,.wraci__c.wes-r .wraci__p,.wraci__c.wes-a .wraci__p,
.wraci__c.wes-ra .wraci__f,.wraci__c.wes-r .wraci__f,.wraci__c.wes-a .wraci__f{color:#fff}
.wraci__c.wes-c{background:var(--azul-p)}
.wraci__c.wes-c .wraci__p{color:var(--azul-o)}
.wraci__c.wes-i{background:var(--blanco);border:1px solid var(--linea)}
.wraci__c.wes-no{background:none;border:1px dashed var(--linea)}
.wraci__c.wes-no .wraci__p{color:var(--linea)}
.leyenda{margin:1rem 0 0;font-size:.76rem;color:var(--muted);line-height:1.6}
.leyenda b{font-family:var(--f-mono);color:var(--negro)}
.puesto__cols{display:grid;grid-template-columns:repeat(auto-fit,minmax(19rem,1fr));gap:2.6rem;
  margin-top:3rem}
.lista2{list-style:none;margin:0;padding:0;display:flex;flex-direction:column}
.lista2 li{font-size:.88rem;line-height:1.5;color:var(--ink-2);padding:.42rem 0;
  border-bottom:1px solid var(--linea-2)}
.lista2 li:last-child{border-bottom:0}
.lista2 .es-vacio{color:var(--muted)}

/* --- mapa de fases ---------------------------------------------------------- */
.wmapa{display:grid;grid-template-columns:repeat(auto-fill,minmax(11rem,1fr));gap:1px;
  background:var(--linea);border:1px solid var(--linea)}
.mfase{background:var(--blanco);padding:.9rem 1rem 1rem;text-decoration:none;display:flex;
  flex-direction:column;gap:.15rem;transition:background .16s var(--e)}
.mfase:hover{background:var(--negro)}
.mfase:hover b{color:#fff}
.mfase:hover .mfase__r{color:var(--azul-p)}
.mfase__n{font-family:var(--f-mono);font-size:.6rem;color:var(--azul)}
.mfase b{font-size:.88rem;font-weight:600;color:var(--negro);line-height:1.3;margin-top:.3rem}
.mfase__r{font-family:var(--f-mono);font-size:.56rem;color:var(--muted);margin-top:.4rem}

/* --- marketing --------------------------------------------------------------- */
.estados{display:grid;grid-template-columns:repeat(auto-fill,minmax(13rem,1fr));gap:1px;
  background:var(--linea);border:1px solid var(--linea)}
.estado{font:inherit;text-align:left;cursor:pointer;background:var(--blanco);border:0;
  padding:1rem 1.1rem 1.2rem;transition:background .16s var(--e)}
.estado:hover{background:var(--gris)}
.estado.es-on{background:var(--azul)}
.estado.es-on b,.estado.es-on p{color:#fff}
.estado.es-on .estado__n{color:rgba(255,255,255,.7)}
.estado__n{font-family:var(--f-mono);font-size:.58rem;color:var(--azul)}
.estado b{display:block;margin-top:.25rem;font-size:.95rem;color:var(--negro)}
.estado p{margin:.4rem 0 0;font-size:.79rem;line-height:1.45;color:var(--ink-2)}
.filtros{display:flex;flex-wrap:wrap;gap:.8rem;align-items:flex-end;margin-bottom:1.4rem}
.filtro{display:flex;flex-direction:column;gap:.3rem}
.filtro span{font-family:var(--f-mono);font-size:.56rem;letter-spacing:.14em;
  text-transform:uppercase;color:var(--muted)}
.filtro select{font:inherit;font-size:.84rem;padding:.42rem .6rem;border:1px solid var(--linea);
  background:var(--blanco);color:var(--tinta)}
.limpiar{font:inherit;font-size:.8rem;cursor:pointer;border:1px solid var(--linea);background:none;
  color:var(--muted);padding:.42rem .9rem}
.limpiar:hover{border-color:var(--negro);color:var(--negro)}
.cuentafiltro{font-family:var(--f-mono);font-size:.64rem;color:var(--muted);margin-left:auto}
.tablawrap{overflow-x:auto;border:1px solid var(--linea)}
.acciones{width:100%;border-collapse:collapse;font-size:.85rem;min-width:52rem;background:var(--blanco)}
.acciones th{font-family:var(--f-mono);font-size:.56rem;letter-spacing:.14em;text-transform:uppercase;
  color:var(--muted);text-align:left;padding:.8rem 1rem;border-bottom:1px solid var(--negro);
  background:var(--blanco);position:sticky;top:0}
.acciones td{padding:.85rem 1rem;border-bottom:1px solid var(--linea-2);vertical-align:top}
.acciones tr:last-child td{border-bottom:0}
.acciones tr:hover td{background:var(--gris)}
.acc__cod{font-family:var(--f-mono);font-size:.68rem;color:var(--azul);white-space:nowrap}
.acc__q b{display:block;font-weight:500;color:var(--negro);line-height:1.45}
.acc__q span{display:block;margin-top:.3rem;font-size:.74rem;color:var(--muted);line-height:1.4}
.acc__gana{color:var(--ink-2);line-height:1.45;max-width:22rem}
.acc__meta{white-space:nowrap}
.etq{display:inline-block;font-family:var(--f-mono);font-size:.56rem;letter-spacing:.06em;
  color:var(--ink-2);background:var(--gris);padding:.16rem .4rem;margin:0 .25rem .25rem 0}
.etq--verde{background:var(--azul-p);color:var(--azul-o)}
.etq--amarillo{background:var(--gris);color:var(--ink-2)}
.etq--naranja{background:var(--negro);color:#fff}
.acc__ef{white-space:nowrap;font-family:var(--f-mono);font-size:.7rem;color:var(--muted)}
.barrita{display:inline-block;width:2.6rem;height:4px;background:var(--linea);margin-right:.45rem;
  position:relative;vertical-align:middle}
.barrita::before{content:"";position:absolute;inset:0 auto 0 0;width:var(--v);background:var(--azul)}
.campanas{display:grid;grid-template-columns:repeat(auto-fill,minmax(18rem,1fr));gap:1px;
  background:var(--linea);border:1px solid var(--linea)}
.wcampana{background:var(--blanco);padding:1.4rem 1.4rem 1.5rem}
.wcampana__k{margin:0;font-family:var(--f-mono);font-size:.58rem;color:var(--azul)}
.wcampana h4{margin:.4rem 0 0;font-size:1.02rem;letter-spacing:-.014em;font-weight:600}
.wcampana__r{margin:.7rem 0 0;font-size:.84rem;line-height:1.55;color:var(--ink-2)}
.wcampana__c{display:flex;gap:1.4rem;margin:1.2rem 0 0;padding-top:1rem;
  border-top:1px solid var(--linea)}
.wcampana__c dt{font-family:var(--f-mono);font-size:.54rem;letter-spacing:.12em;
  text-transform:uppercase;color:var(--muted)}
.wcampana__c dd{margin:.25rem 0 0;font-size:1rem;font-weight:600;color:var(--negro)}

/* --- puente ----------------------------------------------------------------- */
.puente{display:flex;flex-direction:column;gap:.4rem}
.puente__t{height:3rem;padding:.5rem .9rem;background:var(--gris);border-left:3px solid var(--azul);
  width:max(var(--w),13rem);display:flex;flex-direction:column;justify-content:center}
.puente__r{font-size:.85rem;font-weight:600;color:var(--negro)}
.puente__v{font-family:var(--f-mono);font-size:.68rem;color:var(--ink-2)}
.puente__pie{margin:1.4rem 0 0;font-size:.88rem;color:var(--ink-2)}
.puente__pie b{color:var(--negro)}

/* --- el índice de la sección y sus apartados --------------------------------- */
.lienzo--indice .idx{columns:2;column-gap:3rem;border-top:1px solid var(--linea);padding-top:1.6rem}
.idx__g{break-inside:avoid;margin:1.4rem 0 .5rem;font-family:var(--f-mono);font-size:.6rem;
  letter-spacing:.15em;text-transform:uppercase;color:var(--azul)}
.idx__g:first-child{margin-top:0}
.idx__a{break-inside:avoid;display:flex;gap:.8rem;align-items:baseline;text-decoration:none;
  color:var(--ink-2);padding:.35rem 0}
.idx__a span{font-family:var(--f-mono);font-size:.64rem;color:var(--muted);flex:none;min-width:1.5rem}
.idx__a b{font-size:.92rem;font-weight:500;line-height:1.45}
.idx__a:hover b{color:var(--azul)}

.hojas{border-top:1px solid var(--negro);padding-top:3rem}
.sitio--vivo .hoja{display:none}
.sitio--vivo .hoja.es-on{display:block}
.hoja{max-width:var(--texto)}
.hoja__k{margin:0 0 2rem;font-family:var(--f-mono);font-size:.62rem;letter-spacing:.14em;
  text-transform:uppercase;color:var(--muted);display:flex;gap:.7rem;align-items:baseline}
.hoja__k span{color:var(--azul)}
.hoja .wrap{padding:0;max-width:none}
.hoja .section{padding:0;background:none;border:0}
.hoja .section + .section{margin-top:3.4rem;padding-top:3.4rem;border-top:1px solid var(--linea-2)}
.hoja .reveal{opacity:1!important;transform:none!important}
.hoja .phase__grid{grid-template-columns:minmax(0,1fr)}
.hoja .phase__meta{position:static}
.hoja .tablewrap{overflow-x:auto}
.ref{color:var(--ink-2);border-bottom:1px dotted var(--linea)}
/* Un enlace que cambia de sección lo dice: al lado del texto va el nombre de
   la sección a la que lleva. Nadie pulsa a ciegas y nadie aparece en un sitio
   que no esperaba. */
.salta{text-decoration:none;color:var(--azul);border-bottom:1px solid var(--azul-p)}
.salta:hover{border-bottom-color:var(--azul)}
.salta__d{font-style:normal;font-family:var(--f-mono);font-size:.58rem;letter-spacing:.1em;
  text-transform:uppercase;color:var(--muted);margin-left:.45rem;white-space:nowrap}
.salta__d::before{content:"→ "}
.salta:hover .salta__d{color:var(--azul)}
.puesto__ir{margin:2.6rem 0 0}
.puesto__ir a{font-size:.9rem}
.gl{font:inherit;cursor:help;background:none;border:0;padding:0;color:inherit;
  border-bottom:1px solid var(--azul)}
.gl:hover{color:var(--azul)}
.remate{display:flex;flex-wrap:wrap;gap:.8rem;align-items:center;justify-content:space-between;
  margin-top:4rem;padding-top:1.6rem;border-top:1px solid var(--linea)}
.remate a{text-decoration:none;font-size:.85rem;color:var(--ink-2);display:inline-flex;gap:.5rem}
.remate a:hover{color:var(--azul)}
.remate a i{font-style:normal;font-family:var(--f-mono);font-size:.64rem;color:var(--muted)}
.wpasos{display:flex;gap:.4rem}
.wpasos button{font:inherit;cursor:pointer;width:2rem;height:2rem;border:1px solid var(--linea);
  background:none;color:var(--ink-2)}
.wpasos button:hover:not(:disabled){border-color:var(--negro);color:var(--negro)}
.wpasos button:disabled{opacity:.3;cursor:default}

/* ---------------------------------------------------------------------------
   MOVIMIENTO
   Poco y con motivo: los bloques entran una vez al aparecer, los enlaces
   crecen su raya al pasar por encima y la barra de lectura dice en qué
   apartado se está. Nada gira, nada rebota y todo se apaga si el sistema pide
   menos movimiento.
   --------------------------------------------------------------------------- */
.entra-al-ver{opacity:0;transform:translateY(10px)}
.wve{opacity:1;transform:none;transition:opacity .5s var(--e),transform .5s var(--e)}
@media(prefers-reduced-motion:reduce){
  .entra-al-ver{opacity:1;transform:none}
  .wve{transition:none}
}

/* El numeral de la sección: dos cifras enormes al fondo de la cabecera, que
   dicen dónde está uno sin ocupar una línea de texto. */
.cab{position:relative;overflow:hidden}
.cab__n{position:absolute;top:-1.6rem;right:-.6rem;font-size:clamp(6rem,14vw,11rem);
  line-height:.8;font-weight:600;letter-spacing:-.06em;color:var(--linea-2);
  pointer-events:none;user-select:none;z-index:0}
.cab > *{position:relative;z-index:1}

/* La barra de lectura: aparece cuando hay un apartado abierto y se queda
   pegada bajo el índice. Dice qué se está leyendo y cuántos quedan. */
.leyendo{position:sticky;top:var(--nav);z-index:40;display:flex;align-items:center;gap:1rem;
  padding:.6rem 0;margin:0 0 2rem;background:var(--papel);border-bottom:1px solid var(--linea);
  font-size:.82rem;color:var(--muted)}
.leyendo b{color:var(--negro);font-weight:600;white-space:nowrap;overflow:hidden;
  text-overflow:ellipsis}
.leyendo__n{font-family:var(--f-mono);font-size:.66rem;margin-left:auto;white-space:nowrap}
.leyendo__p{flex:none;width:5rem;height:2px;background:var(--linea);position:relative}
.leyendo__p i{position:absolute;inset:0 auto 0 0;background:var(--azul);width:var(--v,0%)}

/* Los enlaces del cuerpo: la raya crece de izquierda a derecha. */
.hoja a:not(.salta):not(.gl),.lienzo__cab a{
  color:var(--negro);text-decoration:none;background-image:linear-gradient(var(--azul),var(--azul));
  background-size:0% 1px;background-position:0 100%;background-repeat:no-repeat;
  border-bottom:1px solid var(--linea);transition:background-size .22s var(--e),color .16s var(--e);
}
.hoja a:not(.salta):not(.gl):hover,.lienzo__cab a:hover{color:var(--azul);background-size:100% 1px}

/* --- lo que flota ------------------------------------------------------------ */
.velo{position:fixed;inset:0;z-index:80;display:flex;align-items:flex-start;justify-content:center;
  padding:8vh 1.2rem 1.2rem;background:rgba(11,11,12,.42);animation:vela .14s ease}
@keyframes vela{from{opacity:0}to{opacity:1}}
.velo[hidden]{display:none}
.flota{width:min(44rem,100%);max-height:82vh;display:flex;flex-direction:column;overflow:hidden;
  background:var(--blanco);border:1px solid var(--negro);animation:sube .16s var(--e)}
@keyframes sube{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
@media(prefers-reduced-motion:reduce){.velo,.flota{animation:none}}
.flota__cab{display:flex;align-items:center;gap:.7rem;padding:.9rem 1.1rem;
  border-bottom:1px solid var(--linea)}
.flota__cab h2{margin:0;font-size:.98rem;font-weight:600;flex:1}
.flota__cuerpo{overflow-y:auto;padding:1.2rem 1.3rem 1.5rem}
.flota__pie{padding:.6rem 1.1rem;border-top:1px solid var(--linea);background:var(--gris);
  font-family:var(--f-mono);font-size:.6rem;letter-spacing:.08em;color:var(--muted);
  display:flex;gap:1.1rem;flex-wrap:wrap}
.flota__pie kbd{background:var(--blanco);border:1px solid var(--linea);padding:.1rem .3rem;
  font-family:inherit}
.pal__campo{display:flex;align-items:center;gap:.7rem;padding:1rem 1.2rem;
  border-bottom:1px solid var(--linea)}
.pal__campo input{flex:1;border:0;outline:none;background:none;font:inherit;font-size:1rem;
  color:var(--tinta)}
.pal__lista{overflow-y:auto;padding:.4rem;max-height:56vh}
.pal__g{margin:.8rem .6rem .35rem;font-family:var(--f-mono);font-size:.58rem;letter-spacing:.15em;
  text-transform:uppercase;color:var(--muted)}
.pal__i{display:flex;gap:.8rem;align-items:baseline;width:100%;text-align:left;font:inherit;
  cursor:pointer;background:none;border:0;padding:.55rem .6rem;color:var(--ink-2)}
.pal__i span{font-family:var(--f-mono);font-size:.6rem;color:var(--muted);flex:none;min-width:1.5rem}
.pal__i b{font-weight:500;font-size:.92rem;line-height:1.35}
.pal__i i{font-style:normal;font-size:.74rem;color:var(--muted);margin-left:auto;flex:none;
  padding-left:1rem}
.pal__i mark{background:var(--azul-p);color:var(--azul-o)}
.pal__i:hover,.pal__i.es-aqui{background:var(--gris)}
.pal__i.es-aqui{background:var(--azul);color:#fff}
.pal__i.es-aqui b,.pal__i.es-aqui span,.pal__i.es-aqui i{color:#fff}
.pal__i b .pal__ctx{display:block;font-family:inherit;font-size:.77rem;font-weight:400;
  color:var(--muted);margin-top:.25rem;line-height:1.5;letter-spacing:0}
.pal__i.es-aqui .pal__ctx{color:rgba(255,255,255,.8)}
.pal__nada{padding:2rem 1rem;text-align:center;color:var(--muted);font-size:.9rem}
.voz{position:absolute;z-index:90;width:min(22rem,calc(100vw - 2rem));background:var(--blanco);
  border:1px solid var(--negro);padding:1rem 1.1rem}
.voz[hidden]{display:none}
.voz b{display:block;font-size:.98rem;font-weight:600;color:var(--negro)}
.voz p{margin:.5rem 0 0;font-size:.86rem;line-height:1.55;color:var(--ink-2)}
.voz small{display:block;margin-top:.8rem;padding-top:.6rem;border-top:1px solid var(--linea);
  font-family:var(--f-mono);font-size:.58rem;letter-spacing:.1em;text-transform:uppercase;
  color:var(--muted)}
.rec__g{margin:0 0 1.7rem}
.rec__g:last-child{margin-bottom:0}
.rec__t{margin:0 0 .8rem;font-family:var(--f-mono);font-size:.6rem;letter-spacing:.15em;
  text-transform:uppercase;color:var(--azul)}
.rec__i{display:flex;gap:.9rem;align-items:flex-start;padding:.7rem .8rem;text-decoration:none;
  color:inherit;width:100%;text-align:left;font:inherit;background:none;border:0;cursor:pointer}
.rec__i:hover{background:var(--gris)}
.rec__i em{font-style:normal;font-family:var(--f-mono);font-size:.58rem;color:var(--azul);
  flex:none;min-width:2.6rem;padding-top:.2rem;letter-spacing:.08em}
.rec__i b{display:block;font-size:.92rem;font-weight:600;color:var(--negro)}
.rec__i p{margin:.2rem 0 0;font-size:.8rem;line-height:1.5;color:var(--ink-2)}
.tec{display:grid;grid-template-columns:auto 1fr;gap:.5rem 1.1rem;align-items:baseline}
.tec dt{font-family:var(--f-mono);font-size:.7rem;color:var(--negro);white-space:nowrap}
.tec dt kbd{background:var(--gris);border:1px solid var(--linea);padding:.14rem .4rem;
  font-family:inherit}
.tec dd{margin:0;font-size:.86rem;color:var(--ink-2);line-height:1.5}
.lupa{align-items:center;padding:3vh 3vw}
.lupa .flota{width:min(72rem,100%);max-height:94vh}
.lupa__lienzo{padding:1.8rem 2rem 2rem;overflow:auto}
.lupa__lienzo > *{max-width:100%;margin:0}
.lupa__lienzo svg{width:100%;height:auto}
.ampliable{cursor:zoom-in}
.pito{position:fixed;left:50%;bottom:2rem;transform:translateX(-50%);z-index:95;
  background:var(--negro);color:#fff;padding:.65rem 1.2rem;font-size:.85rem;animation:sube .16s ease}
.pito[hidden]{display:none}

@media(max-width:900px){
  :root{--nav:auto}
  .nav__f{flex-wrap:wrap;height:auto;padding:.55rem 1rem;gap:.5rem 1rem}
  .nav__m{flex:1 1 auto}
  .nav__l{order:3;flex:1 0 100%;min-width:100%;height:2.3rem}
  .nav__l button{padding:0 .65rem}
  .abrepal span{display:none}
  .sub{columns:1;padding:1.2rem 1rem 1.6rem}
  .sec{padding:2.4rem 1.1rem 5rem}
  .whero{padding:2.6rem 0 2.6rem}
  .reloj__barra{height:auto;flex-direction:column}
  .reloj__t{width:100%!important;flex-direction:row;gap:.7rem;align-items:center;
    border-right:0;border-bottom:1px solid var(--linea)}
  .reloj__r{-webkit-line-clamp:1;flex:1}
  .reloj__eje{display:none}
  .carril{grid-template-columns:5rem minmax(0,1fr);gap:.5rem}
  .wraci{grid-template-columns:repeat(7,minmax(0,1fr))}
  .lienzo--indice .idx{columns:1}
  .puestosel{flex-direction:column}
  .puestobt{border-right:0;border-bottom:1px solid var(--linea)}
  .velo{padding:4vh .8rem .8rem}
}
@media print{
  .nav,.paneles,.velo,.voz,.avance,.pito,.remate{display:none}
  .sitio--vivo .sec,.sitio--vivo .hoja{display:block}
  .hoja{break-after:page}
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
  var paneles= D.getElementById("paneles");
  var avance = D.getElementById("avance");
  if(!secs.length) return;

  /* Las marcas las pone el guion: si no llegara a correr se ve el sitio entero
     seguido —las nueve secciones y los 135 apartados— y no una página vacía. */
  sitio.classList.add("sitio--vivo");

  var porHoja = {};
  hojas.forEach(function(h){ porHoja[h.dataset.hoja] = h; });

  var LLAVE = "giraldo.web.v8";
  var memo = {sec:"inicio", hoja:{}};
  try { var g = localStorage.getItem(LLAVE); if(g) memo = JSON.parse(g) || memo; } catch(e){}
  if(!memo.hoja) memo.hoja = {};
  function recuerda(){ try { localStorage.setItem(LLAVE, JSON.stringify(memo)); } catch(e){} }
  function esc(s){ return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;"); }

  /* ---- ir a una sección, y dentro de ella a un apartado ---------------- */
  function veSec(id, arriba){
    var s = secs.filter(function(x){ return x.dataset.sec === id; })[0] || secs[0];
    secs.forEach(function(x){ x.classList.toggle("es-on", x === s); });
    [].slice.call(D.querySelectorAll(".nav__l button")).forEach(function(b){
      b.classList.toggle("es-on", b.dataset.irSec === s.dataset.sec);
    });
    memo.sec = s.dataset.sec; recuerda();
    /* cada sección recuerda el apartado que se estaba leyendo en ella */
    var suyas = [].slice.call(s.querySelectorAll(".hoja"));
    if(suyas.length){
      var quiere = memo.hoja[s.dataset.sec];
      var viva = suyas.filter(function(h){ return h.classList.contains("es-on"); })[0];
      if(!viva) veHoja((quiere && porHoja[quiere]) ? quiere : suyas[0].dataset.hoja, false);
    }
    if(arriba !== false) window.scrollTo(0, 0);
    return s;
  }

  function veHoja(clave, subir){
    var h = porHoja[clave];
    if(!h) return;
    var s = h.closest(".sec");
    [].slice.call(s.querySelectorAll(".hoja")).forEach(function(x){
      x.classList.toggle("es-on", x === h);
    });
    [].slice.call(s.querySelectorAll("[data-ir]")).forEach(function(a){
      a.classList.toggle("es-on", a.dataset.ir === clave);
    });
    memo.hoja[s.dataset.sec] = clave; recuerda();
    pinta(h, s);
    var todas = [].slice.call(s.querySelectorAll(".hoja"));
    pintaLeyendo(s, h, todas.indexOf(h), todas.length);
    if(subir !== false) h.scrollIntoView({block:"start", behavior:"smooth"});
  }

  /* El pie de cada apartado: dónde está y qué viene después. Se pinta al
     abrirlo y no antes, que son ciento treinta y cinco. */
  function pinta(h, s){
    var suyas = [].slice.call(s.querySelectorAll(".hoja"));
    var i = suyas.indexOf(h);
    var viejo = h.querySelector(".remate");
    if(viejo) viejo.remove();
    var pie = D.createElement("div");
    pie.className = "remate";
    var sig = suyas[i + 1], ant = suyas[i - 1];
    pie.innerHTML =
      '<div class="wpasos">'
      + '<button type="button" data-paso="-1"' + (ant ? "" : " disabled") + ' aria-label="Anterior">&#8592;</button>'
      + '<button type="button" data-paso="1"' + (sig ? "" : " disabled") + ' aria-label="Siguiente">&#8594;</button>'
      + '</div>'
      + (sig ? '<a href="#' + sig.dataset.hoja + '" data-ir="' + sig.dataset.hoja + '">'
             + '<i>Sigue</i> ' + esc(rotulo(sig.dataset.hoja)) + "</a>"
             : '<span class="ref">Último apartado de esta sección</span>')
      + '<span class="ref" style="font-family:var(--f-mono);font-size:.64rem;border:0">'
      + (i + 1) + " / " + suyas.length + "</span>";
    h.appendChild(pie);
    pie.addEventListener("click", function(e){
      var b = e.target.closest("button[data-paso]");
      if(!b) return;
      var j = i + parseInt(b.dataset.paso, 10);
      if(suyas[j]) veHoja(suyas[j].dataset.hoja, true);
    });
  }
  function rotulo(clave){
    for(var i = 0; i < orden.length; i++){ if(orden[i][0] === clave) return orden[i][3]; }
    return "";
  }

  /* ---- el índice de la barra ------------------------------------------- */
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

  /* Un solo camino para llegar a cualquier cosa por su identificador: lo usan
     los enlaces, la dirección al cargar y el cambio de dirección. Antes la
     dirección al cargar solo entendía apartados enteros, y un enlace copiado
     a una función concreta abría el inicio. */
  function irA(id, suave){
    if(porHoja[id]){
      veSec(porHoja[id].closest(".sec").dataset.sec, false);
      veHoja(id, suave !== false);
      return true;
    }
    if(secs.some(function(s){ return s.dataset.sec === id; })){
      veSec(id, true);
      return true;
    }
    var el = D.getElementById(id);
    if(!el) return false;
    var sec = el.closest(".sec");
    if(sec) veSec(sec.dataset.sec, false);
    var dueno = el.closest(".hoja");
    if(dueno) veHoja(dueno.dataset.hoja, false);
    el.scrollIntoView({block:"start", behavior: suave === false ? "auto" : "smooth"});
    return true;
  }

  D.addEventListener("click", function(e){
    var nb = e.target.closest(".nav__l button[data-ir-sec]");
    if(nb){
      var abierto = !paneles.hidden && nb.classList.contains("es-abierto");
      veSec(nb.dataset.irSec, true);
      if(abierto) cierraPanel(); else abrePanel(nb.dataset.irSec);
      return;
    }
    var b = e.target.closest("[data-ir-sec]");
    if(b){ cierraPanel(); veSec(b.dataset.irSec, true); return; }

    var a = e.target.closest("a[data-ir], a[href^='#']");
    if(a){
      var clave = a.dataset.ir || a.getAttribute("href").slice(1);
      if(D.getElementById(clave) || porHoja[clave]){
        e.preventDefault(); cierraPanel();
        irA(clave, true);
        try { history.replaceState(null, "", "#" + clave); } catch(err){}
      }
      return;
    }
    if(!e.target.closest(".nav")) cierraPanel();
  });

  /* ---- puestos ---------------------------------------------------------- */
  D.addEventListener("click", function(e){
    var b = e.target.closest(".puestobt");
    if(!b) return;
    [].slice.call(D.querySelectorAll(".puestobt")).forEach(function(x){
      x.classList.toggle("es-on", x === b);
    });
    [].slice.call(D.querySelectorAll(".puesto")).forEach(function(p){
      p.hidden = p.dataset.puesto !== b.dataset.puesto;
    });
  });

  /* ---- marketing -------------------------------------------------------- */
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
      ? (filas.length + " acciones") : (vivas + " de " + filas.length + " acciones");
  }
  [].slice.call(D.querySelectorAll("[data-filtro]")).forEach(function(s){
    s.addEventListener("change", function(){ filtra(); apagaEstados(); });
  });
  function apagaEstados(){
    [].slice.call(D.querySelectorAll(".estado")).forEach(function(b){ b.classList.remove("es-on"); });
  }
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
    var yaEstaba = b.classList.contains("es-on");
    apagaEstados();
    sel.value = yaEstaba ? "" : g;
    if(!yaEstaba) b.classList.add("es-on");
    filtra();
    if(!yaEstaba && tabla) tabla.closest(".lienzo").scrollIntoView({block:"start", behavior:"smooth"});
  });
  filtra();

  /* ---- lo que flota ------------------------------------------------------ */
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
    D.documentElement.style.overflow = "";
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

  /* ---- la paleta --------------------------------------------------------- */
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
      cache.push({id:b.dataset.irSec, doc:"Sección", rot:b.textContent.trim(), n:"", seccion:true});
    });
    hojas.forEach(function(h){
      var o = null;
      for(var i=0;i<orden.length;i++){ if(orden[i][0] === h.dataset.hoja){ o = orden[i]; break; } }
      if(!o) return;
      var crudo = (h.innerText || h.textContent || "").replace(/\\s+/g," ");
      cache.push({id:h.dataset.hoja, doc:o[1], grupo:o[2], rot:o[3], n:"",
                  crudo:crudo, txt:llano(crudo), rotll:llano(o[3])});
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
         + '<span>' + (d.seccion ? "&#8594;" : "&middot;") + "</span>"
         + '<b>' + esc(d.rot) + (q && !d.seccion ? '<span class="pal__ctx">' + trozo(d,q) + "</span>" : "") + "</b>"
         + '<i>' + esc(d.doc) + "</i></button>";
  }
  function pinta_paleta(q){
    q = llano((q||"").trim());
    var datos = indexa();
    var ss = datos.filter(function(d){ return d.seccion; });
    var aa = datos.filter(function(d){ return !d.seccion; });
    if(!q){
      lista.innerHTML = '<p class="pal__g">Las nueve secciones</p>'
        + ss.map(function(d){ return fila(d,""); }).join("")
        + '<p class="pal__g">Apartados</p>' + aa.slice(0,20).map(function(d){ return fila(d,""); }).join("");
    } else {
      var s1 = ss.filter(function(d){ return llano(d.rot).indexOf(q) > -1; });
      var r1 = aa.filter(function(d){ return d.rotll.indexOf(q) > -1; });
      var t1 = aa.filter(function(d){ return d.rotll.indexOf(q) < 0 && d.txt.indexOf(q) > -1; });
      function entera(d){
        var i = d.txt.indexOf(q);
        if(i < 0) return false;
        var a = i ? d.txt[i-1] : " ", b = i+q.length < d.txt.length ? d.txt[i+q.length] : " ";
        return !/[a-z0-9]/.test(a) && !/[a-z0-9]/.test(b);
      }
      t1.sort(function(m,n){ return (entera(n)?1:0) - (entera(m)?1:0); });
      if(!s1.length && !r1.length && !t1.length){
        lista.innerHTML = '<p class="pal__nada">Nada con «' + esc(q) + '» en el sistema.</p>';
      } else {
        lista.innerHTML =
          (s1.length ? '<p class="pal__g">Secciones</p>' + s1.map(function(d){ return fila(d,""); }).join("") : "")
          + (r1.length ? '<p class="pal__g">' + r1.length + ' en el rótulo</p>' + r1.map(function(d){ return fila(d,""); }).join("") : "")
          + (t1.length ? '<p class="pal__g">' + t1.length + ' en el texto</p>' + t1.map(function(d){ return fila(d,q); }).join("") : "");
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
    if(porHoja[v]){ veSec(porHoja[v].closest(".sec").dataset.sec, false); veHoja(v, true); }
    else veSec(v, true);
  });

  /* ---- glosario ---------------------------------------------------------- */
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

  /* ---- lupa -------------------------------------------------------------- */
  var lienzo = D.getElementById("lupalienzo");
  D.addEventListener("click", function(e){
    var f = e.target.closest("figure, .fig, .t-fig, .tablewrap, .tablawrap");
    if(!f || !lienzo) return;
    if(e.target.closest("a, button, input, select")) return;
    lienzo.innerHTML = "";
    lienzo.appendChild(f.cloneNode(true));
    abre("lupa");
  });
  [].slice.call(D.querySelectorAll("figure, .fig, .t-fig")).forEach(function(f){
    f.classList.add("ampliable");
    f.setAttribute("title", "Pulse para verla de cerca");
  });

  /* ---- teclado ----------------------------------------------------------- */
  D.addEventListener("keydown", function(e){
    var t = e.target;
    var escribiendo = t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA"
                            || t.tagName === "SELECT" || t.isContentEditable);
    if(e.key === "Escape"){ if(cierra()) { e.preventDefault(); return; } cierraPanel(); return; }
    if((e.metaKey || e.ctrlKey) && (e.key === "k" || e.key === "K")){ e.preventDefault(); abre("paleta"); return; }
    if(escribiendo || e.ctrlKey || e.metaKey || e.altKey) return;
    if(e.key === "/"){ e.preventDefault(); abre("paleta"); return; }
    if(e.key === "?"){ e.preventDefault(); abre("teclas"); return; }
    if(e.key === "r" || e.key === "R"){ e.preventDefault(); abre("recursos"); return; }
    if(e.key === "g"){ veSec("inicio", true); return; }
    var viva = D.querySelector(".sec.es-on");
    if(!viva) return;
    var suyas = [].slice.call(viva.querySelectorAll(".hoja"));
    if(!suyas.length) return;
    var i = suyas.findIndex(function(h){ return h.classList.contains("es-on"); });
    if(e.key === "ArrowRight" && suyas[i+1]) veHoja(suyas[i+1].dataset.hoja, true);
    if(e.key === "ArrowLeft" && suyas[i-1]) veHoja(suyas[i-1].dataset.hoja, true);
  });

  /* ---- la barra de lectura de cada sección ------------------------------- */
  function pintaLeyendo(s, h, i, n){
    var barra = s.querySelector(".leyendo");
    if(!barra) return;
    barra.hidden = false;
    barra.querySelector("b").textContent = rotulo(h.dataset.hoja);
    barra.querySelector(".leyendo__n").textContent = (i + 1) + " / " + n;
    barra.querySelector(".leyendo__p i").style.setProperty("--v", (100 * (i + 1) / n) + "%");
  }

  /* ---- lo que entra al aparecer ------------------------------------------ */
  /* Una sola vez, y solo lo que hay antes de la lectura: los bloques de datos.
     El texto de los documentos no se toca, que se lee y no se mira. */
  if("IntersectionObserver" in window){
    var ojo = new IntersectionObserver(function(es){
      es.forEach(function(en){
        if(!en.isIntersecting) return;
        en.target.classList.add("wve");
        ojo.unobserve(en.target);
      });
    }, {rootMargin: "0px 0px -8% 0px"});
    [].slice.call(D.querySelectorAll(".lienzo, .hecho, .idea, .puerta, .cab")).forEach(function(x){
      x.classList.add("entra-al-ver");
      ojo.observe(x);
    });
  }

  /* ---- avance de lectura ------------------------------------------------- */
  function dibujaAvance(){
    if(!avance) return;
    var alto = D.documentElement.scrollHeight - window.innerHeight;
    avance.style.width = alto > 0 ? (100 * window.scrollY / alto) + "%" : "0";
  }
  window.addEventListener("scroll", dibujaAvance, {passive:true});
  window.addEventListener("resize", dibujaAvance);

  window.addEventListener("hashchange", function(){
    var h = (location.hash || "").slice(1);
    if(h) irA(h, true);
  });

  /* ---- arranque ---------------------------------------------------------- */
  var h0 = (location.hash || "").slice(1);
  if(!h0 || !irA(h0, false)) veSec(memo.sec || "inicio", false);
  dibujaAvance();
})();
</script>
"""


MARCO = """
<a class="saltar" href="#sitio">Saltar al contenido</a>
<div class="avance" id="avance" aria-hidden="true"></div>

<header class="nav">
  <div class="nav__f">
    <button class="nav__m" type="button" data-ir-sec="inicio">Giraldo <em>v@VERSION@</em></button>
    <nav class="nav__l" aria-label="Secciones">@@NAV@@</nav>
    <div class="nav__b">
      <button class="abrepal" type="button" data-abre="paleta"><span>Buscar</span><kbd>⌘K</kbd></button>
      <button class="icono" type="button" data-abre="recursos" aria-label="Recursos" title="Recursos (R)">&#9781;</button>
      <button class="icono" type="button" data-abre="teclas" aria-label="Atajos" title="Atajos (?)">?</button>
    </div>
  </div>
  <div class="paneles" id="paneles" hidden>@@PANELES@@</div>
</header>

<div id="sitio">
@@SECCIONES@@
</div>

<div class="velo" data-velo="paleta" role="dialog" aria-modal="true" aria-label="Buscar" hidden>
  <div class="flota">
    <div class="pal__campo">
      <svg width="15" height="15" viewBox="0 0 16 16" aria-hidden="true" style="color:var(--muted);flex:none">
        <circle cx="7" cy="7" r="4.6" fill="none" stroke="currentColor" stroke-width="1.7"/>
        <path d="M10.4 10.4 L14.4 14.4" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/>
      </svg>
      <input id="palq" type="search" autocomplete="off" spellcheck="false"
             placeholder="Buscar secciones, apartados y texto" aria-label="Buscar">
      <button class="icono" type="button" data-cerrar aria-label="Cerrar">&#10005;</button>
    </div>
    <div class="pal__lista" id="pallista"></div>
    <div class="flota__pie"><span><kbd>&#8593;</kbd><kbd>&#8595;</kbd> moverse</span>
      <span><kbd>&#8629;</kbd> abrir</span><span><kbd>Esc</kbd> cerrar</span></div>
  </div>
</div>

<div class="velo" data-velo="recursos" role="dialog" aria-modal="true" aria-label="Recursos" hidden>
  <div class="flota">
    <div class="flota__cab"><h2>Recursos del sistema</h2>
      <button class="icono" type="button" data-cerrar aria-label="Cerrar">&#10005;</button></div>
    <div class="flota__cuerpo">@@RECURSOS@@</div>
    <div class="flota__pie"><span>Uso interno y confidencial.</span></div>
  </div>
</div>

<div class="velo" data-velo="teclas" role="dialog" aria-modal="true" aria-label="Atajos" hidden>
  <div class="flota" style="width:min(30rem,100%)">
    <div class="flota__cab"><h2>Cómo se usa</h2>
      <button class="icono" type="button" data-cerrar aria-label="Cerrar">&#10005;</button></div>
    <div class="flota__cuerpo">
      <dl class="tec">
        <dt><kbd>&#8984;K</kbd> &middot; <kbd>/</kbd></dt><dd>Buscar secciones, apartados y texto</dd>
        <dt><kbd>&#8594;</kbd> &middot; <kbd>&#8592;</kbd></dt><dd>Apartado siguiente y anterior dentro de la sección</dd>
        <dt><kbd>G</kbd></dt><dd>Volver al inicio</dd>
        <dt><kbd>R</kbd></dt><dd>Recursos y descargas</dd>
        <dt><kbd>?</kbd></dt><dd>Esta ventana</dd>
        <dt><kbd>Esc</kbd></dt><dd>Cerrar lo que esté abierto</dd>
      </dl>
      <p style="margin:1.5rem 0 0;font-size:.86rem;color:var(--ink-2);line-height:1.65">
        Pulsando una sección del índice se despliegan sus apartados. Dentro de una sección,
        <b>ningún enlace lleva fuera</b>: si un texto menciona algo que vive en otro documento, se
        queda como texto y no como una puerta que no abre. Las siglas subrayadas —@EJEMPLO@— abren
        su definición, que es la que está escrita en el Manual. Las figuras y las tablas anchas se
        ven de cerca pulsando encima.
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


def hoja_propia(doc, marca):
    for b in re.findall(r"<style>(.*?)</style>", fuente(doc), re.S):
        if marca in b:
            return b
    raise SystemExit("  %s: no se encuentra su hoja propia (%s)" % (doc, marca))


def main():
    secciones, menus, indice, orden, voces = monta()
    total = len(orden)
    inicio = sec_inicio(indice, total, voces)

    nav = ('<button type="button" data-ir-sec="inicio">Inicio</button>'
           + "".join('<button type="button" data-ir-sec="%s">%s</button>' % (i, H.escape(r))
                     for i, r, doc, _l, _n in SECCIONES if doc))

    recursos = (
        '<div class="rec__g"><p class="rec__t">La entrega</p>'
        + "".join(
            ('<div class="rec__i" style="opacity:.6"><em>%s</em><div><b>%s</b>'
             '<p>%s Es la que está viendo.</p></div></div>' % (k, H.escape(n), H.escape(q)))
            if r == "centro.html" else
            ('<a class="rec__i" href="%s"%s><em>%s</em><div><b>%s</b><p>%s</p></div></a>'
             % (r, " download" if d else "", k, H.escape(n), H.escape(q)))
            for r, k, n, q, d in ENTREGA)
        + '</div><div class="rec__g"><p class="rec__t">Los ocho documentos, por separado</p>'
        + "".join(
            '<a class="rec__i" href="%s"><em>%02d</em><div><b>%s</b><p>%s</p></div></a>'
            % (doc, n + 1, H.escape(nombre), H.escape(INTROS[i][0]))
            for n, (i, _r, doc, _l, nombre) in enumerate([s for s in SECCIONES if s[2]]))
        + '</div><div class="rec__g"><p class="rec__t">El glosario, entero</p>'
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

    cuerpo = (MARCO.replace("@@NAV@@", nav)
                   .replace("@@PANELES@@", "\n".join(menus))
                   .replace("@@SECCIONES@@", inicio + "\n" + "\n".join(secciones))
                   .replace("@@RECURSOS@@", recursos)
                   .replace("@EJEMPLO@", ", ".join(sorted(voces)[:3])))

    manual = fuente("manual.html")
    i = manual.index("<body>")
    cabecera = manual[:i + len("<body>")]
    cabecera = cabecera.replace("<title>Manual Maestro Giraldo</title>",
                                "<title>Centro de Excelencia Implantológica Giraldo</title>")
    cabecera = re.sub(
        r'<meta name="description" content="[^"]*">',
        '<meta name="description" content="Centro de Excelencia Implantológica Giraldo: la '
        'dirección, la presentación de Junta, los protocolos por puesto, la primera visita minuto '
        'a minuto, las operaciones, el marketing, los documentos de apoyo y los números. Ocho '
        'documentos y %d apartados, completos." >' % total, cabecera, count=1)
    extra = (CSS + "\n" + hoja_propia("protocolos.html", "PROTOCOLOS POR PUESTO")
             + "\n" + hoja_propia("instrumentos/captura.html", "HOJA DE CAPTURA")
             + "\n" + hoja_propia("deck.html", ".slide{"))
    k = cabecera.rindex("</style>")
    cabecera = cabecera[:k] + extra + "\n" + cabecera[k:]

    datos = ("<script>window.__ORDEN__ = "
             + json.dumps([[c, d, g, r, s] for c, d, g, r, s in orden], ensure_ascii=False)
             + ";\nwindow.__VOCES__ = " + json.dumps(voces, ensure_ascii=False)
             + ";\nwindow.__GRUPOESTADO__ = " + json.dumps(grupo_de, ensure_ascii=False)
             + ";</script>")

    salida = RAIZ / "centro.html"
    texto = (cabecera + "\n" + cuerpo + "\n" + datos + "\n" + JS + "\n</body>\n</html>\n")
    texto = texto.replace("@VERSION@", VERSION).replace("@FECHA@", FECHA)
    salida.write_text(texto, encoding="utf-8")

    # Ni un enlace muerto y ni un salto fuera de su sección: se comprueba aquí
    # mismo, que es donde se puede arreglar.
    # se mira el cuerpo, no los guiones: dentro del guion hay trozos de cadena
    # que parecen enlaces y no lo son
    cuerpo_html = re.sub(r"<script\b.*?</script>", "",
                         texto[texto.index('<div id="sitio">'):], flags=re.S)
    ids = set(re.findall(r'id="([^"]+)"', texto))
    muertos = sorted({h for h in re.findall(r'href="#([^"]+)"', cuerpo_html) if h not in ids})
    if muertos:
        raise SystemExit("  enlaces muertos en centro.html: %s" % ", ".join(muertos[:8]))

    print("centro.html · 9 secciones · %d apartados · %d KB"
          % (total, salida.stat().st_size // 1024))


if __name__ == "__main__":
    main()
