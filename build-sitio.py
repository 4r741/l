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

    return hojas, arbol, indice, orden, cuentas


CSS = """
/* ===========================================================================
   EL CENTRO GIRALDO · EL SISTEMA COMPLETO

   Ocho documentos, ciento treinta y cinco apartados, ochocientos cincuenta mil
   caracteres. La página no compite con eso: se aparta. Una sola columna de
   texto, un índice a la izquierda, el sumario del apartado a la derecha y nada
   más encendido a la vez. Todo lo que hace falta de vez en cuando —buscar,
   consultar una sigla, ver una figura de cerca, saber qué teclas hay— aparece
   cuando se pide y desaparece al soltarlo.
   =========================================================================== */
:root{
  --lado:19rem; --sumario:15.5rem; --cima:3.25rem;
  --texto:70ch;
  --sombra-flota:0 18px 50px -12px rgba(18,35,43,.28), 0 2px 8px rgba(18,35,43,.08);
}
body{background:var(--paper)}
*:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:3px}

/* La barra de avance de la lectura: un pelo de dos píxeles arriba del todo.
   No es un adorno; con ciento treinta y cinco apartados, saber por dónde se va
   es la diferencia entre leer y perderse. */
.avance{position:fixed;inset:0 auto auto 0;height:2px;width:0;background:var(--accent);z-index:60;
  transition:width .12s linear}

.cen{display:grid;grid-template-columns:var(--lado) minmax(0,1fr);min-height:100vh}

/* --- el índice de la izquierda ------------------------------------------ */
.lado{
  position:sticky;top:0;height:100vh;display:flex;flex-direction:column;
  background:var(--surface);border-right:1px solid var(--line-soft);z-index:30;
}
.lado__cab{padding:1.1rem 1.05rem .9rem}
.lado__marca{display:block;text-decoration:none;color:var(--tinta)}
.lado__marca strong{font-family:var(--f-display);font-size:1.02rem;font-weight:500;letter-spacing:-.012em}
.lado__marca b{font-weight:600}
.lado__marca span{
  display:block;margin-top:.15rem;font-family:var(--f-mono);font-size:.62rem;
  letter-spacing:.13em;text-transform:uppercase;color:var(--muted);
}
.abrepal{
  display:flex;align-items:center;gap:.55rem;width:100%;margin-top:.9rem;padding:.5rem .75rem;
  background:var(--surface-2);border:1px solid var(--line-soft);border-radius:8px;
  color:var(--muted);font:inherit;font-size:.85rem;cursor:pointer;text-align:left;
}
.abrepal:hover{border-color:var(--line);color:var(--ink-2)}
.abrepal span{flex:1}
.abrepal kbd{
  font-family:var(--f-mono);font-size:.62rem;color:var(--muted);background:var(--surface);
  border:1px solid var(--line-soft);border-radius:4px;padding:.16rem .32rem;line-height:1;
}
.arbol{flex:1;overflow-y:auto;padding:.2rem .55rem 2.5rem;scrollbar-width:thin}
.arbol::-webkit-scrollbar{width:8px}
.arbol::-webkit-scrollbar-thumb{background:var(--line);border-radius:9px;border:2px solid var(--surface)}
.arbol__inicio{
  display:block;text-decoration:none;padding:.5rem .65rem;border-radius:7px;
  color:var(--ink-2);font-size:.86rem;font-weight:500;margin:.2rem 0 .5rem;
}
.arbol__inicio:hover{background:var(--surface-2);color:var(--ink)}
.arbol__inicio.is-on{background:var(--acido);color:var(--accent-fuerte)}
.lado__doc > summary{
  display:flex;align-items:center;gap:.55rem;cursor:pointer;list-style:none;
  padding:.55rem .65rem;border-radius:7px;
}
.lado__doc > summary::-webkit-details-marker{display:none}
.lado__doc > summary:hover{background:var(--surface-2)}
.lado__doc > summary b{font-family:var(--f-mono);font-size:.64rem;color:var(--muted);font-weight:500}
.lado__doc > summary span{flex:1;font-size:.86rem;font-weight:600;color:var(--tinta);line-height:1.3}
.lado__doc > summary i{font-style:normal;flex:none;display:block;width:1.05rem;height:1.05rem}
.lado__doc[open] > summary span{color:var(--accent-ink)}
/* El anillo de progreso de cada documento: cuánto de él se ha marcado leído.
   Es la única cifra de la página que cambia sola, y por eso no lleva número. */
.aro{transform:rotate(-90deg)}
.aro circle{fill:none;stroke-width:2.4}
.aro .aro__f{stroke:var(--line)}
.aro .aro__v{stroke:var(--accent);stroke-linecap:round;transition:stroke-dashoffset .3s ease}
.lado__ramas{padding:0 0 .55rem .3rem;margin-left:.95rem;border-left:1px solid var(--line-soft)}
.lado__gt{
  margin:.65rem 0 .2rem;padding-left:.65rem;font-family:var(--f-mono);font-size:.58rem;
  letter-spacing:.14em;text-transform:uppercase;color:var(--muted);
}
.lado__ramas a{
  display:flex;gap:.5rem;align-items:baseline;text-decoration:none;color:var(--ink-2);
  font-size:.81rem;line-height:1.36;padding:.32rem .5rem;border-radius:6px;position:relative;
}
.lado__ramas a span{font-family:var(--f-mono);font-size:.6rem;color:var(--muted);flex:none;min-width:1rem}
.lado__ramas a:hover{background:var(--surface-2);color:var(--ink)}
.lado__ramas a.is-on{background:var(--acido);color:var(--accent-fuerte);font-weight:600}
.lado__ramas a.is-on span{color:var(--accent-ink)}
.lado__ramas a.is-leido::after{
  content:"";position:absolute;right:.45rem;top:50%;width:5px;height:5px;border-radius:50%;
  background:var(--accent);transform:translateY(-50%);opacity:.55;
}
.lado__doc.is-fuera,.lado__ramas a.is-fuera,.lado__gt.is-fuera{display:none}

/* --- la cima ------------------------------------------------------------- */
.cen__col{min-width:0;display:flex;flex-direction:column}
.cima{
  position:sticky;top:0;z-index:25;display:flex;align-items:center;gap:.9rem;
  height:var(--cima);padding:0 1.5rem;background:rgba(246,248,249,.88);
  backdrop-filter:saturate(1.5) blur(10px);border-bottom:1px solid var(--line-soft);
}
.miga{flex:1;min-width:0;display:flex;align-items:center;gap:.45rem;font-size:.8rem;
  color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.miga b{color:var(--tinta);font-weight:600}
.miga em{font-style:normal;color:var(--line)}
.cima__n{font-family:var(--f-mono);font-size:.66rem;color:var(--muted);white-space:nowrap}
.icono{
  font:inherit;cursor:pointer;display:inline-flex;align-items:center;justify-content:center;
  width:1.9rem;height:1.9rem;border-radius:6px;border:1px solid transparent;
  background:none;color:var(--muted);line-height:1;
}
.icono:hover:not(:disabled){background:var(--surface);border-color:var(--line-soft);color:var(--ink)}
.icono:disabled{opacity:.3;cursor:default}
.cima__sep{width:1px;height:1.2rem;background:var(--line-soft)}
.cima__menu{display:none}

/* --- la lectura: una columna y nada alrededor ---------------------------- */
.marco{flex:1;display:grid;grid-template-columns:minmax(0,1fr) var(--sumario);
  gap:2.6rem;padding:2.6rem 2.4rem 7rem;max-width:78rem;margin:0 auto;width:100%}
.lectura{min-width:0}
.hoja{max-width:var(--texto);margin:0 auto}
.hoja__de{
  margin:0 0 2rem;font-family:var(--f-mono);font-size:.64rem;letter-spacing:.13em;
  text-transform:uppercase;color:var(--muted);display:flex;flex-wrap:wrap;gap:.55rem;align-items:center;
}
.hoja__de span{color:var(--accent)}
.hoja .wrap{padding:0;max-width:none}
.hoja .section{padding:0;background:none;border:0}
.hoja .section + .section{margin-top:3.2rem;padding-top:3.2rem;border-top:1px solid var(--line-soft)}
.hoja .reveal{opacity:1!important;transform:none!important}
.hoja .phase__grid{grid-template-columns:minmax(0,1fr)}
.hoja .phase__meta{position:static}
.hoja .tablewrap{overflow-x:auto;margin-inline:calc(-1 * var(--sangra,0px))}
a.fuera::after{content:"↗";font-size:.76em;margin-left:.18em;color:var(--muted)}

/* El pie de cada apartado: marcarlo leído y pasar al siguiente. Dos cosas. */
.remate{
  display:flex;flex-wrap:wrap;gap:.7rem;align-items:center;justify-content:space-between;
  margin-top:4rem;padding-top:1.6rem;border-top:1px solid var(--line-soft);
}
.marca-leido{
  display:inline-flex;align-items:center;gap:.5rem;font:inherit;font-size:.85rem;cursor:pointer;
  border:1px solid var(--line);background:var(--surface);color:var(--ink-2);
  border-radius:999px;padding:.45rem .95rem;
}
.marca-leido:hover{border-color:var(--accent);color:var(--accent-ink)}
.marca-leido[aria-pressed="true"]{background:var(--acido);border-color:var(--acido);color:var(--accent-fuerte)}
.marca-leido b{font-family:var(--f-mono);font-size:.8rem}
.remate a{
  text-decoration:none;font-size:.85rem;color:var(--ink-2);display:inline-flex;gap:.5rem;align-items:center;
}
.remate a:hover{color:var(--accent-ink)}
.remate a i{font-style:normal;font-family:var(--f-mono);font-size:.66rem;color:var(--muted)}

/* --- el sumario del apartado, a la derecha ------------------------------- */
.sumario{position:sticky;top:calc(var(--cima) + 2.6rem);align-self:start;max-height:calc(100vh - var(--cima) - 4rem);
  overflow-y:auto;scrollbar-width:none}
.sumario::-webkit-scrollbar{display:none}
.sumario__t{
  margin:0 0 .8rem;font-family:var(--f-mono);font-size:.6rem;letter-spacing:.15em;
  text-transform:uppercase;color:var(--muted);
}
.sumario ol{list-style:none;margin:0;padding:0;border-left:1px solid var(--line-soft)}
.sumario a{
  display:block;text-decoration:none;color:var(--muted);font-size:.79rem;line-height:1.4;
  padding:.3rem 0 .3rem .8rem;margin-left:-1px;border-left:2px solid transparent;
}
.sumario a:hover{color:var(--ink)}
.sumario a.is-aqui{color:var(--accent-ink);border-left-color:var(--accent);font-weight:600}
.sumario__pie{margin-top:1.4rem;padding-top:1rem;border-top:1px solid var(--line-soft);
  display:flex;flex-direction:column;gap:.35rem}
.sumario__pie button{
  font:inherit;font-size:.79rem;cursor:pointer;background:none;border:0;padding:.2rem 0;
  color:var(--muted);text-align:left;
}
.sumario__pie button:hover{color:var(--accent-ink)}

/* --- portada ------------------------------------------------------------- */
.hoja--portada{max-width:none}
/* En la portada no hay sumario que enseñar —el índice completo ya está en el
   cuerpo— y reservarle la columna dejaba el pórtico estrecho y descentrado. */
.marco--ancho{grid-template-columns:minmax(0,1fr)}
.marco--ancho .sumario{display:none}
.portico{background:var(--tinta);color:#fff;padding:4.4rem 3rem 3.6rem;border-radius:14px}
.portico .eyebrow{color:rgba(255,255,255,.45)}
.portico h1{font-size:clamp(2.5rem,5.6vw,4.2rem);line-height:1.04;letter-spacing:-.03em;margin:1.2rem 0 0}
.portico h1 em{font-style:normal;color:var(--acido);display:block}
.portico__p{margin:1.7rem 0 0;font-family:var(--f-display);font-size:clamp(1rem,1.9vw,1.28rem);
  line-height:1.45;color:rgba(255,255,255,.82);max-width:44ch}
.portico__p small{display:block;margin-top:.7rem;font-family:var(--f-mono);font-size:.65rem;
  letter-spacing:.13em;text-transform:uppercase;color:rgba(255,255,255,.38)}
.portico__b{display:flex;flex-wrap:wrap;gap:.6rem;margin-top:2.4rem}
.portico__b button{
  font:inherit;font-size:.86rem;cursor:pointer;border-radius:999px;padding:.6rem 1.15rem;
  border:1px solid rgba(255,255,255,.22);background:transparent;color:#fff;
}
.portico__b button:hover{border-color:var(--acido);color:var(--acido)}
.portico__b button.es-fuerte{background:var(--acido);border-color:var(--acido);color:var(--tinta);font-weight:600}
.portico__c{display:flex;flex-wrap:wrap;gap:2.4rem;margin-top:2.8rem;padding-top:1.7rem;
  border-top:1px solid rgba(255,255,255,.14)}
.portico__c b{display:block;font-family:var(--f-display);font-size:1.6rem;color:var(--acido)}
.portico__c span{display:block;margin-top:.25rem;font-family:var(--f-mono);font-size:.62rem;
  letter-spacing:.13em;text-transform:uppercase;color:rgba(255,255,255,.45)}

.idx{margin-top:3rem}
.idx__cabeza{padding:0 0 1.2rem;border-bottom:1px solid var(--line);margin-bottom:2rem}
.idx__cabeza h2{margin:.45rem 0 0;font-size:clamp(1.6rem,3.2vw,2.3rem);letter-spacing:-.024em}
.idx__cabeza p{margin:.7rem 0 0;color:var(--ink-2);max-width:62ch;line-height:1.62}
.idx__doc{padding:1.9rem 0 2.1rem;border-bottom:1px solid var(--line-soft)}
.idx__cab h3{margin:.4rem 0 0;font-size:1.4rem;letter-spacing:-.018em;display:flex;gap:.8rem;align-items:baseline}
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

/* ===========================================================================
   LO QUE APARECE CUANDO SE PIDE
   Un solo lienzo para todo lo que flota: paleta, glosario, recursos, teclas y
   la lupa de las figuras. Mismo fondo, misma sombra, misma manera de cerrarse.
   =========================================================================== */
.velo{
  position:fixed;inset:0;z-index:80;display:flex;align-items:flex-start;justify-content:center;
  padding:8vh 1.2rem 1.2rem;background:rgba(18,35,43,.34);
  backdrop-filter:blur(3px);animation:vela .14s ease;
}
@keyframes vela{from{opacity:0}to{opacity:1}}
.velo[hidden]{display:none}
.flota{
  width:min(44rem,100%);max-height:82vh;display:flex;flex-direction:column;overflow:hidden;
  background:var(--surface);border-radius:13px;box-shadow:var(--sombra-flota);
  animation:sube .16s cubic-bezier(.2,.7,.3,1);
}
@keyframes sube{from{opacity:0;transform:translateY(8px) scale(.99)}to{opacity:1;transform:none}}
@media(prefers-reduced-motion:reduce){.velo,.flota{animation:none}}
.flota__cab{display:flex;align-items:center;gap:.7rem;padding:.85rem 1.1rem;border-bottom:1px solid var(--line-soft)}
.flota__cab h2{margin:0;font-size:1rem;font-weight:600;flex:1}
.flota__cab .icono{margin-right:-.35rem}
.flota__cuerpo{overflow-y:auto;padding:1.1rem 1.3rem 1.4rem}
.flota__pie{
  padding:.6rem 1.1rem;border-top:1px solid var(--line-soft);background:var(--surface-2);
  font-family:var(--f-mono);font-size:.63rem;letter-spacing:.08em;color:var(--muted);
  display:flex;gap:1.1rem;flex-wrap:wrap;
}
.flota__pie kbd{background:var(--surface);border:1px solid var(--line-soft);border-radius:4px;
  padding:.1rem .3rem;font-family:inherit}

/* --- la paleta ----------------------------------------------------------- */
.pal__campo{display:flex;align-items:center;gap:.7rem;padding:1rem 1.2rem;border-bottom:1px solid var(--line-soft)}
.pal__campo input{flex:1;border:0;outline:none;background:none;font:inherit;font-size:1.02rem;color:var(--ink)}
.pal__campo input::placeholder{color:var(--muted)}
.pal__campo input::-webkit-search-cancel-button{-webkit-appearance:none;appearance:none}
.pal__lista{overflow-y:auto;padding:.45rem;max-height:56vh}
.pal__g{
  margin:.7rem .6rem .35rem;font-family:var(--f-mono);font-size:.6rem;letter-spacing:.15em;
  text-transform:uppercase;color:var(--muted);
}
.pal__i{
  display:flex;gap:.8rem;align-items:baseline;width:100%;text-align:left;font:inherit;cursor:pointer;
  background:none;border:0;border-radius:8px;padding:.55rem .6rem;color:var(--ink-2);
}
.pal__i span{font-family:var(--f-mono);font-size:.62rem;color:var(--muted);flex:none;min-width:1.5rem}
.pal__i b{font-weight:500;font-size:.93rem;line-height:1.35}
.pal__i i{font-style:normal;font-size:.75rem;color:var(--muted);margin-left:auto;flex:none;padding-left:1rem}
.pal__i mark{background:var(--acido);color:var(--accent-fuerte);padding:0 .1em;border-radius:2px}
.pal__i:hover,.pal__i.es-aqui{background:var(--surface-2)}
.pal__i.es-aqui{background:var(--acido)}
.pal__i.es-aqui b{color:var(--accent-fuerte)}
.pal__nada{padding:2rem 1rem;text-align:center;color:var(--muted);font-size:.9rem}
.pal__i b .pal__ctx{display:block;font-family:var(--f-texto,inherit);font-size:.78rem;
  font-weight:400;color:var(--muted);margin-top:.25rem;line-height:1.5;letter-spacing:0}

/* --- el glosario, en una tarjeta que sale donde se pulsa ----------------- */
.gl{
  font:inherit;cursor:help;background:none;border:0;padding:0;color:inherit;
  border-bottom:1px dashed var(--accent);
}
.gl:hover{color:var(--accent-ink)}
.voz{
  position:absolute;z-index:90;width:min(22rem,calc(100vw - 2rem));
  background:var(--surface);border:1px solid var(--line);border-radius:10px;
  box-shadow:var(--sombra-flota);padding:.95rem 1.05rem 1rem;
}
.voz[hidden]{display:none}
.voz b{display:block;font-family:var(--f-display);font-size:1rem;color:var(--tinta)}
.voz p{margin:.45rem 0 0;font-size:.88rem;line-height:1.55;color:var(--ink-2)}
.voz small{
  display:block;margin-top:.7rem;padding-top:.6rem;border-top:1px solid var(--line-soft);
  font-family:var(--f-mono);font-size:.6rem;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);
}

/* --- recursos ------------------------------------------------------------ */
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

/* --- teclas -------------------------------------------------------------- */
.tec{display:grid;grid-template-columns:auto 1fr;gap:.5rem 1.1rem;align-items:baseline}
.tec dt{font-family:var(--f-mono);font-size:.72rem;color:var(--tinta);white-space:nowrap}
.tec dt kbd{background:var(--surface-2);border:1px solid var(--line-soft);border-radius:5px;
  padding:.15rem .4rem;font-family:inherit}
.tec dd{margin:0;font-size:.87rem;color:var(--ink-2);line-height:1.5}

/* --- la lupa de las figuras ---------------------------------------------- */
.lupa{align-items:center;padding:3vh 3vw}
.lupa .flota{width:min(72rem,100%);max-height:94vh;background:var(--surface)}
.lupa__lienzo{padding:1.8rem 2rem 2rem;overflow:auto}
.lupa__lienzo > *{max-width:100%;margin:0}
.lupa__lienzo figcaption,.lupa__lienzo .fig__pie,.lupa__lienzo .t-fig__note{
  margin-top:1.2rem;padding-top:1rem;border-top:1px solid var(--line-soft);
  font-size:.88rem;line-height:1.6;color:var(--ink-2);max-width:74ch;
}
.lupa__lienzo svg{width:100%;height:auto}
.ampliable{cursor:zoom-in}

/* --- avisos efímeros ------------------------------------------------------ */
.pito{
  position:fixed;left:50%;bottom:2rem;transform:translateX(-50%);z-index:95;
  background:var(--tinta);color:#fff;border-radius:999px;padding:.6rem 1.2rem;
  font-size:.85rem;box-shadow:var(--sombra-flota);animation:sube .16s ease;
}
.pito[hidden]{display:none}

/* Con guiones se lee un apartado cada vez; sin ellos —y al imprimir— se ven
   los ciento treinta y cinco seguidos, que es el sistema entero. La marca la
   pone el instalador: si el guion no llegara a correr, no queda una página en
   blanco sino el documento completo. */
.lectura--viva .hoja{display:none}
.lectura--viva .hoja.is-on{display:block}

@media(max-width:1240px){
  .marco{grid-template-columns:minmax(0,1fr);gap:0}
  .sumario{display:none}
}
@media(max-width:1080px){
  .cen{grid-template-columns:minmax(0,1fr)}
  .lado{position:fixed;inset:0 auto 0 0;width:min(21rem,86vw);transform:translateX(-101%);
    transition:transform .2s ease;box-shadow:0 0 40px rgba(18,35,43,.2)}
  .lado.is-abierto{transform:none}
  .cima__menu{display:inline-flex}
  .marco{padding:1.5rem 1.1rem 5rem}
  .portico{padding:2.8rem 1.4rem 2.4rem}
  .idx__lista{columns:1}
  .velo{padding:4vh .8rem .8rem}
}
@media print{
  .lado,.cima,.sumario,.velo,.voz,.avance,.remate,.pito{display:none}
  .cen,.marco{display:block;padding:0;max-width:none}
  .lectura--viva .hoja{display:block;break-after:page}
  .gl{border:0}
}
"""


JS = """
<script>
(function(){
  "use strict";
  var D = document;
  var lectura = D.getElementById("lectura");
  if(!lectura) return;

  var hojas   = [].slice.call(lectura.querySelectorAll(".hoja"));
  var orden   = window.__ORDEN__ || [];
  var VOCES   = window.__VOCES__ || {};
  var lado    = D.getElementById("lado");
  var arbol   = D.getElementById("arbol");
  var miga    = D.getElementById("miga");
  var cuenta  = D.getElementById("cuenta");
  var ant     = D.getElementById("ant");
  var sig     = D.getElementById("sig");
  var avance  = D.getElementById("avance");
  var sumario = D.getElementById("sumario");
  if(!hojas.length) return;

  /* La marca la pone el guion y no el marcado: si esto no llegara a correr se
     ven los ciento treinta y cinco apartados seguidos —el sistema entero— en
     vez de quedarse la página en blanco. */
  lectura.classList.add("lectura--viva");

  var porClave = {};
  hojas.forEach(function(h){ porClave[h.dataset.hoja] = h; });
  var claves = orden.map(function(o){ return o[0]; });

  /* ------------------------------------------------------------------ */
  /*  Lo que se recuerda de una visita a otra: nada del contenido, solo  */
  /*  por dónde iba uno y qué daba por leído. Vive en este navegador y   */
  /*  no sale de aquí.                                                    */
  /* ------------------------------------------------------------------ */
  var LLAVE = "giraldo.centro.v8";
  var memo = {leidos: {}, ultimo: ""};
  try {
    var guardado = localStorage.getItem(LLAVE);
    if(guardado) memo = JSON.parse(guardado) || memo;
    if(!memo.leidos) memo.leidos = {};
  } catch(e){}
  function recuerda(){
    try { localStorage.setItem(LLAVE, JSON.stringify(memo)); } catch(e){}
  }

  /* ------------------------------------------------------------------ */
  /*  Ir a un apartado                                                   */
  /* ------------------------------------------------------------------ */
  function pon(clave, arriba){
    var h = porClave[clave] || porClave["portada"] || hojas[0];
    hojas.forEach(function(x){ x.classList.toggle("is-on", x === h); });

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

    var i = claves.indexOf(h.dataset.hoja);
    if(miga){
      if(i < 0){ miga.innerHTML = "<b>Portada e índice completo</b>"; }
      else {
        var o = orden[i];
        miga.innerHTML = esc(o[1]) + (o[2] ? ' <em>&rsaquo;</em> ' + esc(o[2]) : "")
                       + ' <em>&rsaquo;</em> <b>' + esc(o[3]) + "</b>";
      }
    }
    if(cuenta) cuenta.textContent = i < 0 ? (claves.length + " apartados") : ((i + 1) + " / " + claves.length);
    if(ant) ant.disabled = i <= 0;
    if(sig) sig.disabled = i < 0 || i >= claves.length - 1;

    if(i >= 0){ memo.ultimo = h.dataset.hoja; recuerda(); }
    var marco = D.querySelector(".marco");
    if(marco) marco.classList.toggle("marco--ancho", h.dataset.hoja === "portada");
    haceSumario(h);
    dibujaAvance();
    try { history.replaceState(null, "", "#" + h.dataset.hoja); } catch(e){}
    if(arriba !== false) window.scrollTo(0, 0);
    if(lado) lado.classList.remove("is-abierto");
  }

  function salta(paso){
    var viva = hojas.filter(function(h){ return h.classList.contains("is-on"); })[0];
    var i = viva ? claves.indexOf(viva.dataset.hoja) : -1;
    var j = i < 0 ? (paso > 0 ? 0 : -1) : i + paso;
    if(j >= 0 && j < claves.length) pon(claves[j], true);
  }
  if(ant) ant.addEventListener("click", function(){ salta(-1); });
  if(sig) sig.addEventListener("click", function(){ salta(1); });

  function esc(s){
    return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
  }

  /* ------------------------------------------------------------------ */
  /*  El sumario del apartado, a la derecha, con la señal de dónde se va */
  /* ------------------------------------------------------------------ */
  var vigilante = null;
  function haceSumario(h){
    if(!sumario) return;
    if(vigilante){ vigilante.disconnect(); vigilante = null; }
    var titulares = [].slice.call(h.querySelectorAll("h2[id], h3[id]"))
                      .filter(function(t){ return (t.textContent || "").trim().length > 1; });
    var clave = h.dataset.hoja;
    var leido = !!memo.leidos[clave];
    var esPortada = clave === "portada";

    sumario.innerHTML =
      (titulares.length > 1
        ? '<p class="sumario__t">En este apartado</p><ol>'
          + titulares.map(function(t){
              return '<li><a href="#' + t.id + '" data-suma="' + t.id + '">' + esc(t.textContent.trim()) + "</a></li>";
            }).join("") + "</ol>"
        : "")
      + (esPortada ? "" :
         '<div class="sumario__pie">'
         + '<button type="button" data-acto="enlace">Copiar enlace</button>'
         + '<button type="button" data-acto="imprimir">Imprimir este apartado</button>'
         + '<button type="button" data-acto="recursos">Recursos y descargas</button>'
         + "</div>");

    if(!titulares.length || !("IntersectionObserver" in window)) return;
    var enlaces = {};
    [].slice.call(sumario.querySelectorAll("a[data-suma]")).forEach(function(a){
      enlaces[a.dataset.suma] = a;
    });
    vigilante = new IntersectionObserver(function(entradas){
      entradas.forEach(function(en){
        if(!en.isIntersecting) return;
        var a = enlaces[en.target.id];
        if(!a) return;
        [].slice.call(sumario.querySelectorAll("a")).forEach(function(x){ x.classList.remove("is-aqui"); });
        a.classList.add("is-aqui");
      });
    }, {rootMargin:"-12% 0px -74% 0px"});
    titulares.forEach(function(t){ vigilante.observe(t); });
  }

  if(sumario){
    sumario.addEventListener("click", function(e){
      var b = e.target.closest("button[data-acto]");
      if(!b) return;
      if(b.dataset.acto === "enlace") copia(location.href);
      if(b.dataset.acto === "imprimir") window.print();
      if(b.dataset.acto === "recursos") abre("recursos");
    });
  }

  /* ------------------------------------------------------------------ */
  /*  Marcar leído, el aro de cada documento y la barra de avance        */
  /* ------------------------------------------------------------------ */
  function dibujaAvance(){
    var leidos = Object.keys(memo.leidos).filter(function(k){ return memo.leidos[k]; }).length;
    if(avance) avance.style.width = (100 * leidos / claves.length) + "%";
    [].slice.call(arbol.querySelectorAll(".lado__doc")).forEach(function(d){
      var suyas = [].slice.call(d.querySelectorAll("a[data-ir]"));
      var hechas = suyas.filter(function(a){ return memo.leidos[a.dataset.ir]; });
      suyas.forEach(function(a){ a.classList.toggle("is-leido", !!memo.leidos[a.dataset.ir]); });
      var v = d.querySelector(".aro__v");
      if(v){
        var largo = 2 * Math.PI * 6.2;
        v.setAttribute("stroke-dasharray", largo.toFixed(2));
        v.setAttribute("stroke-dashoffset", (largo * (1 - hechas.length / (suyas.length || 1))).toFixed(2));
      }
    });
    [].slice.call(lectura.querySelectorAll(".marca-leido")).forEach(function(b){
      var si = !!memo.leidos[b.dataset.hoja];
      b.setAttribute("aria-pressed", String(si));
      b.querySelector("b").textContent = si ? "Leído" : "Marcar leído";
    });
  }

  lectura.addEventListener("click", function(e){
    var b = e.target.closest(".marca-leido");
    if(!b) return;
    memo.leidos[b.dataset.hoja] = !memo.leidos[b.dataset.hoja];
    recuerda(); dibujaAvance();
    pita(memo.leidos[b.dataset.hoja] ? "Marcado como leído" : "Ya no está marcado");
  });

  /* ------------------------------------------------------------------ */
  /*  Enlaces internos: nunca se sale del sitio                          */
  /* ------------------------------------------------------------------ */
  D.addEventListener("click", function(e){
    var a = e.target.closest('a[href^="#"]');
    if(!a || a.classList.contains("fuera")) return;
    var destino = D.getElementById(a.getAttribute("href").slice(1));
    if(!destino) return;
    var duena = destino.closest(".hoja");
    if(!duena) return;
    e.preventDefault();
    if(!duena.classList.contains("is-on")) pon(duena.dataset.hoja, true);
    if(destino !== duena){
      destino.scrollIntoView({block:"start", behavior:"smooth"});
      try { history.replaceState(null, "", a.getAttribute("href")); } catch(err){}
    }
  });

  var menu = D.getElementById("menu");
  if(menu) menu.addEventListener("click", function(){ lado.classList.toggle("is-abierto"); });

  /* ================================================================== */
  /*  LO QUE FLOTA                                                       */
  /* ================================================================== */
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
    Object.keys(velos).forEach(function(k){
      if(!velos[k].hidden){ velos[k].hidden = true; abierto = true; }
    });
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
  [].slice.call(D.querySelectorAll("[data-abre]")).forEach(function(b){
    b.addEventListener("click", function(){ abre(b.dataset.abre); });
  });

  /* --- la paleta: buscar y saltar, todo con el teclado --------------- */
  var campo = D.getElementById("palq");
  var lista = D.getElementById("pallista");
  var cache = null, resultados = [], elegido = 0;

  var CON = "\\u00e1\\u00e0\\u00e4\\u00e2\\u00e3\\u00e9\\u00e8\\u00eb\\u00ea\\u00ed\\u00ec\\u00ef\\u00ee"
          + "\\u00f3\\u00f2\\u00f6\\u00f4\\u00f5\\u00fa\\u00f9\\u00fc\\u00fb\\u00f1\\u00e7";
  var SIN = "aaaaaeeeeiiiiooooouuuunc";
  /* Quita acentos SIN cambiar la longitud: el trozo que se enseña sale del
     texto original y hay que poder cortarlo por el mismo sitio. */
  function llano(s){
    s = String(s).toLowerCase();
    var f = "";
    for(var i = 0; i < s.length; i++){
      var j = CON.indexOf(s[i]);
      f += j < 0 ? s[i] : SIN[j];
    }
    return f;
  }
  function indexa(){
    if(cache) return cache;
    cache = hojas.filter(function(h){ return h.dataset.hoja !== "portada"; }).map(function(h){
      var o = orden[claves.indexOf(h.dataset.hoja)] || ["", "", "", ""];
      var crudo = (h.innerText || h.textContent || "").replace(/\\s+/g, " ");
      return {clave:h.dataset.hoja, doc:o[1], grupo:o[2], rot:o[3],
              n:(h.dataset.n || ""), crudo:crudo, txt:llano(crudo), rotll:llano(o[3])};
    });
    return cache;
  }
  function trozo(d, q){
    var i = d.txt.indexOf(q);
    if(i < 0) return "";
    var a = Math.max(0, i - 60), b = Math.min(d.crudo.length, i + q.length + 110);
    return (a ? "…" : "") + esc(d.crudo.slice(a, i)) + "<mark>" + esc(d.crudo.slice(i, i + q.length))
         + "</mark>" + esc(d.crudo.slice(i + q.length, b)) + (b < d.crudo.length ? "…" : "");
  }
  function pintaPaleta(q){
    q = llano((q || "").trim());
    var datos = indexa();
    if(!q){
      var recientes = [];
      if(memo.ultimo && porClave[memo.ultimo]){
        var u = datos.filter(function(d){ return d.clave === memo.ultimo; })[0];
        if(u) recientes.push(u);
      }
      resultados = recientes.concat(datos.filter(function(d){ return recientes.indexOf(d) < 0; }).slice(0, 24));
      lista.innerHTML = (recientes.length ? '<p class="pal__g">Donde lo dejó</p>' : "")
        + resultados.map(function(d, n){
            return fila(d, n, "") + (n === 0 && recientes.length ? '<p class="pal__g">Todo el sistema</p>' : "");
          }).join("");
    } else {
      /* Primero los que llevan la palabra en el rótulo: es lo que uno busca
         cuando escribe dos letras y quiere saltar, no leer. */
      var enRotulo = datos.filter(function(d){ return d.rotll.indexOf(q) > -1; });
      var enTexto  = datos.filter(function(d){ return d.rotll.indexOf(q) < 0 && d.txt.indexOf(q) > -1; });
      /* «raci» dentro de «facturación» es una coincidencia, pero no es la que
         nadie busca: delante van las de palabra entera. Se mira el carácter de
         antes y el de después, que es más barato y más seguro que armar una
         expresión regular con la palabra que haya escrito el lector. */
      function entera(d){
        var i = d.txt.indexOf(q);
        if(i < 0) return false;
        var a = i ? d.txt[i - 1] : " ";
        var b = i + q.length < d.txt.length ? d.txt[i + q.length] : " ";
        return !/[a-z0-9]/.test(a) && !/[a-z0-9]/.test(b);
      }
      enTexto.sort(function(x, y){
        return (entera(y) ? 1 : 0) - (entera(x) ? 1 : 0);
      });
      resultados = enRotulo.concat(enTexto);
      if(!resultados.length){
        lista.innerHTML = '<p class="pal__nada">Nada con «' + esc(q) + '» en los ocho documentos.</p>';
      } else {
        lista.innerHTML =
          (enRotulo.length ? '<p class="pal__g">' + enRotulo.length + ' en el rótulo</p>' : "")
          + enRotulo.map(function(d, n){ return fila(d, n, ""); }).join("")
          + (enTexto.length ? '<p class="pal__g">' + enTexto.length + ' en el texto</p>' : "")
          + enTexto.map(function(d, n){ return fila(d, enRotulo.length + n, q); }).join("");
      }
    }
    elegido = 0; marcaElegido();
  }
  function fila(d, n, q){
    return '<button type="button" class="pal__i" data-va="' + d.clave + '" data-n="' + n + '">'
         + '<span>' + esc(d.n || "·") + "</span>"
         + '<b>' + esc(d.rot) + (q ? '<span class="pal__ctx">' + trozo(d, q) + "</span>" : "") + "</b>"
         + '<i>' + esc(d.doc) + "</i></button>";
  }
  function marcaElegido(){
    var todos = [].slice.call(lista.querySelectorAll(".pal__i"));
    todos.forEach(function(b, n){ b.classList.toggle("es-aqui", n === elegido); });
    var v = todos[elegido];
    if(v) v.scrollIntoView({block:"nearest"});
  }
  if(campo){
    campo.addEventListener("input", function(){ pintaPaleta(campo.value); });
    campo.addEventListener("keydown", function(e){
      var todos = [].slice.call(lista.querySelectorAll(".pal__i"));
      if(e.key === "ArrowDown"){ e.preventDefault(); elegido = Math.min(elegido + 1, todos.length - 1); marcaElegido(); }
      if(e.key === "ArrowUp"){ e.preventDefault(); elegido = Math.max(elegido - 1, 0); marcaElegido(); }
      if(e.key === "Enter" && todos[elegido]){ e.preventDefault(); todos[elegido].click(); }
    });
  }
  if(lista){
    lista.addEventListener("click", function(e){
      var b = e.target.closest(".pal__i");
      if(!b) return;
      cierra(); campo.value = ""; pon(b.dataset.va, true);
    });
  }

  /* --- el glosario: la definición donde se pulsa --------------------- */
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
    /* Dentro de un panel flotante la tarjeta se pone encima del panel, y el
       panel no se desplaza con la página: la posición se calcula igual, pero
       la tarjeta se lleva al final del cuerpo para que nada la recorte. */
    var r = b.getBoundingClientRect();
    var an = voz.offsetWidth, al = voz.offsetHeight;
    var x = Math.min(Math.max(8, r.left + window.scrollX), window.scrollX + window.innerWidth - an - 8);
    var y = r.bottom + window.scrollY + 8;
    if(r.bottom + al + 16 > window.innerHeight) y = r.top + window.scrollY - al - 8;
    voz.style.left = x + "px";
    voz.style.top = Math.max(8, y) + "px";
  });

  /* --- la lupa: una figura, de cerca --------------------------------- */
  var lupa = velos["lupa"], lienzo = D.getElementById("lupalienzo");
  lectura.addEventListener("click", function(e){
    var f = e.target.closest("figure, .fig, .t-fig, .tablewrap");
    if(!f || !lupa || !lienzo) return;
    if(e.target.closest("a, button, input")) return;
    /* Se clona la figura entera, no su contenido: copiar solo lo de dentro
       soltaba el dibujo y su pie como dos piezas sueltas, una al lado de otra. */
    lienzo.innerHTML = "";
    lienzo.appendChild(f.cloneNode(true));
    abre("lupa");
  });
  /* Se avisa de que se puede: una figura que no dice que se amplía no se
     amplía nunca. */
  [].slice.call(lectura.querySelectorAll("figure, .fig, .t-fig")).forEach(function(f){
    f.classList.add("ampliable");
    f.setAttribute("title", "Pulse para verla de cerca");
  });

  /* --- copiar, con aviso -------------------------------------------- */
  var pitido = D.getElementById("pito"), reloj = null;
  function pita(txt){
    if(!pitido) return;
    pitido.textContent = txt; pitido.hidden = false;
    clearTimeout(reloj);
    reloj = setTimeout(function(){ pitido.hidden = true; }, 1900);
  }
  function copia(txt){
    if(navigator.clipboard && navigator.clipboard.writeText){
      navigator.clipboard.writeText(txt).then(function(){ pita("Enlace copiado"); },
                                              function(){ pita("No se ha podido copiar"); });
    } else {
      var c = D.createElement("textarea");
      c.value = txt; D.body.appendChild(c); c.select();
      try { D.execCommand("copy"); pita("Enlace copiado"); } catch(e){ pita("No se ha podido copiar"); }
      D.body.removeChild(c);
    }
  }

  /* --- las teclas ---------------------------------------------------- */
  D.addEventListener("keydown", function(e){
    var t = e.target;
    var escribiendo = t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.isContentEditable);
    if(e.key === "Escape"){ if(cierra()) e.preventDefault(); return; }
    if((e.metaKey || e.ctrlKey) && (e.key === "k" || e.key === "K")){ e.preventDefault(); abre("paleta"); return; }
    if(escribiendo || e.ctrlKey || e.metaKey || e.altKey) return;
    if(e.key === "/"){ e.preventDefault(); abre("paleta"); return; }
    if(e.key === "?"){ e.preventDefault(); abre("teclas"); return; }
    if(e.key === "r" || e.key === "R"){ e.preventDefault(); abre("recursos"); return; }
    if(e.key === "ArrowRight" || e.key === "j"){ salta(1); }
    if(e.key === "ArrowLeft" || e.key === "k"){ salta(-1); }
    if(e.key === "g"){ pon("portada", true); }
  });

  window.addEventListener("hashchange", function(){
    var h = (location.hash || "").slice(1);
    var d = h && D.getElementById(h);
    var duena = d && d.closest ? d.closest(".hoja") : null;
    if(duena && !duena.classList.contains("is-on")) pon(duena.dataset.hoja, d === duena);
  });

  var seguir = D.getElementById("seguir");
  if(seguir){
    if(memo.ultimo && porClave[memo.ultimo] && memo.ultimo !== "portada"){
      var o = orden[claves.indexOf(memo.ultimo)];
      if(o) seguir.textContent = "Seguir en «" + o[3] + "»";
      seguir.addEventListener("click", function(){ pon(memo.ultimo, true); });
    } else {
      seguir.textContent = "Empezar por el principio";
      seguir.addEventListener("click", function(){ pon(claves[0], true); });
    }
  }

  var h0 = (location.hash || "").slice(1);
  var d0 = h0 && D.getElementById(h0);
  var duena0 = d0 && d0.closest ? d0.closest(".hoja") : null;
  pon(duena0 ? duena0.dataset.hoja : "portada", false);
  if(d0 && duena0 && d0 !== duena0) d0.scrollIntoView({block:"start"});
  dibujaAvance();
})();
</script>
"""

# ---------------------------------------------------------------------------
#  La página
# ---------------------------------------------------------------------------
def main():
    """Arma la página. Solo cuando se ejecuta: quien solo quiera el modelo
    —check-coherencia, por ejemplo— importa el archivo y no escribe nada."""
    global TOTAL, CARACTERES, VOCES
    HOJAS, ARBOL, INDICE, ORDEN, CUENTAS = monta()
    TOTAL = sum(CUENTAS)
    CARACTERES = sum(len(sin_marcas(h)) for h in HOJAS)
    VOCES = glosario()

    # Los recursos: lo que existe además de esta página, dicho una sola vez y
    # con lo que es cada cosa. Los archivos de la entrega van con su ruta, que
    # es la que tienen al lado de este archivo.
    RECURSOS = (
        '<div class="rec__g"><p class="rec__t">La entrega, cuatro archivos</p>'
        + "".join(
            ('<div class="rec__i" style="opacity:.62"><em>%s</em><div><b>%s</b>'
             '<p>%s Es la que está viendo.</p></div></div>'
             % (k, H.escape(n), H.escape(q))) if r == "centro.html" else
            ('<a class="rec__i" href="%s"%s><em>%s</em><div><b>%s</b><p>%s</p></div></a>'
             % (r, ' download' if d else '', k, H.escape(n), H.escape(q)))
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
            % (H.escape(k), H.escape(k), H.escape(VOCES[k][0]))
            for k in sorted(VOCES))
        + "</div>")

    PORTADA = """
<article class="hoja hoja--portada" id="portada" data-hoja="portada">
  <section class="portico">
    <p class="eyebrow">Centro de Excelencia Implantológica Giraldo · Rúa Bolivia nº 2 · Vigo</p>
    <h1>No medias <em>sonrisas</em></h1>
    <p class="portico__p">«Le devolvemos su sonrisa completa, en el menor tiempo posible, y le cuidamos para siempre.»
      <small>La promesa, completa · Plan de Dirección</small></p>
    <div class="portico__b">
      <button type="button" id="seguir" class="es-fuerte">Empezar por el principio</button>
      <button type="button" data-abre="paleta">Buscar en todo el sistema</button>
      <button type="button" data-abre="recursos">Recursos y descargas</button>
      <button type="button" data-abre="teclas">Atajos de teclado</button>
    </div>
    <div class="portico__c">
      <div><b>8</b><span>documentos, completos</span></div>
      <div><b>@TOTAL@</b><span>apartados, ninguno fuera</span></div>
      <div><b>@MILES@</b><span>caracteres de literatura</span></div>
      <div><b>@VOCES@</b><span>voces del glosario, en su sitio</span></div>
      <div><b>1,2 M€</b><span>objetivo del ejercicio tercero</span></div>
    </div>
  </section>

  <div class="idx">
    <div class="idx__cabeza">
      <p class="eyebrow">Índice completo</p>
      <h2>Todo lo que hay, y dónde está</h2>
      <p>Los ocho documentos del sistema con sus @TOTAL@ apartados, uno por uno, y debajo de cada uno los titulares que contiene. No hay nada fuera de esta lista: lo que no está aquí no está escrito. Pulse cualquiera y se abre. Con <kbd>⌘K</kbd> o <kbd>/</kbd> se busca en el texto de los ocho a la vez; las siglas subrayadas se explican al pulsarlas.</p>
    </div>
    @@INDICE@@
  </div>
</article>
"""

    CUERPO = """
<a class="saltar" href="#lectura">Saltar al contenido</a>
<div class="avance" id="avance" aria-hidden="true"></div>
<div class="cen">

  <aside class="lado" id="lado">
    <div class="lado__cab">
      <a class="lado__marca" href="#portada" data-ir="portada">
        <strong>El Centro <b>Giraldo</b></strong>
        <span>Sistema completo · v@VERSION@</span>
      </a>
      <button class="abrepal" type="button" data-abre="paleta">
        <svg width="13" height="13" viewBox="0 0 16 16" aria-hidden="true">
          <circle cx="7" cy="7" r="4.6" fill="none" stroke="currentColor" stroke-width="1.7"/>
          <path d="M10.4 10.4 L14.4 14.4" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/>
        </svg>
        <span>Buscar…</span><kbd>⌘K</kbd>
      </button>
    </div>
    <nav class="arbol" id="arbol" aria-label="Índice completo del sistema">
      <a class="arbol__inicio" href="#portada" data-ir="portada">Portada e índice completo</a>
      @@ARBOL@@
    </nav>
  </aside>

  <div class="cen__col">
    <header class="cima">
      <button class="icono cima__menu" id="menu" type="button" aria-label="Índice">&#9776;</button>
      <nav class="miga" id="miga" aria-label="Dónde está"></nav>
      <span class="cima__n" id="cuenta"></span>
      <span class="cima__sep"></span>
      <button class="icono" id="ant" type="button" aria-label="Apartado anterior" title="Anterior (←)">&#8592;</button>
      <button class="icono" id="sig" type="button" aria-label="Apartado siguiente" title="Siguiente (→)">&#8594;</button>
      <button class="icono" type="button" data-abre="recursos" aria-label="Recursos" title="Recursos (R)">&#9781;</button>
      <button class="icono" type="button" data-abre="teclas" aria-label="Atajos" title="Atajos (?)">?</button>
    </header>

    <div class="marco">
      <main class="lectura" id="lectura" tabindex="-1">
        @@PORTADA@@
        @@HOJAS@@
      </main>
      <aside class="sumario" id="sumario" aria-label="En este apartado"></aside>
    </div>
  </div>
</div>

<!-- ------------------------------------------------------------------
     Lo que aparece cuando se pide. Todo se cierra con Esc o pulsando
     fuera, y todo devuelve el foco a donde estaba.
     ------------------------------------------------------------------ -->
<div class="velo" data-velo="paleta" role="dialog" aria-modal="true" aria-label="Buscar en el sistema" hidden>
  <div class="flota">
    <div class="pal__campo">
      <svg width="15" height="15" viewBox="0 0 16 16" aria-hidden="true" style="color:var(--muted);flex:none">
        <circle cx="7" cy="7" r="4.6" fill="none" stroke="currentColor" stroke-width="1.7"/>
        <path d="M10.4 10.4 L14.4 14.4" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/>
      </svg>
      <input id="palq" type="search" autocomplete="off" spellcheck="false"
             placeholder="Buscar en los @TOTAL@ apartados y en su texto" aria-label="Buscar">
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
    <div class="flota__cab">
      <h2>Recursos del sistema</h2>
      <button class="icono" type="button" data-cerrar aria-label="Cerrar">&#10005;</button>
    </div>
    <div class="flota__cuerpo">@@RECURSOS@@</div>
    <div class="flota__pie"><span>Todo es de uso interno y confidencial.</span></div>
  </div>
</div>

<div class="velo" data-velo="teclas" role="dialog" aria-modal="true" aria-label="Atajos de teclado" hidden>
  <div class="flota" style="width:min(30rem,100%)">
    <div class="flota__cab">
      <h2>Atajos de teclado</h2>
      <button class="icono" type="button" data-cerrar aria-label="Cerrar">&#10005;</button>
    </div>
    <div class="flota__cuerpo">
      <dl class="tec">
        <dt><kbd>&#8984;K</kbd> &middot; <kbd>/</kbd></dt><dd>Buscar en los ocho documentos y saltar a un apartado</dd>
        <dt><kbd>&#8594;</kbd> &middot; <kbd>J</kbd></dt><dd>Apartado siguiente</dd>
        <dt><kbd>&#8592;</kbd> &middot; <kbd>K</kbd></dt><dd>Apartado anterior</dd>
        <dt><kbd>G</kbd></dt><dd>Volver a la portada y al índice completo</dd>
        <dt><kbd>R</kbd></dt><dd>Recursos y descargas</dd>
        <dt><kbd>?</kbd></dt><dd>Esta ventana</dd>
        <dt><kbd>Esc</kbd></dt><dd>Cerrar lo que esté abierto</dd>
      </dl>
      <p style="margin:1.4rem 0 0;font-size:.86rem;color:var(--ink-2);line-height:1.6">
        Las siglas subrayadas —@EJEMPLO@— abren su definición al pulsarlas, y la
        definición es la que está escrita en el Manual, no una redacción nueva.
        Las figuras y las tablas anchas se ven de cerca pulsando encima. Lo que
        marque como leído y el último apartado en el que estuvo se quedan en
        este navegador y no salen de aquí.
      </p>
    </div>
  </div>
</div>

<div class="velo lupa" data-velo="lupa" role="dialog" aria-modal="true" aria-label="Figura ampliada" hidden>
  <div class="flota">
    <div class="flota__cab">
      <h2>De cerca</h2>
      <button class="icono" type="button" data-cerrar aria-label="Cerrar">&#10005;</button>
    </div>
    <div class="lupa__lienzo" id="lupalienzo"></div>
  </div>
</div>

<div class="voz" id="voz" role="tooltip" hidden></div>
<div class="pito" id="pito" role="status" hidden></div>
"""

    def sello(t):
        return (t.replace("@VERSION@", VERSION).replace("@FECHA@", FECHA)
                 .replace("@TOTAL@", str(TOTAL))
                 .replace("@VOCES@", str(len(VOCES)))
                 .replace("@EJEMPLO@", ", ".join(sorted(VOCES)[:3]))
                 .replace("@MILES@", "{:,}".format(CARACTERES).replace(",", ".")))


    # La cabeza del manual trae los tipos, los tokens y el sistema visual entero;
    # aquí se le añade la hoja del sitio y las hojas propias de las dos páginas que
    # aportan mandos —el selector de puesto y la hoja de captura—, que si no
    # viajaran saldrían como controles crudos del navegador.
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


    manual = fuente("manual.html")
    i = manual.index("<body>")
    cabecera = manual[:i + len("<body>")]
    cabecera = cabecera.replace("<title>Manual Maestro Giraldo</title>",
                                "<title>El Centro Giraldo · el sistema documental completo</title>")
    cabecera = re.sub(r'<meta name="description" content="[^"]*">',
                      '<meta name="description" content="El sistema documental completo del Centro de '
                      'Excelencia Implantológica Giraldo: los ocho documentos y sus %d apartados en una '
                      'sola página, con índice completo y buscador que entra en el texto.">' % TOTAL,
                      cabecera, count=1)

    extra = CSS
    extra += "\n" + hoja_propia("protocolos.html", "PROTOCOLOS POR PUESTO")
    extra += "\n" + hoja_propia("instrumentos/captura.html", "HOJA DE CAPTURA")
    extra += "\n" + hoja_propia("deck.html", ".slide{")
    k = cabecera.rindex("</style>")
    cabecera = cabecera[:k] + extra + "\n" + cabecera[k:]

    # El selector de puesto, con su mando. Allí la dirección de la página nombra el
    # puesto; aquí nombra el apartado, y son dos cosas distintas: se le quita el
    # trozo que la escribe y el que la lee al arrancar.
    SELECTOR = guion_propio("protocolos.html", "ES_PERFIL")
    SELECTOR = re.sub(r"\n\s*var actual = location\.hash.*?\n\s*\}\n", "\n", SELECTOR, count=1, flags=re.S)
    SELECTOR = SELECTOR.replace('var h = (location.hash || "").replace(ES_PERFIL, "");', 'var h = "";')
    SELECTOR = SELECTOR.replace('var sel = document.querySelector(".selector");',
                                'var sel = document.querySelector(".hoja .selector");')

    cuerpo = (CUERPO.replace("@@ARBOL@@", "\n".join(ARBOL))
                    .replace("@@PORTADA@@", PORTADA.replace("@@INDICE@@", "\n".join(INDICE)))
                    .replace("@@RECURSOS@@", RECURSOS)
                .replace("@@HOJAS@@", "\n".join(HOJAS)))

    datos = ("<script>window.__ORDEN__ = "
             + json.dumps([[c, d, g, r] for c, d, g, r in ORDEN], ensure_ascii=False)
             + ";\nwindow.__VOCES__ = "
             + json.dumps(VOCES, ensure_ascii=False) + ";</script>")

    salida = RAIZ / "centro.html"
    salida.write_text(
        sello(cabecera + "\n" + cuerpo + "\n" + datos + "\n" + JS + "\n" + SELECTOR
              + "\n</body>\n</html>\n"),
        encoding="utf-8")
    print("centro.html · 8 documentos · %d apartados · %s caracteres · %d KB"
          % (TOTAL, "{:,}".format(CARACTERES).replace(",", "."), salida.stat().st_size // 1024))

if __name__ == "__main__":
    main()
