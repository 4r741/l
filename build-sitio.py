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
CLAVES_META = ("Momento", "Responsable", "Ubicación", "Herramienta", "KPI")


def meta_limpia(f):
    fuera, vistos = [], set()
    for k, v in f["meta"]:
        for c in CLAVES_META:
            if c.lower() in k.lower() and c not in vistos:
                vistos.add(c)
                fuera.append((k, v))
                break
    return fuera


def rol_jefe(f):
    return f["roles"][0] if f["roles"] else "director"


def pinta_reloj(fs, marca):
    """Los ciento veintitrés minutos, a escala y por dentro.

    Una lista de doce fases no dice cuál pesa. Una barra proporcional sí: se ve
    de un golpe que la propuesta económica dura tres veces lo que la acogida, y
    que el color cambia de manos cinco veces.
    """
    total = sum(f["min"] for f in fs)
    trozos, acumulado = [], 0
    for f in fs:
        pct = 100.0 * f["min"] / total
        trozos.append(
            '<button type="button" class="reloj__t" data-fase="%s%s" '
            'style="width:%.4f%%;--c:%s" title="%s · %d min">'
            '<span class="reloj__n">%02d</span>'
            '<span class="reloj__r">%s</span>'
            '<span class="reloj__m">%d′</span></button>'
            % (marca, f["id"], pct, COLOR_ROL.get(rol_jefe(f), "var(--accent)"),
               H.escape(f["label"] or f["titulo"]), f["min"],
               f["n"], H.escape(f["label"] or f["titulo"]), f["min"]))
        acumulado += f["min"]
    ejes = "".join(
        '<span style="left:%.4f%%">%d′</span>' % (100.0 * c / total, c)
        for c in (0, 30, 60, 90, total))
    return ('<div class="reloj" role="group" aria-label="Las doce fases a escala">'
            '<div class="reloj__barra">%s</div>'
            '<div class="reloj__eje">%s</div></div>' % ("".join(trozos), ejes))


def pinta_carriles(fs, marca):
    """Quién tiene al paciente en cada minuto. Cinco carriles, doce bloques."""
    total = sum(f["min"] for f in fs)
    usados = []
    for f in fs:
        for r in f["roles"]:
            if r not in usados:
                usados.append(r)
    filas = []
    for r in usados:
        bloques, x = [], 0.0
        for f in fs:
            an = 100.0 * f["min"] / total
            if r in f["roles"]:
                jefe = rol_jefe(f) == r
                bloques.append(
                    '<button type="button" class="carril__b%s" data-fase="%s%s" '
                    'style="left:%.4f%%;width:%.4f%%;--c:%s" title="%s · fase %02d">%s</button>'
                    % (" es-jefe" if jefe else "", marca, f["id"], x, an,
                       COLOR_ROL.get(r, "var(--accent)"),
                       H.escape(f["label"] or f["titulo"]), f["n"],
                       ("%02d" % f["n"]) if an > 4 else ""))
            x += an
        filas.append('<div class="carril"><p class="carril__q">%s</p>'
                     '<div class="carril__p">%s</div></div>'
                     % (H.escape(NOMBRE_ROL.get(r, r.title())), "".join(bloques)))
    return '<div class="carriles">%s</div>' % "".join(filas)


def ficha_fase(f, marca, doc, total):
    """El detalle de una fase: sus datos delante y su literatura entera debajo."""
    meta = "".join(
        '<div><dt>%s</dt><dd>%s</dd></div>' % (H.escape(k), H.escape(v))
        for k, v in meta_limpia(f))
    roles = "".join(
        '<span class="rolchip" style="--c:%s">%s</span>'
        % (COLOR_ROL.get(r, "var(--accent)"), H.escape(NOMBRE_ROL.get(r, r.title())))
        for r in f["roles"])
    return (
        '<article class="fase" id="%s%s" data-fase="%s%s" hidden>\n'
        '  <header class="fase__cab">\n'
        '    <p class="fase__n"><b>%02d</b> de %d · %s</p>\n'
        '    <h3>%s</h3>\n'
        '    <p class="fase__lede">%s</p>\n'
        '    <p class="fase__roles">%s<span class="fase__min">%d minutos</span></p>\n'
        '  </header>\n'
        '  <dl class="fase__meta">%s</dl>\n'
        '  <div class="fase__texto">%s</div>\n'
        '</article>'
        % (marca, f["id"], marca, f["id"], f["n"], total,
           H.escape(f["momento"] or "En consulta"),
           H.escape(f["titulo"]), H.escape(f["lede"]), roles, f["min"], meta, f["html"]))


def sec_primera_visita():
    """La primera visita: ciento veintitrés minutos, doce fases, cinco puestos."""
    fs = fases("index.html")
    fs = [dict(f, html=prefija(entabla(f["html"]), "pv-")) for f in fs]
    total = sum(f["min"] for f in fs)
    marca = "pv-"
    fichas = "\n".join(ficha_fase(f, marca, "index.html", len(fs)) for f in fs)
    tarjetas = "".join(
        '<button type="button" class="minif" data-fase="%s%s" style="--c:%s">'
        '<span class="minif__n">%02d</span>'
        '<span class="minif__r">%s</span>'
        '<span class="minif__q">%s</span>'
        '<span class="minif__m">%d′ · %s</span></button>'
        % (marca, f["id"], COLOR_ROL.get(rol_jefe(f), "var(--accent)"), f["n"],
           H.escape(f["label"] or f["titulo"]),
           H.escape((f["lede"] or "")[:96] + ("…" if len(f["lede"]) > 96 else "")),
           f["min"], H.escape(NOMBRE_ROL.get(rol_jefe(f), "")))
        for f in fs)
    return """
<section class="pag" id="primera-visita" data-pag="primera-visita">
  <header class="cabecera">
    <p class="eyebrow">La visita que decide</p>
    <h1>Ciento veintitrés minutos<em>que valen un tratamiento</em></h1>
    <p class="cabecera__p">Un paciente entra por la puerta sin saber qué le pasa y sale con un
      diagnóstico en la mano, un plan en tres dimensiones y una decisión que puede tomar. Entre
      una cosa y otra hay doce fases, cinco puestos que se pasan el testigo cinco veces y nueve
      documentos que quedan firmados. Nada de eso se improvisa: está escrito minuto a minuto y
      es lo que se audita.</p>
    <div class="cifrafila">
      <div><b>@PVTOTAL@′</b><span>de la llamada a la despedida</span></div>
      <div><b>12</b><span>fases encadenadas</span></div>
      <div><b>5</b><span>puestos que intervienen</span></div>
      <div><b>9</b><span>documentos firmados</span></div>
    </div>
  </header>

  <div class="bloque">
    <div class="bloque__cab">
      <h2>El reloj de la visita</h2>
      <p>Cada trozo es una fase y mide lo que dura de verdad. El color dice de quién es el
        paciente en ese tramo. Pulse cualquiera y se abre entera.</p>
    </div>
    @@RELOJ@@
    <div class="vistas">
      <button type="button" class="vista es-on" data-vista="tarjetas">Las doce fases</button>
      <button type="button" class="vista" data-vista="carriles">Quién tiene al paciente</button>
    </div>
    <div class="vista__p" data-vista="tarjetas">
      <div class="minifs">@@TARJETAS@@</div>
    </div>
    <div class="vista__p" data-vista="carriles" hidden>
      @@CARRILES@@
      <p class="pieaviso">Un carril lleno es un puesto con el paciente delante. El bloque en
        color pleno es de quien lleva la fase; el suave, de quien acompaña. Las cinco entregas
        del testigo —recepción a dirección, dirección a doctor, doctor a dirección, dirección a
        recepción— son los cinco puntos donde una primera visita se rompe.</p>
    </div>
  </div>

  <div class="bloque bloque--fase" id="pv-detalle">
    @@FICHAS@@
  </div>
</section>
""".replace("@@RELOJ@@", pinta_reloj(fs, marca)) \
   .replace("@@TARJETAS@@", tarjetas) \
   .replace("@@CARRILES@@", pinta_carriles(fs, marca)) \
   .replace("@@FICHAS@@", fichas) \
   .replace("@PVTOTAL@", str(total))


CLASE_RACI = {"R/A": "es-ra", "R": "es-r", "A": "es-a", "C": "es-c", "I": "es-i", "—": "es-no"}


def sec_puestos():
    """Los seis puestos: qué le toca a cada uno, fase por fase."""
    P = PERFILES
    botones, fichas = [], []
    for n, p in enumerate(P.PERFILES):
        raci = P.raci_de(p)
        activas = sum(1 for _f, papel in raci if papel != "—")
        botones.append(
            '<button type="button" class="selpuesto%s" data-puesto="%s" style="--c:%s">'
            '<b>%s</b><span>%d de 14 fases</span></button>'
            % (" es-on" if n == 0 else "", p["id"],
               COLOR_ROL.get(p["id"], "var(--accent)"), H.escape(p["corto"]), activas))

        celdas = "".join(
            '<div class="raci__c %s" title="%s · %s">'
            '<span class="raci__f">%02d</span><span class="raci__p">%s</span></div>'
            % (CLASE_RACI[papel], H.escape(fase), H.escape(P.QUE_ES[papel][0]), i + 1,
               H.escape(papel))
            for i, (fase, papel) in enumerate(raci))

        bloques = "".join(
            '<li><a href="#bib-%s"><span>%s</span>%s</a></li>'
            % (anc, "PR", H.escape(rot)) for rot, anc in p["bloques"]) or \
            '<li class="es-vacio">Su manual no se parte en procedimientos numerados: su trabajo '
        vang = "".join(
            '<li><a href="#bib-%s"><span>V</span>%s</a></li>' % (anc, H.escape(rot))
            for rot, anc in p["vanguardia"])

        fichas.append(
            '<article class="puesto" data-puesto="%s" style="--c:%s"%s>\n'
            '  <header class="puesto__cab">\n'
            '    <p class="eyebrow">Puesto %d de 6 · columna %s de la matriz</p>\n'
            '    <h3>%s</h3>\n'
            '    <p class="puesto__q">%s</p>\n'
            '  </header>\n'
            '  <div class="puesto__cifras">'
            '<div><b>%d</b><span>fases en las que interviene</span></div>'
            '<div><b>%d</b><span>procedimientos escritos</span></div>'
            '<div><b>%d</b><span>funciones de vanguardia</span></div></div>\n'
            '  <div class="puesto__raci">\n'
            '    <p class="rotulillo">Su papel en las catorce fases del recorrido</p>\n'
            '    <div class="raci">%s</div>\n'
            '    <p class="leyenda">%s</p>\n'
            '  </div>\n'
            '  <div class="puesto__cols">\n'
            '    <div><p class="rotulillo">Sus procedimientos</p><ul class="listilla">%s</ul></div>\n'
            '    <div><p class="rotulillo">Sus funciones de vanguardia</p><ul class="listilla">%s</ul></div>\n'
            '  </div>\n'
            '  <p class="puesto__ir"><a href="#bib-%s">Su manual completo, en la biblioteca &#8594;</a></p>\n'
            '</article>'
            % (p["id"], COLOR_ROL.get(p["id"], "var(--accent)"), "" if n == 0 else " hidden",
               n + 1, p.get("raci") or "—", H.escape(p["nombre"]), H.escape(p["que"]),
               activas, len(p["bloques"]), len(p["vanguardia"]), celdas,
               " · ".join("<b>%s</b> %s" % (k, H.escape(v[0])) for k, v in P.QUE_ES.items()),
               bloques, vang or '<li class="es-vacio">Ninguna propia: las suyas son de gobierno '
               'del sistema y están en su manual.</li>', p["manual"]))

    return """
<section class="pag" id="puestos" data-pag="puestos">
  <header class="cabecera">
    <p class="eyebrow">Qué se espera de cada uno</p>
    <h1>Seis puestos<em>y ninguna zona gris</em></h1>
    <p class="cabecera__p">La matriz RACI reparte las catorce fases del recorrido entre seis
      puestos. <b>R</b> ejecuta, <b>A</b> responde del resultado, <b>C</b> se consulta antes de
      decidir e <b>I</b> se informa después. Una fase sin A es una fase de la que no responde
      nadie: por eso no hay ninguna. Elija un puesto y verá lo suyo —dónde entra, con qué papel,
      qué tiene escrito y con qué se le mide— en un solo sitio.</p>
  </header>

  <div class="bloque">
    <div class="selector2">@@BOTONES@@</div>
    <div class="puestos">@@FICHAS@@</div>
  </div>
</section>
""".replace("@@BOTONES@@", "".join(botones)).replace("@@FICHAS@@", "\n".join(fichas))


COSTE_ROT = {"0": "No cuesta dinero", "€": "Hasta 1.000 €", "€€": "De 1 a 5 mil",
             "€€€": "De 5 a 15 mil", "€€€€": "Más de 15 mil"}
PLAZO_ROT = {"ya": "Ya", "trim": "Este trimestre", "año": "Este año",
             "estruct": "Cambia cómo trabajamos"}
SEM_ROT = {"verde": "Sin reservas", "amarillo": "Con cautela", "naranja": "Requiere criterio"}


def sec_marketing():
    """Los doce estados, las setenta y seis acciones y la cartera de campañas."""
    C = CATALOGO
    estados = "".join(
        '<button type="button" class="estado" data-estado="%s">'
        '<span class="estado__n">%s</span><b>%s</b><p>%s</p></button>'
        % (cod, cod, H.escape(nombre), H.escape(que))
        for cod, nombre, que in C["estados"])

    grupos = "".join(
        '<div class="grupom"><p class="grupom__n">%s · %s</p><b>%s</b><p>%s</p></div>'
        % (H.escape(cod), H.escape(estados_del), H.escape(nombre), H.escape(que))
        for cod, estados_del, nombre, que in C["grupos"])

    filas = "".join(
        '<tr data-grupo="%s" data-quien="%s" data-coste="%s" data-plazo="%s" data-sem="%s">'
        '<td class="acc__cod">%s</td>'
        '<td class="acc__q"><b>%s</b><span>%s</span></td>'
        '<td class="acc__gana">%s</td>'
        '<td class="acc__meta"><span class="etq">%s</span><span class="etq">%s</span>'
        '<span class="etq etq--%s">%s</span></td>'
        '<td class="acc__ef"><span class="barrita" style="--v:%d%%"></span>%d</td></tr>'
        % (a["grupo"], a["quien"], a["coste"], a["plazo"], a["sem"],
           a["cod"], H.escape(a["accion"]), H.escape(a["indicador"]),
           H.escape(a["gana"]),
           H.escape(COSTE_ROT.get(a["coste"], a["coste"])),
           H.escape(PLAZO_ROT.get(a["plazo"], a["plazo"])),
           a["sem"], H.escape(SEM_ROT.get(a["sem"], a["sem"])),
           20 * a["efecto"], a["efecto"])
        for a in C["acciones"])

    def opciones(nombre, pares):
        return ('<label class="filtro"><span>%s</span><select data-filtro="%s">'
                '<option value="">Todos</option>%s</select></label>'
                % (nombre, nombre.lower().replace(" ", "-"),
                   "".join('<option value="%s">%s</option>' % (v, H.escape(r)) for v, r in pares)))

    filtros = (
        opciones("grupo", [(g[0], "%s · %s" % (g[0], g[2])) for g in C["grupos"]])
        + opciones("quien", sorted((k, k) for k in C["por_puesto"]))
        + opciones("coste", [(k, COSTE_ROT.get(k, k)) for k in ("0", "€", "€€", "€€€", "€€€€")])
        + opciones("plazo", [(k, PLAZO_ROT[k]) for k in ("ya", "trim", "año", "estruct")])
        + opciones("sem", [(k, SEM_ROT[k]) for k in ("verde", "amarillo", "naranja")]))

    camp = "".join(
        '<article class="campana"><header><p class="eyebrow">%s</p><h4>%s</h4></header>'
        '<p class="campana__r">%s</p>'
        '<dl class="campana__c"><div><dt>Aporta</dt><dd>%s €</dd></div>'
        '<div><dt>Cuesta</dt><dd>%s €</dd></div>'
        '<div><dt>Por cada euro</dt><dd>%s €</dd></div></dl></article>'
        % (H.escape(c["cod"]), H.escape(c["nombre"]), H.escape(c.get("razon", "")),
           "{:,}".format(int(c.get("aporta") or sum(p[1] for p in c.get("partes", [])))).replace(",", "."),
           "{:,}".format(int(c["coste"])).replace(",", "."),
           ("%.1f" % ((c.get("aporta") or sum(p[1] for p in c.get("partes", []))) / c["coste"])).replace(".", ","))
        for c in CAMPANAS["campanas"])

    return """
<section class="pag" id="marketing" data-pag="marketing">
  <header class="cabecera">
    <p class="eyebrow">Cómo llega el paciente</p>
    <h1>Setenta y seis acciones<em>y treinta y dos que no cuestan dinero</em></h1>
    <p class="cabecera__p">El paciente no recorre un embudo: recorre estados, y los recorre en
      los dos sentidos. Un embudo termina en la venta; una persona, no. Aquí están los doce
      estados, las acciones que actúan sobre cada uno —con dueño, con coste, con plazo y con el
      número que se mueve si funciona— y la cartera de campañas con sus cifras. La regla de
      entrada es una sola: una acción entra si puede declarar en una línea <b>qué gana el
      paciente</b>. No qué ganamos nosotros.</p>
    <div class="cifrafila">
      <div><b>@ACCIONES@</b><span>acciones con dueño</span></div>
      <div><b>@SINCOSTE@</b><span>no cuestan dinero</span></div>
      <div><b>@INMEDIATAS@</b><span>se pueden hacer ya</span></div>
      <div><b>12</b><span>estados del paciente</span></div>
    </div>
  </header>

  <div class="bloque">
    <div class="bloque__cab"><h2>Los doce estados</h2>
      <p>Pulse uno y la tabla de abajo se queda con lo que actúa sobre él.</p></div>
    <div class="estados">@@ESTADOS@@</div>
    <div class="gruposm">@@GRUPOS@@</div>
  </div>

  <div class="bloque">
    <div class="bloque__cab"><h2>Las setenta y seis acciones</h2>
      <p>Con dueño, coste, plazo, efecto esperado y el indicador que las delata. Se filtran.</p></div>
    <div class="filtros">@@FILTROS@@
      <button type="button" class="limpiar" id="limpiafiltros">Quitar filtros</button>
      <span class="cuentafiltro" id="cuentaacc"></span>
    </div>
    <div class="tablawrap">
      <table class="acciones" id="tablaacciones">
        <thead><tr><th>Cód.</th><th>Qué se hace y qué mueve</th><th>Qué gana el paciente</th>
          <th>Coste · plazo · marco</th><th>Efecto</th></tr></thead>
        <tbody>@@FILAS@@</tbody>
      </table>
    </div>
  </div>

  <div class="bloque">
    <div class="bloque__cab"><h2>La cartera de campañas</h2>
      <p>Ninguna cifra está escrita a mano: todas salen del modelo, y el criterio es el
        conservador —una campaña vale la diferencia entre el paciente que trae y el que
        desplaza, no lo que factura.</p></div>
    <div class="campanas">@@CAMPANAS@@</div>
  </div>
</section>
""".replace("@@ESTADOS@@", estados).replace("@@GRUPOS@@", grupos) \
   .replace("@@FILTROS@@", filtros).replace("@@FILAS@@", filas) \
   .replace("@@CAMPANAS@@", camp) \
   .replace("@ACCIONES@", str(C["total"])).replace("@SINCOSTE@", str(C["sin_coste"])) \
   .replace("@INMEDIATAS@", str(C["inmediatas"]))


def trae(doc, ancla, marca):
    """Un trozo de literatura, entero y listo para vivir aquí."""
    return prefija(entabla(pieza(doc, ancla)), marca)


def sec_protocolos():
    """El recorrido completo, los procedimientos por puesto y lo que se verifica."""
    fs = fases("manual.html")
    total = sum(f["min"] for f in fs if f["min"]) or 1
    mapa = "".join(
        '<button type="button" class="mfase" data-fase="mf-%s" style="--c:%s">'
        '<span class="mfase__n">%02d</span><b>%s</b>'
        '<span class="mfase__r">%s</span></button>'
        % (f["id"], COLOR_ROL.get(rol_jefe(f), "var(--accent)"), f["n"],
           H.escape(f["label"] or f["titulo"]),
           H.escape(NOMBRE_ROL.get(rol_jefe(f), "")))
        for f in fs)
    fichas = "\n".join(
        ficha_fase(dict(f, html=prefija(entabla(f["html"]), "mf-")), "mf-", "manual.html", len(fs))
        for f in fs)

    P = PERFILES
    porPuesto = "".join(
        '<article class="proc" style="--c:%s"><header><b>%s</b>'
        '<span>%d procedimientos · %d de vanguardia</span></header><ol>%s</ol></article>'
        % (COLOR_ROL.get(p["id"], "var(--accent)"), H.escape(p["nombre"]),
           len(p["bloques"]), len(p["vanguardia"]),
           "".join('<li><a href="#bib-%s">%s</a></li>' % (a, H.escape(r))
                   for r, a in p["bloques"]) or "<li class=\"es-vacio\">En su manual, sin numerar</li>")
        for p in P.PERFILES)

    docs = trae("otros.html", "o-cada-cosa-cuando-abre", "pr-")
    verif = trae("otros.html", "o-protocolo-maestro-verificacion-322-puntos-control", "pr-")
    return """
<section class="pag" id="protocolos" data-pag="protocolos">
  <header class="cabecera">
    <p class="eyebrow">El documento troncal</p>
    <h1>Catorce fases<em>y nadie improvisa ninguna</em></h1>
    <p class="cabecera__p">De la primera llamada al mantenimiento a largo plazo. Cada fase
      construye sobre la anterior: la información recogida en la llamada personaliza la
      recepción, la anamnesis alimenta la presentación y el cierre abre el circuito de
      producción. La cadena es tan fuerte como su eslabón más débil, y por eso ninguna fase se
      salta «por falta de tiempo».</p>
  </header>

  <div class="bloque">
    <div class="bloque__cab"><h2>El recorrido completo</h2>
      <p>Las doce primeras son la primera visita. La trece ejecuta lo vendido; la catorce es la
        que da coherencia al nombre del centro.</p></div>
    <div class="mapa">@@MAPA@@</div>
  </div>

  <div class="bloque bloque--fase" id="mf-detalle">@@FICHAS@@</div>

  <div class="bloque">
    <div class="bloque__cab"><h2>Los procedimientos, por puesto</h2>
      <p>Lo que cada uno tiene escrito, numerado y citable. Pulse para leerlo entero.</p></div>
    <div class="procs">@@PROCS@@</div>
  </div>

  <div class="bloque bloque--texto">
    <div class="bloque__cab"><h2>Qué se verifica, y cada cuánto</h2></div>
    @@VERIF@@
  </div>

  <div class="bloque bloque--texto">
    <div class="bloque__cab"><h2>Los catorce documentos de apoyo</h2>
      <p>Qué es cada cosa y cuándo se abre.</p></div>
    @@DOCS@@
  </div>
</section>
""".replace("@@MAPA@@", mapa).replace("@@FICHAS@@", fichas) \
   .replace("@@PROCS@@", porPuesto).replace("@@VERIF@@", verif).replace("@@DOCS@@", docs)


def sec_gtc():
    """Giraldo Te Cuida: el programa que convierte «le cuidamos» en revisiones."""
    c1 = [c for c in CAMPANAS["campanas"] if c["cod"] == "C1"]
    c1 = c1[0] if c1 else {"coste": 6000, "partes": []}
    aporta = int(c1.get("aporta") or sum(p[1] for p in c1.get("partes", [])))
    partes = "".join(
        '<div class="gtcp"><b>%s €</b><p class="gtcp__q">%s</p><p class="gtcp__c">%s</p></div>'
        % ("{:,}".format(int(v)).replace(",", "."), H.escape(k), H.escape(por))
        for k, v, por in c1.get("partes", []))
    texto = trae("otros.html", "o-gtc-giraldo-te-cuida", "gtc-")
    return """
<section class="pag" id="gtc" data-pag="gtc">
  <header class="cabecera cabecera--gtc">
    <p class="eyebrow">El programa de cuidado</p>
    <h1>Giraldo Te Cuida<em>«y le cuidamos para siempre» deja de ser una frase</em></h1>
    <p class="cabecera__p">La promesa del centro tiene dos mitades. La primera es el resultado y
      la fija el posicionamiento: ningún tratamiento se deja a medias. La segunda es la relación,
      y una relación sin instrumento es una intención. El instrumento se llama GTC: una cuota
      anual, unas revisiones que ocurren de verdad y un informe que se entrega en persona.</p>
    <div class="cifrafila">
      <div><b>@APORTA@ €</b><span>que produce al año</span></div>
      <div><b>@COSTE@ €</b><span>que cuesta ponerlo en pie</span></div>
      <div><b>@RATIO@ €</b><span>por cada euro invertido</span></div>
      <div><b>0</b><span>huecos de primera visita que ocupa</span></div>
    </div>
  </header>

  <div class="bloque">
    <div class="bloque__cab"><h2>De dónde sale su cifra</h2>
      <p>No de una previsión: de dos partidas que se pueden contar por separado.</p></div>
    <div class="gtcps">@@PARTES@@</div>
  </div>

  <div class="bloque bloque--texto">@@TEXTO@@</div>
</section>
""".replace("@@PARTES@@", partes).replace("@@TEXTO@@", texto) \
   .replace("@APORTA@", "{:,}".format(aporta).replace(",", ".")) \
   .replace("@COSTE@", "{:,}".format(int(c1["coste"])).replace(",", ".")) \
   .replace("@RATIO@", ("%.1f" % (aporta / c1["coste"])).replace(".", ","))


def sec_numeros():
    """Los diez indicadores, los cinco números que faltan y el puente hasta 1,2 M€."""
    P = CAMPANAS["puente"]
    cap = CAMPANAS["capacidad"]
    tramos = [("Punto de partida", P["base"], "var(--muted)"),
              ("Llenar la agenda", P["llenar"], "var(--rol-recepcion)"),
              ("Mejor mezcla de casos", P["mezcla"], "var(--rol-doctor)"),
              ("Seguimiento y cuidado", P["seguimiento"], "var(--accent)")]
    tope = P["planificado"]
    barras, acumulado = [], 0
    for rot, valor, color in tramos:
        barras.append(
            '<div class="puente__t" style="--w:%.3f%%;--c:%s">'
            '<span class="puente__r">%s</span>'
            '<span class="puente__v">%s €</span></div>'
            % (100.0 * valor / tope, color, H.escape(rot),
               "{:,}".format(int(valor)).replace(",", ".")))
        acumulado += valor

    cinco = trae("memoria.html", "t-cinco-numeros-aun-no-tenemos", "nu-")
    indic = trae("instrumentos/captura.html", "c-cuenta-arriba-cuenta-abajo", "nu-")
    return """
<section class="pag" id="numeros" data-pag="numeros">
  <header class="cabecera">
    <p class="eyebrow">El instrumento que mide</p>
    <h1>De 720.000 €<em>a 1,2 millones, bloque a bloque</em></h1>
    <p class="cabecera__p">Un objetivo sin un puente que lo sostenga es un deseo. Este se
      construye con tres bloques que se pueden contar por separado y auditar uno a uno, sobre un
      punto de partida heredado. Y con una advertencia escrita en el propio plan: cinco de los
      números que lo sostienen todavía no se tienen, y hasta que se tengan son supuestos de
      trabajo marcados como tales.</p>
    <div class="cifrafila">
      <div><b>@PVANO@</b><span>primeras visitas al año de capacidad</span></div>
      <div><b>@PVLIBRES@</b><span>huecos libres para campañas</span></div>
      <div><b>@VALOR@ €</b><span>valor medio de una primera visita</span></div>
      <div><b>@COLCHON@ %</b><span>de colchón sobre el objetivo</span></div>
    </div>
  </header>

  <div class="bloque">
    <div class="bloque__cab"><h2>El puente, a escala</h2>
      <p>Cada bloque mide lo que aporta. Ninguno está escrito a mano: salen del modelo.</p></div>
    <div class="puente">@@BARRAS@@
      <p class="puente__pie">Planificado <b>@PLANIFICADO@ €</b> · objetivo <b>@OBJETIVO@ €</b>
        · colchón <b>@COLCHONE@ €</b></p>
    </div>
  </div>

  <div class="bloque bloque--texto">
    <div class="bloque__cab"><h2>Los cinco números que aún no tenemos</h2></div>
    @@CINCO@@
  </div>

  <div class="bloque bloque--texto">
    <div class="bloque__cab"><h2>Qué se cuenta, y qué se deriva</h2></div>
    @@INDIC@@
  </div>
</section>
""".replace("@@BARRAS@@", "".join(barras)).replace("@@CINCO@@", cinco).replace("@@INDIC@@", indic) \
   .replace("@PVANO@", "{:,}".format(int(cap["pv_ano"])).replace(",", ".")) \
   .replace("@PVLIBRES@", "{:,}".format(int(cap["pv_libres"])).replace(",", ".")) \
   .replace("@VALOR@", str(int(cap["valor_base"]))) \
   .replace("@COLCHON@", ("%.1f" % (100 * P["colchon_pct"])).replace(".", ",")) \
   .replace("@PLANIFICADO@", "{:,}".format(int(P["planificado"])).replace(",", ".")) \
   .replace("@OBJETIVO@", "{:,}".format(int(P["objetivo"])).replace(",", ".")) \
   .replace("@COLCHONE@", "{:,}".format(int(abs(P["colchon"]))).replace(",", "."))


ENTRADAS = [
    ("primera-visita", "La primera visita", "La visita que decide",
     "Ciento veintitrés minutos, doce fases y cinco puestos que se pasan el testigo.",
     "M12 4 L12 20 M4 12 L20 12"),
    ("puestos", "Los puestos", "Qué se espera de cada uno",
     "Seis puestos, catorce fases y ninguna zona gris: elija el suyo y vea lo que le toca.",
     "M4 20 L4 8 L12 4 L20 8 L20 20"),
    ("protocolos", "Los protocolos", "El documento troncal",
     "El recorrido completo, los procedimientos por puesto y los 322 puntos que se verifican.",
     "M6 4 H18 V20 H6 Z M9 9 H15 M9 13 H15"),
    ("marketing", "El marketing", "Cómo llega el paciente",
     "Doce estados, setenta y seis acciones con dueño y la cartera de campañas con sus cifras.",
     "M4 18 L9 11 L14 15 L20 6"),
    ("gtc", "Giraldo Te Cuida", "El programa de cuidado",
     "El instrumento que convierte «le cuidamos para siempre» en revisiones que ocurren.",
     "M12 20 C6 15 4 12 4 9 A4 4 0 0 1 12 8 A4 4 0 0 1 20 9 C20 12 18 15 12 20 Z"),
    ("numeros", "Los números", "El instrumento que mide",
     "El puente de 720.000 € a 1,2 M€, los diez indicadores y los cinco que faltan.",
     "M5 19 V10 M11 19 V5 M17 19 V13"),
    ("biblioteca", "La biblioteca", "Todo el sistema, completo",
     "Los ocho documentos y sus 135 apartados, con índice completo, buscador y glosario.",
     "M5 5 H11 V19 H5 Z M13 5 H19 V19 H13 Z"),
]


def sec_inicio():
    tarjetas = "".join(
        '<button type="button" class="entrada" data-ir-pag="%s">'
        '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="%s"/></svg>'
        '<p class="entrada__k">%s</p><b>%s</b><p class="entrada__q">%s</p>'
        '<span class="entrada__f">Entrar &#8594;</span></button>'
        % (i, d, H.escape(k), H.escape(rot), H.escape(q))
        for i, rot, k, q, d in ENTRADAS)
    return """
<section class="pag" id="inicio" data-pag="inicio">
  <div class="hero">
    <div class="hero__t">
      <p class="eyebrow">Centro de Excelencia Implantológica Giraldo · Rúa Bolivia nº 2 · Vigo</p>
      <h1>No medias<em>sonrisas</em></h1>
      <p class="hero__p">«Le devolvemos su sonrisa completa, en el menor tiempo posible, y le
        cuidamos para siempre.»</p>
      <p class="hero__s">La primera mitad es el resultado: ningún tratamiento se deja a medias.
        La segunda es la relación, y tiene instrumento propio. Todo lo que hay debajo de esas dos
        frases —lo que se cree, lo que se decide y cómo se ejecuta, minuto a minuto y puesto a
        puesto— está aquí, completo y sin atajos.</p>
      <div class="hero__b">
        <button type="button" class="bt bt--fuerte" data-ir-pag="primera-visita">Ver la primera visita</button>
        <button type="button" class="bt" data-abre="paleta">Buscar en todo el sistema</button>
      </div>
    </div>
    <div class="hero__c">
      <div><b>8</b><span>documentos</span></div>
      <div><b>@TOTAL@</b><span>apartados</span></div>
      <div><b>14</b><span>fases del recorrido</span></div>
      <div><b>6</b><span>puestos</span></div>
      <div><b>@ACC@</b><span>acciones de marketing</span></div>
      <div><b>322</b><span>puntos de verificación</span></div>
      <div><b>1,2 M€</b><span>objetivo del tercer ejercicio</span></div>
      <div><b>@VOCES@</b><span>voces de glosario</span></div>
    </div>
  </div>

  <div class="bloque">
    <div class="bloque__cab"><h2>Por dónde se entra</h2>
      <p>Siete puertas. Ninguna es un resumen: todas llevan al detalle completo.</p></div>
    <div class="entradas">@@TARJETAS@@</div>
  </div>
</section>
""".replace("@@TARJETAS@@", tarjetas).replace("@ACC@", str(CATALOGO["total"]))
def monta():
    hojas, arbol, indice, orden, cuentas = [], [], [], [], []
    todos_ids = {}
    crudos = []

    # 1 · recoger, prefijar y quedarse con el mapa de identificadores
    voces = glosario()
    # de la más larga a la más corta: si no, «RAC» se comería «RACI»
    orden_voces = sorted(voces, key=len, reverse=True)
    anclas_glosario = {a for _d, a, _p in GLOSARIOS}

    for n, (doc, rotulo, clase, que, marca) in enumerate(DOCUMENTOS):
        piezas = recoge(doc)
        pre = marca + "-"
        for p in piezas:
            cuerpo = entabla(p["html"])
            if not any(('id="%s"' % a) in cuerpo for a in anclas_glosario):
                cuerpo = marca_glosario(cuerpo, voces, orden_voces)
            p["html"] = prefija(cuerpo, pre)
            p["clave"] = pre + p["id"]
            p["doc"] = n
            for ident in re.findall(r'id="([^"]+)"', p["html"]):
                todos_ids.setdefault(ident[len(pre):], ident)
                todos_ids.setdefault(ident, ident)
            todos_ids.setdefault(p["id"], p["clave"])
        crudos.append((doc, rotulo, clase, que, pre, piezas))

    # 2 · coser los enlaces: aquí está todo, así que casi nada sale fuera
    docs_re = "|".join(re.escape(d) for d, *_ in DOCUMENTOS) + "|inicio.html"

    def local(destino, pre):
        return todos_ids.get(pre + destino) or todos_ids.get(destino)

    for doc, rotulo, clase, que, pre, piezas in crudos:
        for p in piezas:
            def propio(m, pre=pre):
                d = local(m.group(1), pre)
                return 'href="#%s"' % d if d else 'href="#%s" class="fuera"' % m.group(1)

            def ajeno(m, pre=pre):
                d = local(m.group(2), pre)
                return 'href="#%s"' % d if d else 'href="%s#%s" class="fuera"' % (m.group(1), m.group(2))

            p["html"] = re.sub(r'href="#([^"]+)"', propio, p["html"])
            p["html"] = re.sub(r'href="(%s)#([^"]+)"(?: class="fuera")?' % docs_re, ajeno, p["html"])
            p["html"] = re.sub(r'href="(%s)"' % docs_re,
                               lambda m: 'href="%s" class="fuera"' % m.group(1), p["html"])

    # 3 · las hojas, el árbol del lado y el índice completo de la portada
    for n, (doc, rotulo, clase, que, pre, piezas) in enumerate(crudos):
        nn = "%02d" % (n + 1)
        ramas, filas, grupo_abierto = [], [], None
        for p in piezas:
            orden.append((p["clave"], rotulo, p["grupo"], p["rotulo"]))
            titulares = [sin_marcas(x) for x in
                         re.findall(r"<h[23][^>]*>(.*?)</h[23]>", p["html"], re.S)]
            titulares = [x for x in titulares if x and x != p["rotulo"]][:14]

            if p["grupo"] != grupo_abierto:
                grupo_abierto = p["grupo"]
                if p["grupo"]:
                    ramas.append('<p class="lado__gt">%s</p>' % H.escape(p["grupo"]))
                    filas.append('<p class="idx__gt">%s</p>' % H.escape(p["grupo"]))
            ramas.append('<a href="#%s" data-ir="%s"><span>%s</span>%s</a>'
                         % (p["clave"], p["clave"], H.escape(p["n"] or "·"), H.escape(p["rotulo"])))
            filas.append(
                '<div class="idx__ap"><a href="#%s" data-ir="%s">'
                '<span>%s</span><b>%s</b></a>%s</div>'
                % (p["clave"], p["clave"], H.escape(p["n"] or "·"), H.escape(p["rotulo"]),
                   ('<p class="idx__t">%s</p>' % " · ".join(H.escape(x) for x in titulares))
                   if titulares else ""))

            hojas.append(
                '<article class="hoja" id="%s" data-hoja="%s" data-doc="%d" data-n="%s">\n'
                '  <p class="hoja__de"><span>%s</span> %s%s</p>\n'
                '%s\n'
                '  <div class="remate">\n'
                '    <button class="marca-leido" type="button" data-hoja="%s" aria-pressed="false">'
                '<b>Marcar leído</b></button>\n'
                '    %s\n'
                '  </div>\n</article>'
                % (p["clave"], p["clave"], n, H.escape(p["n"] or ""), nn, H.escape(rotulo),
                   " · " + H.escape(p["grupo"]) if p["grupo"] else "", p["html"], p["clave"],
                   "@@SIGUIENTE:%s@@" % p["clave"]))

        cuentas.append(len(piezas))
        arbol.append(
            '<details class="lado__doc" data-doc="%d"%s>\n'
            '  <summary><b>%s</b><span>%s</span>'
            '<i title="%d apartados"><svg class="aro" width="16" height="16" viewBox="0 0 16 16" '
            'aria-hidden="true"><circle class="aro__f" cx="8" cy="8" r="6.2"/>'
            '<circle class="aro__v" cx="8" cy="8" r="6.2" stroke-dasharray="39" '
            'stroke-dashoffset="39"/></svg></i></summary>\n'
            '  <div class="lado__ramas">%s</div>\n</details>'
            % (n, " open" if n == 0 else "", nn, H.escape(rotulo), len(piezas), "".join(ramas)))
        indice.append(
            '<section class="idx__doc">\n'
            '  <header class="idx__cab"><p class="eyebrow">%s · %d apartados</p>'
            '<h3><span>%s</span>%s</h3><p>%s</p></header>\n'
            '  <div class="idx__lista">%s</div>\n</section>'
            % (H.escape(clase), len(piezas), nn, H.escape(rotulo), H.escape(que), "".join(filas)))

    # El pie de cada apartado nombra el siguiente: dice adónde lleva y no
    # obliga a subir a la barra para seguir leyendo. Se resuelve al final,
    # cuando ya se sabe el orden completo de los ciento treinta y cinco.
    porOrden = {c: (i, d, g, r) for i, (c, d, g, r) in enumerate(orden)}
    for i, h in enumerate(hojas):
        clave = re.search(r'data-hoja="([^"]+)"', h).group(1)
        pos = porOrden[clave][0]
        if pos + 1 < len(orden):
            c2, d2, g2, r2 = orden[pos + 1]
            enlace = ('<a href="#%s"><i>Sigue</i> %s<span style="color:var(--muted)"> · %s</span></a>'
                      % (c2, H.escape(r2), H.escape(d2)))
        else:
            enlace = '<a href="#portada"><i>Final</i> Volver al índice completo</a>'
        hojas[i] = h.replace("@@SIGUIENTE:%s@@" % clave, enlace)

    return hojas, arbol, indice, orden, cuentas, todos_ids




CSS = """
/* ===========================================================================
   EL CENTRO GIRALDO · EL SITIO

   Siete puertas y una biblioteca. Cada sección está construida para lo que
   cuenta: la primera visita es una línea de tiempo porque son ciento veintitrés
   minutos; los puestos, una matriz, porque son seis por catorce; el marketing,
   una tabla que se filtra, porque son setenta y seis acciones. Nada de cajas
   dentro de cajas: aire, una regla de un píxel y el color justo para señalar
   de quién es el paciente en cada tramo.
   =========================================================================== */
:root{
  --nav:3.4rem; --texto:70ch; --ancho:82rem;
  --sombra-flota:0 18px 50px -12px rgba(18,35,43,.28), 0 2px 8px rgba(18,35,43,.08);
  --e:cubic-bezier(.2,.7,.3,1);
}
body{background:var(--paper)}
*:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:3px}
.avance{position:fixed;inset:0 auto auto 0;height:2px;width:0;background:var(--accent);
  z-index:70;transition:width .12s linear}

/* --- la barra de arriba: la única navegación permanente ------------------ */
.nav{
  position:sticky;top:0;z-index:50;height:var(--nav);display:flex;align-items:center;gap:1.4rem;
  padding:0 1.6rem;background:rgba(246,248,249,.9);backdrop-filter:saturate(1.5) blur(10px);
  border-bottom:1px solid var(--line-soft);
}
.nav__m{display:flex;align-items:baseline;gap:.5rem;text-decoration:none;color:var(--tinta);
  font-family:var(--f-display);font-size:1rem;font-weight:500;letter-spacing:-.012em;flex:none}
.nav__m b{font-weight:600}
.nav__m span{font-family:var(--f-mono);font-size:.6rem;letter-spacing:.13em;
  text-transform:uppercase;color:var(--muted)}
.nav__l{display:flex;gap:.15rem;flex:1;min-width:0;overflow-x:auto;scrollbar-width:none}
.nav__l::-webkit-scrollbar{display:none}
.nav__l button{
  font:inherit;font-size:.85rem;cursor:pointer;border:0;background:none;color:var(--ink-2);
  padding:.4rem .7rem;border-radius:7px;white-space:nowrap;
}
.nav__l button:hover{background:var(--surface);color:var(--ink)}
.nav__l button.es-on{background:var(--tinta);color:#fff}
.nav__b{display:flex;gap:.35rem;flex:none;align-items:center}
.abrepal{
  display:flex;align-items:center;gap:.5rem;padding:.38rem .6rem .38rem .7rem;
  background:var(--surface);border:1px solid var(--line-soft);border-radius:7px;
  color:var(--muted);font:inherit;font-size:.82rem;cursor:pointer;
}
.abrepal:hover{border-color:var(--line);color:var(--ink-2)}
.abrepal kbd{font-family:var(--f-mono);font-size:.6rem;background:var(--surface-2);
  border:1px solid var(--line-soft);border-radius:4px;padding:.12rem .3rem;line-height:1}
.icono{
  font:inherit;cursor:pointer;display:inline-flex;align-items:center;justify-content:center;
  width:1.9rem;height:1.9rem;border-radius:6px;border:1px solid transparent;background:none;
  color:var(--muted);line-height:1;
}
.icono:hover:not(:disabled){background:var(--surface);border-color:var(--line-soft);color:var(--ink)}
.icono:disabled{opacity:.3;cursor:default}

/* --- las páginas --------------------------------------------------------- */
.pag{max-width:var(--ancho);margin:0 auto;padding:3.4rem 1.8rem 7rem}
.sitio--vivo .pag{display:none}
.sitio--vivo .pag.es-on{display:block;animation:entrada .22s var(--e)}
@keyframes entrada{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
@media(prefers-reduced-motion:reduce){.sitio--vivo .pag.es-on{animation:none}}

.cabecera{max-width:60rem;padding-bottom:2.6rem;margin-bottom:3.2rem;border-bottom:1px solid var(--line)}
.cabecera h1{
  font-size:clamp(2.4rem,5.4vw,4.1rem);line-height:1.03;letter-spacing:-.032em;margin:1rem 0 0;
}
.cabecera h1 em{font-style:normal;color:var(--accent);display:block}
.cabecera__p{margin:1.6rem 0 0;font-size:1.06rem;line-height:1.68;color:var(--ink-2);max-width:64ch}
.cabecera__p b{color:var(--tinta);font-weight:600}
.cifrafila{display:flex;flex-wrap:wrap;gap:2.4rem;margin-top:2.4rem}
.cifrafila b{display:block;font-family:var(--f-display);font-size:1.75rem;letter-spacing:-.02em;
  color:var(--tinta)}
.cifrafila span{display:block;margin-top:.25rem;font-family:var(--f-mono);font-size:.62rem;
  letter-spacing:.13em;text-transform:uppercase;color:var(--muted)}

.bloque{margin-bottom:4.4rem}
.bloque__cab{margin-bottom:1.8rem;max-width:58rem}
.bloque__cab h2{font-size:clamp(1.4rem,2.6vw,1.95rem);letter-spacing:-.022em;margin:0}
.bloque__cab p{margin:.55rem 0 0;color:var(--ink-2);line-height:1.62;max-width:62ch}
.rotulillo{font-family:var(--f-mono);font-size:.61rem;letter-spacing:.15em;text-transform:uppercase;
  color:var(--muted);margin:0 0 .8rem}
.bloque--texto .wrap{padding:0;max-width:none}
.bloque--texto .section{padding:0;background:none;border:0}
.bloque--texto{max-width:var(--texto)}
.pieaviso{margin:1.4rem 0 0;font-size:.88rem;line-height:1.6;color:var(--muted);max-width:64ch}

/* --- portada ------------------------------------------------------------- */
.hero{
  display:grid;grid-template-columns:minmax(0,1.25fr) minmax(0,1fr);gap:3.6rem;align-items:end;
  padding:3.4rem 0 3.6rem;border-bottom:1px solid var(--line);margin-bottom:3.6rem;
}
.hero h1{font-size:clamp(3rem,7.6vw,6rem);line-height:.98;letter-spacing:-.038em;margin:1.2rem 0 0}
.hero h1 em{font-style:normal;color:var(--accent);display:block}
.hero__p{margin:2rem 0 0;font-family:var(--f-display);font-size:clamp(1.1rem,2.1vw,1.45rem);
  line-height:1.42;color:var(--tinta);max-width:32ch}
.hero__s{margin:1.2rem 0 0;color:var(--ink-2);line-height:1.66;max-width:54ch}
.hero__b{display:flex;flex-wrap:wrap;gap:.6rem;margin-top:2rem}
.bt{font:inherit;font-size:.9rem;cursor:pointer;border-radius:999px;padding:.62rem 1.25rem;
  border:1px solid var(--line);background:var(--surface);color:var(--ink-2)}
.bt:hover{border-color:var(--accent);color:var(--accent-ink)}
.bt--fuerte{background:var(--tinta);border-color:var(--tinta);color:#fff;font-weight:500}
.bt--fuerte:hover{background:var(--accent-fuerte);border-color:var(--accent-fuerte);color:#fff}
.hero__c{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1.4rem 2rem}
.hero__c b{display:block;font-family:var(--f-display);font-size:1.55rem;letter-spacing:-.02em;
  color:var(--accent-ink)}
.hero__c span{display:block;margin-top:.15rem;font-family:var(--f-mono);font-size:.6rem;
  letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}

.entradas{display:grid;grid-template-columns:repeat(auto-fill,minmax(17rem,1fr));gap:1px;
  background:var(--line);border:1px solid var(--line);border-radius:12px;overflow:hidden}
.entrada{
  font:inherit;text-align:left;cursor:pointer;border:0;background:var(--surface);
  padding:1.7rem 1.6rem 1.5rem;display:flex;flex-direction:column;gap:.15rem;
  transition:background .16s var(--e);
}
.entrada:hover{background:var(--surface-2)}
.entrada svg{width:22px;height:22px;fill:none;stroke:var(--accent);stroke-width:1.6;
  stroke-linecap:round;stroke-linejoin:round;margin-bottom:1rem}
.entrada__k{margin:0;font-family:var(--f-mono);font-size:.6rem;letter-spacing:.14em;
  text-transform:uppercase;color:var(--muted)}
.entrada b{font-family:var(--f-display);font-size:1.24rem;font-weight:600;letter-spacing:-.018em;
  color:var(--tinta);margin-top:.3rem}
.entrada__q{margin:.55rem 0 0;font-size:.88rem;line-height:1.55;color:var(--ink-2)}
.entrada__f{margin-top:1.1rem;font-family:var(--f-mono);font-size:.66rem;letter-spacing:.1em;
  color:var(--accent);text-transform:uppercase}

/* --- el reloj de la primera visita --------------------------------------- */
.reloj{margin:0 0 2.2rem}
.reloj__barra{display:flex;height:5.6rem;border-radius:10px;overflow:hidden;
  border:1px solid var(--line);background:var(--surface)}
.reloj__t{
  font:inherit;cursor:pointer;border:0;border-right:1px solid rgba(255,255,255,.6);
  background:color-mix(in srgb, var(--c) 13%, #fff);color:var(--tinta);
  border-left:2px solid color-mix(in srgb, var(--c) 55%, #fff);
  padding:.6rem .5rem;display:flex;flex-direction:column;justify-content:space-between;
  align-items:flex-start;overflow:hidden;position:relative;transition:background .16s var(--e);
  min-width:0;box-sizing:border-box;flex-shrink:1;
}
/* Los bordes de doce trozos suman veinticuatro píxeles: sin encogerlos, el
   último se salía por la derecha y la fase 12 quedaba cortada. */
.reloj__t:last-child{border-right:0}
.reloj__t::before{content:"";position:absolute;inset:auto 0 0 0;height:4px;background:var(--c)}
.reloj__t:first-child{border-left:0}
.reloj__t:hover{background:color-mix(in srgb, var(--c) 24%, #fff)}
.reloj__t.es-on{background:var(--c);color:#fff}
.reloj__t.es-on .reloj__n,.reloj__t.es-on .reloj__m{color:rgba(255,255,255,.82)}
.reloj__n{font-family:var(--f-mono);font-size:.62rem;color:var(--c);font-weight:600}
.reloj__r{font-size:.72rem;line-height:1.2;font-weight:500;text-align:left;
  overflow:hidden;text-overflow:ellipsis;display:-webkit-box;-webkit-line-clamp:2;
  -webkit-box-orient:vertical;white-space:normal}
.reloj__m{font-family:var(--f-mono);font-size:.6rem;color:var(--muted)}
.reloj__eje{position:relative;height:1.3rem;margin-top:.4rem}
.reloj__eje span{position:absolute;transform:translateX(-50%);font-family:var(--f-mono);
  font-size:.6rem;color:var(--muted)}
.reloj__eje span:first-child{transform:none}
.reloj__eje span:last-child{transform:translateX(-100%)}

.vistas{display:flex;gap:.3rem;margin:0 0 1.4rem}
.vista{font:inherit;font-size:.84rem;cursor:pointer;border:1px solid var(--line-soft);
  background:var(--surface);color:var(--ink-2);border-radius:999px;padding:.4rem .95rem}
.vista.es-on{background:var(--tinta);border-color:var(--tinta);color:#fff}

.minifs{display:grid;grid-template-columns:repeat(auto-fill,minmax(15rem,1fr));gap:.7rem}
.minif{
  font:inherit;text-align:left;cursor:pointer;background:var(--surface);
  border:1px solid var(--line-soft);border-left:3px solid var(--c);border-radius:9px;
  padding:.95rem 1.05rem 1rem;display:flex;flex-direction:column;gap:.2rem;
  transition:border-color .16s var(--e),transform .16s var(--e);
}
.minif:hover{border-color:var(--line);border-left-color:var(--c);transform:translateY(-2px)}
.minif__n{font-family:var(--f-mono);font-size:.62rem;color:var(--c);font-weight:600}
.minif__r{font-size:.98rem;font-weight:600;color:var(--tinta);line-height:1.3}
.minif__q{font-size:.82rem;color:var(--ink-2);line-height:1.5;margin-top:.2rem}
.minif__m{margin-top:.6rem;font-family:var(--f-mono);font-size:.62rem;color:var(--muted)}

.carriles{display:flex;flex-direction:column;gap:.4rem}
.carril{display:grid;grid-template-columns:9rem minmax(0,1fr);gap:1rem;align-items:center}
.carril__q{margin:0;font-size:.82rem;color:var(--ink-2);text-align:right}
.carril__p{position:relative;height:2.1rem;background:var(--surface);
  border:1px solid var(--line-soft);border-radius:6px}
.carril__b{
  position:absolute;top:.25rem;bottom:.25rem;border:0;border-radius:4px;cursor:pointer;
  background:color-mix(in srgb, var(--c) 22%, #fff);font-family:var(--f-mono);font-size:.6rem;
  color:var(--c);display:flex;align-items:center;justify-content:center;
}
.carril__b.es-jefe{background:var(--c);color:#fff}
.carril__b:hover{outline:2px solid var(--tinta);outline-offset:1px}

/* --- la ficha de una fase ------------------------------------------------ */
.bloque--fase{scroll-margin-top:calc(var(--nav) + 1rem)}
.fase{border-top:1px solid var(--line);padding-top:2.4rem}
.fase__n{margin:0;font-family:var(--f-mono);font-size:.66rem;letter-spacing:.13em;
  text-transform:uppercase;color:var(--muted)}
.fase__n b{color:var(--accent);font-size:.8rem}
.fase__cab h3{font-size:clamp(1.5rem,3vw,2.2rem);letter-spacing:-.024em;margin:.7rem 0 0;
  max-width:24ch}
.fase__lede{margin:.9rem 0 0;font-size:1.02rem;line-height:1.65;color:var(--ink-2);max-width:60ch}
.fase__roles{display:flex;flex-wrap:wrap;gap:.45rem;align-items:center;margin:1.2rem 0 0}
.rolchip{font-family:var(--f-mono);font-size:.62rem;letter-spacing:.08em;text-transform:uppercase;
  color:#fff;background:var(--c);border-radius:999px;padding:.24rem .65rem}
.fase__min{font-family:var(--f-mono);font-size:.66rem;color:var(--muted);margin-left:.3rem}
.fase__meta{display:grid;grid-template-columns:repeat(auto-fit,minmax(11rem,1fr));gap:1px;
  margin:2rem 0 2.4rem;background:var(--line-soft);border:1px solid var(--line-soft);
  border-radius:10px;overflow:hidden}
.fase__meta > div{background:var(--surface);padding:.9rem 1rem}
.fase__meta dt{font-family:var(--f-mono);font-size:.58rem;letter-spacing:.13em;
  text-transform:uppercase;color:var(--muted)}
.fase__meta dd{margin:.35rem 0 0;font-size:.86rem;line-height:1.45;color:var(--tinta)}
.fase__texto{max-width:var(--texto)}
.fase__texto > *:first-child,.fase__texto .phase__body > *:first-child,
.fase__texto .phase__grid > *:first-child{margin-top:0}
.fase__texto .block:first-of-type{margin-top:0}
/* El titular y la entradilla de la fase ya están arriba, en la cabecera de la
   ficha, con su número, sus minutos y sus puestos. Repetirlos dos párrafos
   más abajo es exactamente lo que hace que un documento parezca un documento. */
.fase__texto .phase__meta,.fase__texto .phase__num,
.fase__texto .phase__body > h2:first-child,
.fase__texto .phase__body > h3:first-child,
.fase__texto .phase__intro{display:none}
.fase__texto .wrap{padding:0;max-width:none}
.fase__texto .phase__grid{display:block}
.fase__texto .reveal{opacity:1!important;transform:none!important}

/* --- puestos -------------------------------------------------------------- */
.selector2{display:flex;flex-wrap:wrap;gap:.45rem;margin-bottom:2.4rem}
.selpuesto{
  font:inherit;cursor:pointer;text-align:left;background:var(--surface);
  border:1px solid var(--line-soft);border-top:3px solid var(--c);border-radius:9px;
  padding:.7rem 1.1rem .75rem;transition:background .16s var(--e);
}
.selpuesto b{display:block;font-size:.95rem;font-weight:600;color:var(--tinta)}
.selpuesto span{display:block;margin-top:.15rem;font-family:var(--f-mono);font-size:.6rem;
  color:var(--muted)}
.selpuesto:hover{background:var(--surface-2)}
.selpuesto.es-on{background:var(--c);border-color:var(--c)}
.selpuesto.es-on b,.selpuesto.es-on span{color:#fff}
.puesto__cab h3{font-size:clamp(1.6rem,3.2vw,2.3rem);letter-spacing:-.024em;margin:.6rem 0 0}
.puesto__q{margin:.9rem 0 0;font-size:1.02rem;line-height:1.65;color:var(--ink-2);max-width:58ch}
.puesto__cifras{display:flex;flex-wrap:wrap;gap:2.2rem;margin:1.8rem 0 2.6rem;padding:1.3rem 0;
  border-top:1px solid var(--line-soft);border-bottom:1px solid var(--line-soft)}
.puesto__cifras b{display:block;font-family:var(--f-display);font-size:1.6rem;color:var(--c)}
.puesto__cifras span{display:block;margin-top:.2rem;font-family:var(--f-mono);font-size:.6rem;
  letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}
.raci{display:grid;grid-template-columns:repeat(14,minmax(0,1fr));gap:3px}
.raci__c{aspect-ratio:1;border-radius:5px;display:flex;flex-direction:column;
  align-items:center;justify-content:center;background:var(--surface-2);cursor:help}
.raci__f{font-family:var(--f-mono);font-size:.54rem;color:var(--muted)}
.raci__p{font-family:var(--f-mono);font-size:.72rem;font-weight:600;color:var(--muted)}
.raci__c.es-ra{background:var(--accent-fuerte)}
.raci__c.es-r{background:var(--accent)}
.raci__c.es-a{background:var(--rol-doctor)}
.raci__c.es-ra .raci__p,.raci__c.es-r .raci__p,.raci__c.es-a .raci__p,
.raci__c.es-ra .raci__f,.raci__c.es-r .raci__f,.raci__c.es-a .raci__f{color:#fff}
.raci__c.es-c{background:var(--acido)}
.raci__c.es-c .raci__p{color:var(--accent-fuerte)}
.raci__c.es-i{background:var(--surface);border:1px solid var(--line)}
.raci__c.es-no{background:transparent;border:1px dashed var(--line-soft)}
.raci__c.es-no .raci__p{color:var(--line)}
.leyenda{margin:1rem 0 0;font-size:.78rem;color:var(--muted);line-height:1.6}
.leyenda b{font-family:var(--f-mono);color:var(--tinta)}
.puesto__cols{display:grid;grid-template-columns:repeat(auto-fit,minmax(19rem,1fr));gap:2.6rem;
  margin-top:2.8rem}
.listilla{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:.1rem}
.listilla a{display:flex;gap:.7rem;align-items:baseline;text-decoration:none;color:var(--ink-2);
  font-size:.9rem;line-height:1.45;padding:.4rem .5rem;border-radius:6px}
.listilla a span{font-family:var(--f-mono);font-size:.58rem;color:var(--muted);flex:none}
.listilla a:hover{background:var(--surface-2);color:var(--accent-ink)}
.listilla .es-vacio{font-size:.88rem;color:var(--muted);line-height:1.55;padding:.4rem .5rem}
.puesto__ir{margin:2.4rem 0 0}
.puesto__ir a{font-size:.9rem;color:var(--accent-ink);text-decoration:none}
.puesto__ir a:hover{text-decoration:underline}

/* --- protocolos ----------------------------------------------------------- */
.mapa{display:grid;grid-template-columns:repeat(auto-fill,minmax(11rem,1fr));gap:.5rem}
.mfase{font:inherit;text-align:left;cursor:pointer;background:var(--surface);
  border:1px solid var(--line-soft);border-radius:9px;padding:.85rem .95rem;
  display:flex;flex-direction:column;gap:.15rem;position:relative;overflow:hidden}
.mfase::before{content:"";position:absolute;inset:0 auto 0 0;width:3px;background:var(--c)}
.mfase:hover{border-color:var(--line);background:var(--surface-2)}
.mfase__n{font-family:var(--f-mono);font-size:.6rem;color:var(--c);font-weight:600}
.mfase b{font-size:.9rem;font-weight:600;color:var(--tinta);line-height:1.3}
.mfase__r{font-family:var(--f-mono);font-size:.58rem;color:var(--muted);margin-top:.3rem}
.procs{display:grid;grid-template-columns:repeat(auto-fill,minmax(19rem,1fr));gap:1rem}
.proc{background:var(--surface);border:1px solid var(--line-soft);border-top:3px solid var(--c);
  border-radius:10px;padding:1.2rem 1.3rem 1.4rem}
.proc header b{display:block;font-size:1rem;font-weight:600;color:var(--tinta)}
.proc header span{display:block;margin-top:.15rem;font-family:var(--f-mono);font-size:.6rem;
  color:var(--muted)}
.proc ol{margin:1rem 0 0;padding:0 0 0 1.1rem;display:flex;flex-direction:column;gap:.4rem}
.proc li{font-size:.86rem;line-height:1.45;color:var(--ink-2)}
.proc a{color:inherit;text-decoration:none}
.proc a:hover{color:var(--accent-ink);text-decoration:underline}

/* --- marketing ------------------------------------------------------------ */
.estados{display:grid;grid-template-columns:repeat(auto-fill,minmax(13rem,1fr));gap:.55rem;
  margin-bottom:2rem}
.estado{font:inherit;text-align:left;cursor:pointer;background:var(--surface);
  border:1px solid var(--line-soft);border-radius:9px;padding:.9rem 1rem 1rem}
.estado:hover,.estado.es-on{border-color:var(--accent);background:var(--acido)}
.estado__n{font-family:var(--f-mono);font-size:.6rem;color:var(--accent);font-weight:600}
.estado b{display:block;margin-top:.2rem;font-size:.95rem;color:var(--tinta)}
.estado p{margin:.35rem 0 0;font-size:.8rem;line-height:1.45;color:var(--ink-2)}
.gruposm{display:grid;grid-template-columns:repeat(auto-fill,minmax(16rem,1fr));gap:1rem}
.grupom{padding:1.1rem 0 0;border-top:1px solid var(--line)}
.grupom__n{margin:0;font-family:var(--f-mono);font-size:.6rem;letter-spacing:.12em;color:var(--muted)}
.grupom b{display:block;margin-top:.3rem;font-size:.98rem;color:var(--tinta)}
.grupom p{margin:.4rem 0 0;font-size:.84rem;line-height:1.5;color:var(--ink-2)}
.filtros{display:flex;flex-wrap:wrap;gap:.7rem;align-items:flex-end;margin-bottom:1.2rem}
.filtro{display:flex;flex-direction:column;gap:.25rem}
.filtro span{font-family:var(--f-mono);font-size:.58rem;letter-spacing:.13em;
  text-transform:uppercase;color:var(--muted)}
.filtro select{font:inherit;font-size:.85rem;padding:.4rem .7rem;border-radius:7px;
  border:1px solid var(--line);background:var(--surface);color:var(--ink)}
.limpiar{font:inherit;font-size:.82rem;cursor:pointer;border:1px solid var(--line-soft);
  background:none;color:var(--muted);border-radius:999px;padding:.4rem .9rem}
.limpiar:hover{border-color:var(--accent);color:var(--accent-ink)}
.cuentafiltro{font-family:var(--f-mono);font-size:.66rem;color:var(--muted);margin-left:auto}
.tablawrap{overflow-x:auto;border:1px solid var(--line);border-radius:10px;background:var(--surface)}
.acciones{width:100%;border-collapse:collapse;font-size:.86rem;min-width:52rem}
.acciones th{font-family:var(--f-mono);font-size:.58rem;letter-spacing:.13em;text-transform:uppercase;
  color:var(--muted);text-align:left;padding:.8rem 1rem;border-bottom:1px solid var(--line);
  background:var(--surface-2);position:sticky;top:0}
.acciones td{padding:.85rem 1rem;border-bottom:1px solid var(--line-soft);vertical-align:top}
.acciones tr:last-child td{border-bottom:0}
.acciones tr:hover td{background:var(--surface-2)}
.acc__cod{font-family:var(--f-mono);font-size:.7rem;color:var(--accent);white-space:nowrap}
.acc__q b{display:block;font-weight:500;color:var(--tinta);line-height:1.45}
.acc__q span{display:block;margin-top:.3rem;font-size:.76rem;color:var(--muted);line-height:1.4}
.acc__gana{color:var(--ink-2);line-height:1.45;max-width:22rem}
.acc__meta{white-space:nowrap}
.etq{display:inline-block;font-family:var(--f-mono);font-size:.58rem;letter-spacing:.06em;
  color:var(--ink-2);background:var(--surface-2);border-radius:4px;padding:.16rem .4rem;
  margin:0 .25rem .25rem 0}
.etq--verde{background:var(--acido);color:var(--accent-fuerte)}
.etq--amarillo{background:#F6EFD6;color:#6E6112}
.etq--naranja{background:#F6E3D2;color:var(--sem-naranja)}
.acc__ef{white-space:nowrap;font-family:var(--f-mono);font-size:.72rem;color:var(--muted)}
.barrita{display:inline-block;width:2.6rem;height:5px;border-radius:3px;background:var(--line);
  margin-right:.45rem;position:relative;vertical-align:middle}
.barrita::before{content:"";position:absolute;inset:0 auto 0 0;width:var(--v);border-radius:3px;
  background:var(--accent)}
.campanas{display:grid;grid-template-columns:repeat(auto-fill,minmax(18rem,1fr));gap:1rem}
.campana{background:var(--surface);border:1px solid var(--line-soft);border-radius:10px;
  padding:1.2rem 1.3rem 1.3rem}
.campana h4{margin:.3rem 0 0;font-size:1.05rem;letter-spacing:-.014em}
.campana__r{margin:.6rem 0 0;font-size:.85rem;line-height:1.55;color:var(--ink-2)}
.campana__c{display:flex;gap:1.4rem;margin:1.1rem 0 0;padding-top:.9rem;
  border-top:1px solid var(--line-soft)}
.campana__c dt{font-family:var(--f-mono);font-size:.56rem;letter-spacing:.12em;
  text-transform:uppercase;color:var(--muted)}
.campana__c dd{margin:.2rem 0 0;font-family:var(--f-display);font-size:1.05rem;color:var(--tinta)}

/* --- gtc y números -------------------------------------------------------- */
.cabecera--gtc h1 em{color:var(--accent-ink)}
.gtcps{display:grid;grid-template-columns:repeat(auto-fit,minmax(18rem,1fr));gap:1rem}
.gtcp{background:var(--surface);border:1px solid var(--line-soft);border-left:3px solid var(--accent);
  border-radius:10px;padding:1.3rem 1.4rem}
.gtcp b{display:block;font-family:var(--f-display);font-size:1.9rem;color:var(--accent-ink);
  letter-spacing:-.02em}
.gtcp__q{margin:.4rem 0 0;font-weight:600;color:var(--tinta);font-size:.95rem}
.gtcp__c{margin:.5rem 0 0;font-size:.84rem;line-height:1.5;color:var(--ink-2)}
.puente{display:flex;flex-direction:column;gap:.5rem}
.puente__t{position:relative;height:3.1rem;border-radius:7px;padding:.55rem .9rem;
  background:color-mix(in srgb, var(--c) 16%, #fff);border-left:3px solid var(--c);
  width:max(var(--w),14rem);display:flex;flex-direction:column;justify-content:center}
.puente__r{font-size:.86rem;font-weight:600;color:var(--tinta)}
.puente__v{font-family:var(--f-mono);font-size:.7rem;color:var(--ink-2)}
.puente__pie{margin:1.2rem 0 0;font-size:.88rem;color:var(--ink-2)}
.puente__pie b{color:var(--tinta)}

/* --- biblioteca ----------------------------------------------------------- */
#biblioteca{max-width:none;padding:0}
.bibl{display:grid;grid-template-columns:19rem minmax(0,1fr);min-height:calc(100vh - var(--nav))}
.lado{position:sticky;top:var(--nav);height:calc(100vh - var(--nav));display:flex;
  flex-direction:column;background:var(--surface);border-right:1px solid var(--line-soft)}
.arbol{flex:1;overflow-y:auto;padding:.8rem .55rem 2.5rem;scrollbar-width:thin}
.arbol__inicio{display:block;text-decoration:none;padding:.5rem .65rem;border-radius:7px;
  color:var(--ink-2);font-size:.86rem;font-weight:500;margin:0 0 .5rem}
.arbol__inicio:hover{background:var(--surface-2);color:var(--ink)}
.arbol__inicio.is-on{background:var(--acido);color:var(--accent-fuerte)}
.lado__doc > summary{display:flex;align-items:center;gap:.55rem;cursor:pointer;list-style:none;
  padding:.55rem .65rem;border-radius:7px}
.lado__doc > summary::-webkit-details-marker{display:none}
.lado__doc > summary:hover{background:var(--surface-2)}
.lado__doc > summary b{font-family:var(--f-mono);font-size:.64rem;color:var(--muted);font-weight:500}
.lado__doc > summary span{flex:1;font-size:.86rem;font-weight:600;color:var(--tinta);line-height:1.3}
.lado__doc > summary i{font-style:normal;flex:none;display:block;width:1.05rem;height:1.05rem}
.lado__doc[open] > summary span{color:var(--accent-ink)}
.aro{transform:rotate(-90deg)}
.aro circle{fill:none;stroke-width:2.4}
.aro .aro__f{stroke:var(--line)}
.aro .aro__v{stroke:var(--accent);stroke-linecap:round;transition:stroke-dashoffset .3s ease}
.lado__ramas{padding:0 0 .55rem .3rem;margin-left:.95rem;border-left:1px solid var(--line-soft)}
.lado__gt{margin:.65rem 0 .2rem;padding-left:.65rem;font-family:var(--f-mono);font-size:.58rem;
  letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}
.lado__ramas a{display:flex;gap:.5rem;align-items:baseline;text-decoration:none;color:var(--ink-2);
  font-size:.81rem;line-height:1.36;padding:.32rem .5rem;border-radius:6px;position:relative}
.lado__ramas a span{font-family:var(--f-mono);font-size:.6rem;color:var(--muted);flex:none;min-width:1rem}
.lado__ramas a:hover{background:var(--surface-2);color:var(--ink)}
.lado__ramas a.is-on{background:var(--acido);color:var(--accent-fuerte);font-weight:600}
.lado__ramas a.is-leido::after{content:"";position:absolute;right:.45rem;top:50%;width:5px;height:5px;
  border-radius:50%;background:var(--accent);transform:translateY(-50%);opacity:.55}
.marco{display:grid;grid-template-columns:minmax(0,1fr) 15.5rem;gap:2.6rem;
  padding:2.4rem 2.2rem 6rem;max-width:74rem;margin:0 auto;width:100%}
.marco--ancho{grid-template-columns:minmax(0,1fr)}
.marco--ancho .sumario{display:none}
.lectura{min-width:0}
.hoja{max-width:var(--texto);margin:0 auto}
.hoja--portada{max-width:none}
.hoja__de{margin:0 0 1.6rem;font-family:var(--f-mono);font-size:.64rem;letter-spacing:.13em;
  text-transform:uppercase;color:var(--muted);display:flex;flex-wrap:wrap;gap:.55rem;align-items:center}
.hoja__de span{color:var(--accent)}
.hoja .wrap{padding:0;max-width:none}
.hoja .section{padding:0;background:none;border:0}
.hoja .section + .section{margin-top:3.2rem;padding-top:3.2rem;border-top:1px solid var(--line-soft)}
.hoja .reveal{opacity:1!important;transform:none!important}
.hoja .phase__grid{grid-template-columns:minmax(0,1fr)}
.hoja .phase__meta{position:static}
.hoja .tablewrap{overflow-x:auto}
.lectura--viva .hoja{display:none}
.lectura--viva .hoja.is-on{display:block}
.bibcima{display:flex;align-items:center;gap:.9rem;padding:.7rem 2.2rem;
  border-bottom:1px solid var(--line-soft);background:var(--surface-2)}
.miga{flex:1;min-width:0;font-size:.8rem;color:var(--muted);white-space:nowrap;overflow:hidden;
  text-overflow:ellipsis}
.miga b{color:var(--tinta);font-weight:600}
.miga em{font-style:normal;color:var(--line)}
.cima__n{font-family:var(--f-mono);font-size:.66rem;color:var(--muted);white-space:nowrap}
.sumario{position:sticky;top:calc(var(--nav) + 2.4rem);align-self:start;
  max-height:calc(100vh - var(--nav) - 4rem);overflow-y:auto;scrollbar-width:none}
.sumario::-webkit-scrollbar{display:none}
.sumario__t{margin:0 0 .8rem;font-family:var(--f-mono);font-size:.6rem;letter-spacing:.15em;
  text-transform:uppercase;color:var(--muted)}
.sumario ol{list-style:none;margin:0;padding:0;border-left:1px solid var(--line-soft)}
.sumario a{display:block;text-decoration:none;color:var(--muted);font-size:.79rem;line-height:1.4;
  padding:.3rem 0 .3rem .8rem;margin-left:-1px;border-left:2px solid transparent}
.sumario a:hover{color:var(--ink)}
.sumario a.is-aqui{color:var(--accent-ink);border-left-color:var(--accent);font-weight:600}
.sumario__pie{margin-top:1.4rem;padding-top:1rem;border-top:1px solid var(--line-soft);
  display:flex;flex-direction:column;gap:.35rem}
.sumario__pie button{font:inherit;font-size:.79rem;cursor:pointer;background:none;border:0;
  padding:.2rem 0;color:var(--muted);text-align:left}
.sumario__pie button:hover{color:var(--accent-ink)}
.remate{display:flex;flex-wrap:wrap;gap:.7rem;align-items:center;justify-content:space-between;
  margin-top:4rem;padding-top:1.6rem;border-top:1px solid var(--line-soft)}
.marca-leido{display:inline-flex;align-items:center;gap:.5rem;font:inherit;font-size:.85rem;
  cursor:pointer;border:1px solid var(--line);background:var(--surface);color:var(--ink-2);
  border-radius:999px;padding:.45rem .95rem}
.marca-leido:hover{border-color:var(--accent);color:var(--accent-ink)}
.marca-leido[aria-pressed="true"]{background:var(--acido);border-color:var(--acido);
  color:var(--accent-fuerte)}
.remate a{text-decoration:none;font-size:.85rem;color:var(--ink-2);display:inline-flex;gap:.5rem;
  align-items:center}
.remate a:hover{color:var(--accent-ink)}
.remate a i{font-style:normal;font-family:var(--f-mono);font-size:.66rem;color:var(--muted)}
.idx{margin-top:3rem}
.idx__cabeza{padding:0 0 1.2rem;border-bottom:1px solid var(--line);margin-bottom:2rem}
.idx__cabeza h2{margin:.45rem 0 0;font-size:clamp(1.6rem,3.2vw,2.3rem);letter-spacing:-.024em}
.idx__cabeza p{margin:.7rem 0 0;color:var(--ink-2);max-width:62ch;line-height:1.62}
.idx__doc{padding:1.9rem 0 2.1rem;border-bottom:1px solid var(--line-soft)}
.idx__cab h3{margin:.4rem 0 0;font-size:1.4rem;letter-spacing:-.018em;display:flex;gap:.8rem;
  align-items:baseline}
.idx__cab h3 span{font-family:var(--f-mono);font-size:.82rem;color:var(--accent);font-weight:500}
.idx__cab > p{margin:.5rem 0 0;color:var(--ink-2);font-size:.94rem;line-height:1.6;max-width:70ch}
.idx__lista{margin-top:1.5rem;columns:2;column-gap:2.8rem}
.idx__gt{break-inside:avoid;margin:1.2rem 0 .45rem;font-family:var(--f-mono);font-size:.61rem;
  letter-spacing:.15em;text-transform:uppercase;color:var(--accent-ink)}
.idx__gt:first-child{margin-top:0}
.idx__ap{break-inside:avoid;margin-bottom:.7rem}
.idx__ap a{display:flex;gap:.65rem;align-items:baseline;text-decoration:none;color:var(--ink-2)}
.idx__ap a span{font-family:var(--f-mono);font-size:.66rem;color:var(--muted);flex:none;min-width:1.3rem}
.idx__ap a b{font-size:.93rem;font-weight:500;line-height:1.4}
.idx__ap a:hover b{color:var(--accent-ink)}
.idx__t{margin:.2rem 0 0 1.95rem;font-size:.76rem;line-height:1.5;color:var(--muted)}
a.fuera::after{content:"↗";font-size:.76em;margin-left:.18em;color:var(--muted)}

/* ===========================================================================
   LO QUE APARECE CUANDO SE PIDE
   =========================================================================== */
.velo{position:fixed;inset:0;z-index:80;display:flex;align-items:flex-start;justify-content:center;
  padding:8vh 1.2rem 1.2rem;background:rgba(18,35,43,.34);backdrop-filter:blur(3px);
  animation:vela .14s ease}
@keyframes vela{from{opacity:0}to{opacity:1}}
.velo[hidden]{display:none}
.flota{width:min(44rem,100%);max-height:82vh;display:flex;flex-direction:column;overflow:hidden;
  background:var(--surface);border-radius:13px;box-shadow:var(--sombra-flota);
  animation:sube .16s var(--e)}
@keyframes sube{from{opacity:0;transform:translateY(8px) scale(.99)}to{opacity:1;transform:none}}
@media(prefers-reduced-motion:reduce){.velo,.flota,.entrada,.minif{animation:none;transition:none}}
.flota__cab{display:flex;align-items:center;gap:.7rem;padding:.85rem 1.1rem;
  border-bottom:1px solid var(--line-soft)}
.flota__cab h2{margin:0;font-size:1rem;font-weight:600;flex:1}
.flota__cuerpo{overflow-y:auto;padding:1.1rem 1.3rem 1.4rem}
.flota__pie{padding:.6rem 1.1rem;border-top:1px solid var(--line-soft);background:var(--surface-2);
  font-family:var(--f-mono);font-size:.63rem;letter-spacing:.08em;color:var(--muted);
  display:flex;gap:1.1rem;flex-wrap:wrap}
.flota__pie kbd{background:var(--surface);border:1px solid var(--line-soft);border-radius:4px;
  padding:.1rem .3rem;font-family:inherit}
.pal__campo{display:flex;align-items:center;gap:.7rem;padding:1rem 1.2rem;
  border-bottom:1px solid var(--line-soft)}
.pal__campo input{flex:1;border:0;outline:none;background:none;font:inherit;font-size:1.02rem;
  color:var(--ink)}
.pal__campo input::placeholder{color:var(--muted)}
.pal__campo input::-webkit-search-cancel-button{-webkit-appearance:none;appearance:none}
.pal__lista{overflow-y:auto;padding:.45rem;max-height:56vh}
.pal__g{margin:.7rem .6rem .35rem;font-family:var(--f-mono);font-size:.6rem;letter-spacing:.15em;
  text-transform:uppercase;color:var(--muted)}
.pal__i{display:flex;gap:.8rem;align-items:baseline;width:100%;text-align:left;font:inherit;
  cursor:pointer;background:none;border:0;border-radius:8px;padding:.55rem .6rem;color:var(--ink-2)}
.pal__i span{font-family:var(--f-mono);font-size:.62rem;color:var(--muted);flex:none;min-width:1.5rem}
.pal__i b{font-weight:500;font-size:.93rem;line-height:1.35}
.pal__i i{font-style:normal;font-size:.75rem;color:var(--muted);margin-left:auto;flex:none;
  padding-left:1rem}
.pal__i mark{background:var(--acido);color:var(--accent-fuerte);padding:0 .1em;border-radius:2px}
.pal__i:hover,.pal__i.es-aqui{background:var(--surface-2)}
.pal__i.es-aqui{background:var(--acido)}
.pal__i.es-aqui b{color:var(--accent-fuerte)}
.pal__i b .pal__ctx{display:block;font-family:inherit;font-size:.78rem;font-weight:400;
  color:var(--muted);margin-top:.25rem;line-height:1.5;letter-spacing:0}
.pal__nada{padding:2rem 1rem;text-align:center;color:var(--muted);font-size:.9rem}
.gl{font:inherit;cursor:help;background:none;border:0;padding:0;color:inherit;
  border-bottom:1px dashed var(--accent)}
.gl:hover{color:var(--accent-ink)}
.voz{position:absolute;z-index:90;width:min(22rem,calc(100vw - 2rem));background:var(--surface);
  border:1px solid var(--line);border-radius:10px;box-shadow:var(--sombra-flota);
  padding:.95rem 1.05rem 1rem}
.voz[hidden]{display:none}
.voz b{display:block;font-family:var(--f-display);font-size:1rem;color:var(--tinta)}
.voz p{margin:.45rem 0 0;font-size:.88rem;line-height:1.55;color:var(--ink-2)}
.voz small{display:block;margin-top:.7rem;padding-top:.6rem;border-top:1px solid var(--line-soft);
  font-family:var(--f-mono);font-size:.6rem;letter-spacing:.1em;text-transform:uppercase;
  color:var(--muted)}
.rec__g{margin:0 0 1.6rem}
.rec__g:last-child{margin-bottom:0}
.rec__t{margin:0 0 .7rem;font-family:var(--f-mono);font-size:.61rem;letter-spacing:.15em;
  text-transform:uppercase;color:var(--muted)}
.rec__i{display:flex;gap:.9rem;align-items:flex-start;padding:.7rem .8rem;border-radius:9px;
  text-decoration:none;color:inherit;width:100%;text-align:left;font:inherit;background:none;
  border:1px solid transparent;cursor:pointer}
.rec__i:hover{background:var(--surface-2);border-color:var(--line-soft)}
.rec__i em{font-style:normal;font-family:var(--f-mono);font-size:.6rem;color:var(--accent);
  flex:none;min-width:2.6rem;padding-top:.2rem;letter-spacing:.08em}
.rec__i b{display:block;font-size:.93rem;font-weight:600;color:var(--tinta)}
.rec__i p{margin:.2rem 0 0;font-size:.82rem;line-height:1.5;color:var(--ink-2)}
.tec{display:grid;grid-template-columns:auto 1fr;gap:.5rem 1.1rem;align-items:baseline}
.tec dt{font-family:var(--f-mono);font-size:.72rem;color:var(--tinta);white-space:nowrap}
.tec dt kbd{background:var(--surface-2);border:1px solid var(--line-soft);border-radius:5px;
  padding:.15rem .4rem;font-family:inherit}
.tec dd{margin:0;font-size:.87rem;color:var(--ink-2);line-height:1.5}
.lupa{align-items:center;padding:3vh 3vw}
.lupa .flota{width:min(72rem,100%);max-height:94vh}
.lupa__lienzo{padding:1.8rem 2rem 2rem;overflow:auto}
.lupa__lienzo > *{max-width:100%;margin:0}
.lupa__lienzo svg{width:100%;height:auto}
.ampliable{cursor:zoom-in}
.pito{position:fixed;left:50%;bottom:2rem;transform:translateX(-50%);z-index:95;
  background:var(--tinta);color:#fff;border-radius:999px;padding:.6rem 1.2rem;font-size:.85rem;
  box-shadow:var(--sombra-flota);animation:sube .16s ease}
.pito[hidden]{display:none}

@media(max-width:1240px){
  .marco{grid-template-columns:minmax(0,1fr);gap:0}
  .sumario{display:none}
  .hero{grid-template-columns:minmax(0,1fr);gap:2.4rem}
}
@media(max-width:860px){
  /* En un teléfono la marca, ocho secciones y tres botones no caben en una
     línea: la fila de secciones baja a la suya y se desplaza a lo ancho. Sin
     esto la barra empujaba once píxeles a toda la página. */
  :root{--nav:5.9rem}
  .nav{height:auto;flex-wrap:wrap;padding:.5rem 1rem .35rem;gap:.45rem 1rem;align-items:center}
  .nav__m{flex:1 1 auto}
  .nav__b{flex:0 0 auto}
  .nav__l{order:3;flex:1 0 100%;width:100%;min-width:100%;padding-bottom:.2rem}
  .abrepal span{display:none}
}
@media(max-width:1080px){
  .bibl{grid-template-columns:minmax(0,1fr)}
  .lado{position:fixed;inset:var(--nav) auto 0 0;height:auto;width:min(21rem,86vw);
    transform:translateX(-101%);transition:transform .2s var(--e);z-index:40;
    box-shadow:0 0 40px rgba(18,35,43,.2)}
  .lado.is-abierto{transform:none}
  .pag{padding:2rem 1.1rem 5rem}
  .marco{padding:1.4rem 1.1rem 5rem}
  .reloj__barra{height:auto;flex-direction:column}
  .reloj__t{width:100%!important;flex-direction:row;gap:.7rem;align-items:center;
    border-right:0;border-bottom:1px solid var(--line-soft)}
  .reloj__t::before{inset:0 auto 0 0;width:3px;height:auto}
  .reloj__r{-webkit-line-clamp:1;flex:1}
  .reloj__eje{display:none}
  .carril{grid-template-columns:5.5rem minmax(0,1fr);gap:.5rem}
  .raci{grid-template-columns:repeat(7,minmax(0,1fr))}
  .velo{padding:4vh .8rem .8rem}
  .cifrafila{gap:1.4rem 2rem}
}
@media print{
  .nav,.lado,.velo,.voz,.avance,.remate,.pito,.vistas,.sumario,.bibcima{display:none}
  .sitio--vivo .pag{display:block}
  .lectura--viva .hoja{display:block;break-after:page}
  .fase[hidden]{display:block!important}
  .bibl,.marco{display:block}
}
"""


JS = """
<script>
(function(){
  "use strict";
  var D = document;
  var sitio = D.getElementById("sitio");
  if(!sitio) return;

  var pags   = [].slice.call(D.querySelectorAll(".pag"));
  var orden  = window.__ORDEN__ || [];
  var VOCES  = window.__VOCES__ || {};
  var lado   = D.getElementById("lado");
  var arbol  = D.getElementById("arbol");
  var lectura= D.getElementById("lectura");
  var miga   = D.getElementById("miga");
  var cuenta = D.getElementById("cuenta");
  var ant    = D.getElementById("ant");
  var sig    = D.getElementById("sig");
  var avance = D.getElementById("avance");
  var sumario= D.getElementById("sumario");
  var hojas  = lectura ? [].slice.call(lectura.querySelectorAll(".hoja")) : [];

  /* Las marcas las pone el guion y no el marcado: si esto no llegara a correr,
     se ve el sitio entero seguido —las siete secciones y los 135 apartados— en
     vez de quedarse la página en blanco. */
  sitio.classList.add("sitio--vivo");
  if(lectura) lectura.classList.add("lectura--viva");

  var porClave = {};
  hojas.forEach(function(h){ porClave[h.dataset.hoja] = h; });
  var claves = orden.map(function(o){ return o[0]; });

  /* ---------------------------------------------------------------- */
  /*  Memoria de este navegador: por dónde iba y qué dio por leído     */
  /* ---------------------------------------------------------------- */
  var LLAVE = "giraldo.centro.v8";
  var memo = {leidos:{}, ultimo:"", pag:""};
  try {
    var g = localStorage.getItem(LLAVE);
    if(g) memo = JSON.parse(g) || memo;
    if(!memo.leidos) memo.leidos = {};
  } catch(e){}
  function recuerda(){ try { localStorage.setItem(LLAVE, JSON.stringify(memo)); } catch(e){} }

  function esc(s){
    return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
  }

  /* ---------------------------------------------------------------- */
  /*  Ir a una sección                                                  */
  /* ---------------------------------------------------------------- */
  function vePag(id, arriba){
    var hay = pags.filter(function(p){ return p.dataset.pag === id; })[0] || pags[0];
    pags.forEach(function(p){ p.classList.toggle("es-on", p === hay); });
    [].slice.call(D.querySelectorAll(".nav__l button")).forEach(function(b){
      b.classList.toggle("es-on", b.dataset.irPag === hay.dataset.pag);
    });
    memo.pag = hay.dataset.pag; recuerda();
    if(arriba !== false) window.scrollTo(0, 0);
    if(lado) lado.classList.remove("is-abierto");
    return hay;
  }

  /* Ir a cualquier cosa por su identificador: abre su sección, y dentro de
     ella su apartado o su fase, y luego baja hasta ello. Un solo camino para
     todos los enlaces del sitio: así no hay saltos que dejen al lector en
     mitad de algo que no se ve. */
  function ir(id, suave){
    var el = D.getElementById(id);
    if(!el) return false;
    var pag = el.closest(".pag");
    if(pag) vePag(pag.dataset.pag, false);
    var fase = el.classList.contains("fase") ? el : el.closest(".fase");
    if(fase) abreFase(fase.dataset.fase, false);
    var hoja = el.classList.contains("hoja") ? el : el.closest(".hoja");
    if(hoja) veHoja(hoja.dataset.hoja, false);
    var blanco = fase || (hoja && hoja === el ? hoja : el);
    if(blanco && blanco.scrollIntoView){
      blanco.scrollIntoView({block:"start", behavior: suave ? "smooth" : "auto"});
    } else { window.scrollTo(0, 0); }
    try { history.replaceState(null, "", "#" + id); } catch(e){}
    return true;
  }

  D.addEventListener("click", function(e){
    var b = e.target.closest("[data-ir-pag]");
    if(b){
      e.preventDefault();
      var p = vePag(b.dataset.irPag, true);
      try { history.replaceState(null, "", "#" + p.id); } catch(err){}
      return;
    }
    var a = e.target.closest('a[href^="#"]');
    if(a && !a.classList.contains("fuera")){
      var destino = a.getAttribute("href").slice(1);
      if(D.getElementById(destino)){ e.preventDefault(); ir(destino, true); }
    }
  });

  /* ---------------------------------------------------------------- */
  /*  La primera visita y el recorrido: abrir una fase                  */
  /* ---------------------------------------------------------------- */
  var fases = [].slice.call(D.querySelectorAll(".fase"));
  function abreFase(clave, subir){
    var duena = null;
    fases.forEach(function(f){
      var si = f.dataset.fase === clave;
      if(si) duena = f;
      if(f.closest(".pag") === (D.getElementById(clave) || f).closest(".pag")){
        f.hidden = !si;
      } else if(si){ f.hidden = false; }
    });
    if(!duena) return;
    // las de su misma sección se cierran; las de otras, se quedan como estén
    [].slice.call(duena.closest(".pag").querySelectorAll(".fase")).forEach(function(f){
      f.hidden = f !== duena;
    });
    [].slice.call(duena.closest(".pag").querySelectorAll("[data-fase]")).forEach(function(b){
      if(b.classList.contains("fase")) return;
      b.classList.toggle("es-on", b.dataset.fase === clave);
    });
    if(subir !== false) duena.scrollIntoView({block:"start", behavior:"smooth"});
  }
  D.addEventListener("click", function(e){
    var b = e.target.closest("button[data-fase]");
    if(!b || b.classList.contains("fase")) return;
    abreFase(b.dataset.fase, true);
    try { history.replaceState(null, "", "#" + b.dataset.fase); } catch(err){}
  });

  /* las dos vistas de la primera visita */
  D.addEventListener("click", function(e){
    var b = e.target.closest(".vista");
    if(!b) return;
    var caja = b.closest(".bloque");
    [].slice.call(caja.querySelectorAll(".vista")).forEach(function(x){
      x.classList.toggle("es-on", x === b);
    });
    [].slice.call(caja.querySelectorAll(".vista__p")).forEach(function(p){
      p.hidden = p.dataset.vista !== b.dataset.vista;
    });
  });

  /* ---------------------------------------------------------------- */
  /*  Los puestos                                                       */
  /* ---------------------------------------------------------------- */
  D.addEventListener("click", function(e){
    var b = e.target.closest(".selpuesto");
    if(!b) return;
    [].slice.call(D.querySelectorAll(".selpuesto")).forEach(function(x){
      x.classList.toggle("es-on", x === b);
    });
    [].slice.call(D.querySelectorAll(".puesto")).forEach(function(p){
      p.hidden = p.dataset.puesto !== b.dataset.puesto;
    });
  });

  /* ---------------------------------------------------------------- */
  /*  El marketing: filtros sobre las setenta y seis acciones          */
  /* ---------------------------------------------------------------- */
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
    if(cuentaAcc){
      cuentaAcc.textContent = vivas === filas.length
        ? (filas.length + " acciones")
        : (vivas + " de " + filas.length + " acciones");
    }
    [].slice.call(D.querySelectorAll(".estado")).forEach(function(b){
      b.classList.toggle("es-on", false);
    });
  }
  [].slice.call(D.querySelectorAll("[data-filtro]")).forEach(function(s){
    s.addEventListener("change", filtra);
  });
  var limpia = D.getElementById("limpiafiltros");
  if(limpia) limpia.addEventListener("click", function(){
    [].slice.call(D.querySelectorAll("[data-filtro]")).forEach(function(s){ s.value = ""; });
    filtra();
  });
  /* Pulsar un estado filtra por el grupo que actúa sobre él: es lo que uno
     quiere saber al mirar «Dormido», no una lista de doce cosas más. */
  var GRUPO_DE = window.__GRUPOESTADO__ || {};
  D.addEventListener("click", function(e){
    var b = e.target.closest(".estado");
    if(!b) return;
    var sel = D.querySelector('[data-filtro="grupo"]');
    var g = GRUPO_DE[b.dataset.estado];
    if(sel && g){
      sel.value = (sel.value === g && b.classList.contains("es-on")) ? "" : g;
      filtra();
      b.classList.add("es-on");
      if(tabla) tabla.closest(".bloque").scrollIntoView({block:"start", behavior:"smooth"});
    }
  });
  filtra();

  /* ================================================================ */
  /*  LA BIBLIOTECA                                                    */
  /* ================================================================ */
  function veHoja(clave, arriba){
    if(!lectura) return;
    var h = porClave[clave] || porClave["portada"] || hojas[0];
    if(!h) return;
    hojas.forEach(function(x){ x.classList.toggle("is-on", x === h); });
    if(arbol){
      [].slice.call(arbol.querySelectorAll("a[data-ir]")).forEach(function(a){
        a.classList.toggle("is-on", a.dataset.ir === h.dataset.hoja);
      });
      if(h.dataset.doc !== undefined){
        var caja = arbol.querySelector('.lado__doc[data-doc="' + h.dataset.doc + '"]');
        if(caja && !caja.open) caja.open = true;
      }
      var vivo = arbol.querySelector('a[data-ir="' + h.dataset.hoja + '"]');
      if(vivo){
        var r = vivo.getBoundingClientRect(), c = arbol.getBoundingClientRect();
        if(r.top < c.top + 8 || r.bottom > c.bottom - 8) vivo.scrollIntoView({block:"center"});
      }
    }
    var i = claves.indexOf(h.dataset.hoja);
    if(miga){
      if(i < 0){ miga.innerHTML = "<b>Portada e índice completo</b>"; }
      else {
        var o = orden[i];
        miga.innerHTML = esc(o[1]) + (o[2] ? ' <em>&rsaquo;</em> ' + esc(o[2]) : "")
                       + ' <em>&rsaquo;</em> <b>' + esc(o[3]) + "</b>";
      }
    }
    if(cuenta) cuenta.textContent = i < 0 ? (claves.length + " apartados") : ((i+1) + " / " + claves.length);
    if(ant) ant.disabled = i <= 0;
    if(sig) sig.disabled = i < 0 || i >= claves.length - 1;
    if(i >= 0){ memo.ultimo = h.dataset.hoja; recuerda(); }
    var marco = D.querySelector(".marco");
    if(marco) marco.classList.toggle("marco--ancho", h.dataset.hoja === "portada");
    haceSumario(h);
    dibujaAvance();
    if(arriba !== false) window.scrollTo(0, 0);
  }
  function saltaHoja(paso){
    var viva = hojas.filter(function(h){ return h.classList.contains("is-on"); })[0];
    var i = viva ? claves.indexOf(viva.dataset.hoja) : -1;
    var j = i < 0 ? (paso > 0 ? 0 : -1) : i + paso;
    if(j >= 0 && j < claves.length){ veHoja(claves[j], true); }
  }
  if(ant) ant.addEventListener("click", function(){ saltaHoja(-1); });
  if(sig) sig.addEventListener("click", function(){ saltaHoja(1); });

  var vigilante = null;
  function haceSumario(h){
    if(!sumario) return;
    if(vigilante){ vigilante.disconnect(); vigilante = null; }
    var ts = [].slice.call(h.querySelectorAll("h2[id], h3[id]"))
               .filter(function(t){ return (t.textContent||"").trim().length > 1; });
    var esPortada = h.dataset.hoja === "portada";
    sumario.innerHTML =
      (ts.length > 1 ? '<p class="sumario__t">En este apartado</p><ol>'
        + ts.map(function(t){
            return '<li><a href="#' + t.id + '" data-suma="' + t.id + '">'
                 + esc(t.textContent.trim()) + "</a></li>"; }).join("") + "</ol>" : "")
      + (esPortada ? "" :
        '<div class="sumario__pie">'
        + '<button type="button" data-acto="enlace">Copiar enlace</button>'
        + '<button type="button" data-acto="imprimir">Imprimir este apartado</button>'
        + '<button type="button" data-acto="recursos">Recursos y descargas</button></div>');
    if(!ts.length || !("IntersectionObserver" in window)) return;
    var enl = {};
    [].slice.call(sumario.querySelectorAll("a[data-suma]")).forEach(function(a){ enl[a.dataset.suma] = a; });
    vigilante = new IntersectionObserver(function(es){
      es.forEach(function(en){
        if(!en.isIntersecting) return;
        var a = enl[en.target.id];
        if(!a) return;
        [].slice.call(sumario.querySelectorAll("a")).forEach(function(x){ x.classList.remove("is-aqui"); });
        a.classList.add("is-aqui");
      });
    }, {rootMargin:"-12% 0px -74% 0px"});
    ts.forEach(function(t){ vigilante.observe(t); });
  }
  if(sumario) sumario.addEventListener("click", function(e){
    var b = e.target.closest("button[data-acto]");
    if(!b) return;
    if(b.dataset.acto === "enlace") copia(location.href);
    if(b.dataset.acto === "imprimir") window.print();
    if(b.dataset.acto === "recursos") abre("recursos");
  });

  function dibujaAvance(){
    var leidos = Object.keys(memo.leidos).filter(function(k){ return memo.leidos[k]; }).length;
    if(avance && claves.length) avance.style.width = (100 * leidos / claves.length) + "%";
    if(!arbol) return;
    [].slice.call(arbol.querySelectorAll(".lado__doc")).forEach(function(d){
      var suyas = [].slice.call(d.querySelectorAll("a[data-ir]"));
      var hechas = suyas.filter(function(a){ return memo.leidos[a.dataset.ir]; });
      suyas.forEach(function(a){ a.classList.toggle("is-leido", !!memo.leidos[a.dataset.ir]); });
      var v = d.querySelector(".aro__v");
      if(v){
        var largo = 2 * Math.PI * 6.2;
        v.setAttribute("stroke-dasharray", largo.toFixed(2));
        v.setAttribute("stroke-dashoffset", (largo * (1 - hechas.length / (suyas.length||1))).toFixed(2));
      }
    });
    [].slice.call(D.querySelectorAll(".marca-leido")).forEach(function(b){
      var si = !!memo.leidos[b.dataset.hoja];
      b.setAttribute("aria-pressed", String(si));
      b.querySelector("b").textContent = si ? "Leído" : "Marcar leído";
    });
  }
  D.addEventListener("click", function(e){
    var b = e.target.closest(".marca-leido");
    if(!b) return;
    memo.leidos[b.dataset.hoja] = !memo.leidos[b.dataset.hoja];
    recuerda(); dibujaAvance();
    pita(memo.leidos[b.dataset.hoja] ? "Marcado como leído" : "Ya no está marcado");
  });

  var menu = D.getElementById("menu");
  if(menu) menu.addEventListener("click", function(){ if(lado) lado.classList.toggle("is-abierto"); });

  /* ================================================================ */
  /*  LO QUE FLOTA                                                     */
  /* ================================================================ */
  var velos = {}, ultimoFoco = null;
  [].slice.call(D.querySelectorAll(".velo")).forEach(function(v){ velos[v.dataset.velo] = v; });
  function abre(cual){
    cierra();
    var v = velos[cual];
    if(!v) return;
    ultimoFoco = D.activeElement;
    v.hidden = false;
    D.documentElement.style.overflow = "hidden";
    var f = v.querySelector("input, button, a");
    if(f) f.focus();
    if(cual === "paleta") pintaPaleta("");
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

  /* --- la paleta: secciones y apartados, en un solo sitio ---------- */
  var campo = D.getElementById("palq");
  var lista = D.getElementById("pallista");
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
      cache.push({id:b.dataset.irPag, doc:"Sección", grupo:"", rot:b.textContent.trim(),
                  n:"", crudo:"", txt:"", seccion:true});
    });
    hojas.filter(function(h){ return h.dataset.hoja !== "portada"; }).forEach(function(h){
      var o = orden[claves.indexOf(h.dataset.hoja)] || ["","","",""];
      var crudo = (h.innerText || h.textContent || "").replace(/\\s+/g," ");
      cache.push({id:h.dataset.hoja, doc:o[1], grupo:o[2], rot:o[3], n:(h.dataset.n||""),
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
         + '<span>' + esc(d.n || (d.seccion ? "→" : "·")) + "</span>"
         + '<b>' + esc(d.rot) + (q && !d.seccion ? '<span class="pal__ctx">' + trozo(d,q) + "</span>" : "") + "</b>"
         + '<i>' + esc(d.doc) + "</i></button>";
  }
  function pintaPaleta(q){
    q = llano((q||"").trim());
    var datos = indexa();
    var secs = datos.filter(function(d){ return d.seccion; });
    var aps  = datos.filter(function(d){ return !d.seccion; });
    if(!q){
      var recientes = [];
      if(memo.ultimo){
        var u = aps.filter(function(d){ return d.id === memo.ultimo; })[0];
        if(u) recientes.push(u);
      }
      lista.innerHTML = '<p class="pal__g">Las secciones</p>' + secs.map(function(d){ return fila(d,""); }).join("")
        + (recientes.length ? '<p class="pal__g">Donde lo dejó</p>' + recientes.map(function(d){ return fila(d,""); }).join("") : "")
        + '<p class="pal__g">Los apartados</p>' + aps.slice(0,20).map(function(d){ return fila(d,""); }).join("");
    } else {
      var s = secs.filter(function(d){ return llano(d.rot).indexOf(q) > -1; });
      var r = aps.filter(function(d){ return d.rotll.indexOf(q) > -1; });
      var x = aps.filter(function(d){ return d.rotll.indexOf(q) < 0 && d.txt.indexOf(q) > -1; });
      function entera(d){
        var i = d.txt.indexOf(q);
        if(i < 0) return false;
        var a = i ? d.txt[i-1] : " ", b = i+q.length < d.txt.length ? d.txt[i+q.length] : " ";
        return !/[a-z0-9]/.test(a) && !/[a-z0-9]/.test(b);
      }
      x.sort(function(m,n){ return (entera(n)?1:0) - (entera(m)?1:0); });
      if(!s.length && !r.length && !x.length){
        lista.innerHTML = '<p class="pal__nada">Nada con «' + esc(q) + '» en el sistema.</p>';
      } else {
        lista.innerHTML =
          (s.length ? '<p class="pal__g">Secciones</p>' + s.map(function(d){ return fila(d,""); }).join("") : "")
          + (r.length ? '<p class="pal__g">' + r.length + ' en el rótulo</p>' + r.map(function(d){ return fila(d,""); }).join("") : "")
          + (x.length ? '<p class="pal__g">' + x.length + ' en el texto</p>' + x.map(function(d){ return fila(d,q); }).join("") : "");
      }
    }
    elegido = 0; marcaElegido();
  }
  function marcaElegido(){
    var todos = [].slice.call(lista.querySelectorAll(".pal__i"));
    todos.forEach(function(b,n){ b.classList.toggle("es-aqui", n === elegido); });
    if(todos[elegido]) todos[elegido].scrollIntoView({block:"nearest"});
  }
  if(campo){
    campo.addEventListener("input", function(){ pintaPaleta(campo.value); });
    campo.addEventListener("keydown", function(e){
      var todos = [].slice.call(lista.querySelectorAll(".pal__i"));
      if(e.key === "ArrowDown"){ e.preventDefault(); elegido = Math.min(elegido+1, todos.length-1); marcaElegido(); }
      if(e.key === "ArrowUp"){ e.preventDefault(); elegido = Math.max(elegido-1, 0); marcaElegido(); }
      if(e.key === "Enter" && todos[elegido]){ e.preventDefault(); todos[elegido].click(); }
    });
  }
  if(lista) lista.addEventListener("click", function(e){
    var b = e.target.closest(".pal__i");
    if(!b) return;
    cierra(); campo.value = "";
    var v = b.dataset.va;
    if(porClave[v]){ vePag("biblioteca", true); veHoja(v, true); }
    else if(D.getElementById(v)) ir(v, false);
    else vePag(v, true);
  });

  /* --- el glosario -------------------------------------------------- */
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

  /* --- la lupa ------------------------------------------------------ */
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

  /* --- copiar, con aviso -------------------------------------------- */
  var pitido = D.getElementById("pito"), reloj = null;
  function pita(t){
    if(!pitido) return;
    pitido.textContent = t; pitido.hidden = false;
    clearTimeout(reloj);
    reloj = setTimeout(function(){ pitido.hidden = true; }, 1900);
  }
  function copia(t){
    if(navigator.clipboard && navigator.clipboard.writeText){
      navigator.clipboard.writeText(t).then(function(){ pita("Enlace copiado"); },
                                           function(){ pita("No se ha podido copiar"); });
    } else {
      var c = D.createElement("textarea");
      c.value = t; D.body.appendChild(c); c.select();
      try { D.execCommand("copy"); pita("Enlace copiado"); } catch(e){ pita("No se ha podido copiar"); }
      D.body.removeChild(c);
    }
  }

  /* --- teclado ------------------------------------------------------ */
  D.addEventListener("keydown", function(e){
    var t = e.target;
    var escribiendo = t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA"
                            || t.tagName === "SELECT" || t.isContentEditable);
    if(e.key === "Escape"){ if(cierra()) e.preventDefault(); return; }
    if((e.metaKey || e.ctrlKey) && (e.key === "k" || e.key === "K")){ e.preventDefault(); abre("paleta"); return; }
    if(escribiendo || e.ctrlKey || e.metaKey || e.altKey) return;
    if(e.key === "/"){ e.preventDefault(); abre("paleta"); return; }
    if(e.key === "?"){ e.preventDefault(); abre("teclas"); return; }
    if(e.key === "r" || e.key === "R"){ e.preventDefault(); abre("recursos"); return; }
    if(e.key === "g"){ vePag("inicio", true); return; }
    var enBib = D.querySelector(".pag.es-on") && D.querySelector(".pag.es-on").dataset.pag === "biblioteca";
    if(enBib && (e.key === "ArrowRight" || e.key === "j")) saltaHoja(1);
    if(enBib && (e.key === "ArrowLeft" || e.key === "k")) saltaHoja(-1);
  });

  window.addEventListener("hashchange", function(){
    var h = (location.hash || "").slice(1);
    if(h) ir(h, false);
  });

  var seguir = D.getElementById("seguir");
  if(seguir){
    if(memo.ultimo && porClave[memo.ultimo]){
      var o = orden[claves.indexOf(memo.ultimo)];
      if(o) seguir.textContent = "Seguir en «" + o[3] + "»";
      seguir.addEventListener("click", function(){ vePag("biblioteca", true); veHoja(memo.ultimo, true); });
    } else {
      seguir.addEventListener("click", function(){ vePag("biblioteca", true); veHoja("portada", true); });
    }
  }

  /* --- arranque ------------------------------------------------------ */
  if(lectura) veHoja("portada", false);
  var h0 = (location.hash || "").slice(1);
  if(h0 && D.getElementById(h0)){ ir(h0, false); }
  else { vePag(memo.pag || "inicio", false); }
  dibujaAvance();
})();
</script>
"""


PORTADA_BIB = """
<article class="hoja hoja--portada" id="portada" data-hoja="portada">
  <div class="idx">
    <div class="idx__cabeza">
      <p class="eyebrow">Índice completo</p>
      <h2>Todo lo que hay, y dónde está</h2>
      <p>Los ocho documentos del sistema con sus @TOTAL@ apartados, uno por uno, y debajo de cada
        uno los titulares que contiene. No hay nada fuera de esta lista: lo que no está aquí no
        está escrito. Son @MILES@ caracteres de literatura y @VOCES@ voces de glosario que se
        explican al pulsarlas. Con <kbd>⌘K</kbd> se busca en el texto de los ocho a la vez.</p>
    </div>
    @@INDICE@@
  </div>
</article>
"""

BIBLIOTECA = """
<section class="pag" id="biblioteca" data-pag="biblioteca">
  <div class="bibl">
    <aside class="lado" id="lado">
      <nav class="arbol" id="arbol" aria-label="Índice completo del sistema">
        <a class="arbol__inicio" href="#portada" data-ir="portada">Portada e índice completo</a>
        @@ARBOL@@
      </nav>
    </aside>
    <div>
      <div class="bibcima">
        <button class="icono" id="menu" type="button" aria-label="Índice">&#9776;</button>
        <nav class="miga" id="miga" aria-label="Dónde está"></nav>
        <span class="cima__n" id="cuenta"></span>
        <button class="icono" id="ant" type="button" aria-label="Anterior" title="Anterior (←)">&#8592;</button>
        <button class="icono" id="sig" type="button" aria-label="Siguiente" title="Siguiente (→)">&#8594;</button>
      </div>
      <div class="marco">
        <main class="lectura" id="lectura" tabindex="-1">
          @@PORTADA@@
          @@HOJAS@@
        </main>
        <aside class="sumario" id="sumario" aria-label="En este apartado"></aside>
      </div>
    </div>
  </div>
</section>
"""

MARCO = """
<a class="saltar" href="#sitio">Saltar al contenido</a>
<div class="avance" id="avance" aria-hidden="true"></div>

<header class="nav">
  <a class="nav__m" href="#inicio" data-ir-pag="inicio">El Centro <b>Giraldo</b><span>v@VERSION@</span></a>
  <nav class="nav__l" aria-label="Secciones">@@NAV@@</nav>
  <div class="nav__b">
    <button class="abrepal" type="button" data-abre="paleta">Buscar <kbd>⌘K</kbd></button>
    <button class="icono" type="button" data-abre="recursos" aria-label="Recursos" title="Recursos (R)">&#9781;</button>
    <button class="icono" type="button" data-abre="teclas" aria-label="Atajos" title="Atajos (?)">?</button>
  </div>
</header>

<div id="sitio">
@@SECCIONES@@
</div>

<footer class="nav" style="position:static;height:auto;padding:1.4rem 1.8rem;border-top:1px solid var(--line-soft);border-bottom:0;background:none;flex-wrap:wrap;gap:.8rem 2rem">
  <span style="font-size:.82rem;color:var(--muted)">Centro de Excelencia Implantológica Giraldo · Rúa Bolivia nº 2 · Vigo · Uso interno y confidencial</span>
  <span style="font-size:.82rem;color:var(--muted);margin-left:auto">v@VERSION@ · @FECHA@ · No medias sonrisas</span>
</footer>

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
    <div class="flota__pie">
      <span><kbd>&#8593;</kbd><kbd>&#8595;</kbd> moverse</span>
      <span><kbd>&#8629;</kbd> abrir</span>
      <span><kbd>Esc</kbd> cerrar</span>
    </div>
  </div>
</div>

<div class="velo" data-velo="recursos" role="dialog" aria-modal="true" aria-label="Recursos" hidden>
  <div class="flota">
    <div class="flota__cab"><h2>Recursos del sistema</h2>
      <button class="icono" type="button" data-cerrar aria-label="Cerrar">&#10005;</button></div>
    <div class="flota__cuerpo">@@RECURSOS@@</div>
    <div class="flota__pie"><span>Todo es de uso interno y confidencial.</span></div>
  </div>
</div>

<div class="velo" data-velo="teclas" role="dialog" aria-modal="true" aria-label="Atajos" hidden>
  <div class="flota" style="width:min(30rem,100%)">
    <div class="flota__cab"><h2>Atajos de teclado</h2>
      <button class="icono" type="button" data-cerrar aria-label="Cerrar">&#10005;</button></div>
    <div class="flota__cuerpo">
      <dl class="tec">
        <dt><kbd>&#8984;K</kbd> &middot; <kbd>/</kbd></dt><dd>Buscar secciones, apartados y texto</dd>
        <dt><kbd>G</kbd></dt><dd>Volver al inicio</dd>
        <dt><kbd>R</kbd></dt><dd>Recursos y descargas</dd>
        <dt><kbd>?</kbd></dt><dd>Esta ventana</dd>
        <dt><kbd>&#8594;</kbd> &middot; <kbd>&#8592;</kbd></dt><dd>En la biblioteca, apartado siguiente y anterior</dd>
        <dt><kbd>Esc</kbd></dt><dd>Cerrar lo que esté abierto</dd>
      </dl>
      <p style="margin:1.4rem 0 0;font-size:.86rem;color:var(--ink-2);line-height:1.6">
        Las siglas subrayadas —@EJEMPLO@— abren su definición al pulsarlas, y la definición es la
        que está escrita en el Manual, no una redacción nueva. Las figuras y las tablas anchas se
        ven de cerca pulsando encima. Lo que marque como leído en la biblioteca y la sección en la
        que estuvo se quedan en este navegador y no salen de aquí.
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


# ===========================================================================
#  LA PÁGINA
# ===========================================================================
def hoja_propia(doc, marca):
    for b in re.findall(r"<style>(.*?)</style>", fuente(doc), re.S):
        if marca in b:
            return b
    raise SystemExit("  %s: no se encuentra su hoja propia (%s)" % (doc, marca))


def guion_propio(doc, marca):
    for g in re.findall(r"<script>.*?</script>", fuente(doc), re.S):
        if marca in g:
            return g
    raise SystemExit("  %s: no se encuentra su guion propio (%s)" % (doc, marca))


NAV = [("inicio", "Inicio"), ("primera-visita", "La primera visita"), ("puestos", "Los puestos"),
       ("protocolos", "Los protocolos"), ("marketing", "El marketing"),
       ("gtc", "Giraldo Te Cuida"), ("numeros", "Los números"), ("biblioteca", "La biblioteca")]


def main():
    hojas, arbol, indice, orden, cuentas, ids = monta()
    total = sum(cuentas)
    caracteres = sum(len(sin_marcas(h)) for h in hojas)
    voces = glosario()

    # ------------------------------------------------------------------
    #  Las siete secciones y la biblioteca
    # ------------------------------------------------------------------
    portada_bib = PORTADA_BIB.replace("@@INDICE@@", "\n".join(indice)) \
        .replace("@TOTAL@", str(total)) \
        .replace("@MILES@", "{:,}".format(caracteres).replace(",", ".")) \
        .replace("@VOCES@", str(len(voces)))

    biblioteca = BIBLIOTECA.replace("@@ARBOL@@", "\n".join(arbol)) \
        .replace("@@PORTADA@@", portada_bib) \
        .replace("@@HOJAS@@", "\n".join(hojas)) \
        .replace("@TOTAL@", str(total))

    secciones = "\n".join([
        sec_inicio().replace("@TOTAL@", str(total)).replace("@VOCES@", str(len(voces))),
        sec_primera_visita(), sec_puestos(), sec_protocolos(),
        sec_marketing(), sec_gtc(), sec_numeros(), biblioteca,
    ])

    # ------------------------------------------------------------------
    #  Coser: aquí dentro está todo, así que casi ningún enlace sale
    # ------------------------------------------------------------------
    #  Las secciones nuevas enlazan al detalle con «#bib-ancla»; la biblioteca
    #  guarda el identificador real, que lleva el prefijo de su documento.
    def a_biblioteca(m):
        d = ids.get(m.group(1))
        return 'href="#%s"' % d if d else 'href="#biblioteca"'
    secciones = re.sub(r'href="#bib-([^"]+)"', a_biblioteca, secciones)

    # y lo que la literatura traía apuntando a otro documento
    docs_re = "|".join(re.escape(d) for d, *_ in DOCUMENTOS) + "|inicio.html"

    def ajeno(m):
        d = ids.get(m.group(2))
        return 'href="#%s"' % d if d else 'href="%s#%s" class="fuera"' % (m.group(1), m.group(2))
    secciones = re.sub(r'href="(%s)#([^"]+)"(?: class="fuera")?' % docs_re, ajeno, secciones)
    secciones = re.sub(r'href="(%s)"(?![^>]*class=)' % docs_re,
                       lambda m: 'href="%s" class="fuera"' % m.group(1), secciones)

    # La literatura que se trae a una sección conserva sus enlaces internos, y
    # esos apuntan a anclas de su documento que aquí viven en la biblioteca con
    # otro nombre. Se resuelven contra el mapa de identificadores; el que no
    # esté en ninguna parte deja de ser un enlace, que es mejor que un enlace
    # que no lleva a nada.
    presentes = set(re.findall(r'id="([^"]+)"', secciones))

    def suelto(m):
        destino = m.group(1)
        if destino in presentes:
            return m.group(0)
        d = ids.get(destino)
        return 'href="#%s"' % d if d else 'href="#biblioteca" class="fuera"'
    secciones = re.sub(r'href="#([^"]+)"', suelto, secciones)

    # ------------------------------------------------------------------
    #  Los recursos y los datos que necesita el guion
    # ------------------------------------------------------------------
    recursos = (
        '<div class="rec__g"><p class="rec__t">La entrega, cuatro archivos</p>'
        + "".join(
            ('<div class="rec__i" style="opacity:.62"><em>%s</em><div><b>%s</b>'
             '<p>%s Es la que está viendo.</p></div></div>' % (k, H.escape(n), H.escape(q)))
            if r == "centro.html" else
            ('<a class="rec__i" href="%s"%s><em>%s</em><div><b>%s</b><p>%s</p></div></a>'
             % (r, " download" if d else "", k, H.escape(n), H.escape(q)))
            for r, k, n, q, d in ENTREGA)
        + '</div><div class="rec__g"><p class="rec__t">Los ocho documentos, por separado</p>'
        + "".join(
            '<a class="rec__i" href="%s"><em>%02d</em><div><b>%s</b><p>%s</p></div></a>'
            % (doc, i + 1, H.escape(rot), H.escape(q))
            for i, (doc, rot, _c, q, _m) in enumerate(DOCUMENTOS))
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

    nav = "".join('<button type="button" data-ir-pag="%s">%s</button>' % (i, H.escape(r))
                  for i, r in NAV)

    cuerpo = (MARCO.replace("@@NAV@@", nav)
                   .replace("@@SECCIONES@@", secciones)
                   .replace("@@RECURSOS@@", recursos)
                   .replace("@TOTAL@", str(total))
                   .replace("@EJEMPLO@", ", ".join(sorted(voces)[:3])))

    # ------------------------------------------------------------------
    #  La cabeza: los tipos y el sistema visual del manual, más lo propio
    # ------------------------------------------------------------------
    manual = fuente("manual.html")
    i = manual.index("<body>")
    cabecera = manual[:i + len("<body>")]
    cabecera = cabecera.replace("<title>Manual Maestro Giraldo</title>",
                                "<title>El Centro Giraldo · el sistema completo</title>")
    cabecera = re.sub(
        r'<meta name="description" content="[^"]*">',
        '<meta name="description" content="El Centro de Excelencia Implantológica Giraldo: la '
        'primera visita minuto a minuto, los seis puestos, los protocolos, el marketing, el '
        'programa Giraldo Te Cuida, los números y los ocho documentos completos con sus %d '
        'apartados.">' % total, cabecera, count=1)
    extra = (CSS + "\n" + hoja_propia("protocolos.html", "PROTOCOLOS POR PUESTO")
             + "\n" + hoja_propia("instrumentos/captura.html", "HOJA DE CAPTURA")
             + "\n" + hoja_propia("deck.html", ".slide{"))
    k = cabecera.rindex("</style>")
    cabecera = cabecera[:k] + extra + "\n" + cabecera[k:]

    # El selector de puesto de la biblioteca viaja con su mando, acotado a la
    # hoja que lo lleva para que no toque el selector propio del sitio.
    selector = guion_propio("protocolos.html", "ES_PERFIL")
    selector = re.sub(r"\n\s*var actual = location\.hash.*?\n\s*\}\n", "\n", selector,
                      count=1, flags=re.S)
    selector = selector.replace('var h = (location.hash || "").replace(ES_PERFIL, "");', 'var h = "";')
    selector = selector.replace('var sel = document.querySelector(".selector");',
                                'var sel = document.querySelector(".hoja .selector");')

    datos = ("<script>window.__ORDEN__ = "
             + json.dumps([[c, d, g, r] for c, d, g, r in orden], ensure_ascii=False)
             + ";\nwindow.__VOCES__ = " + json.dumps(voces, ensure_ascii=False)
             + ";\nwindow.__GRUPOESTADO__ = " + json.dumps(grupo_de, ensure_ascii=False)
             + ";</script>")

    salida = RAIZ / "centro.html"
    texto = (cabecera + "\n" + cuerpo + "\n" + datos + "\n" + JS + "\n" + selector
             + "\n</body>\n</html>\n")
    texto = texto.replace("@VERSION@", VERSION).replace("@FECHA@", FECHA)
    salida.write_text(texto, encoding="utf-8")
    print("centro.html · 7 secciones + biblioteca · %d apartados · %d KB"
          % (total, salida.stat().st_size // 1024))


if __name__ == "__main__":
    main()
