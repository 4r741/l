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
    for n, (doc, rotulo, clase, que, marca) in enumerate(DOCUMENTOS):
        piezas = recoge(doc)
        pre = marca + "-"
        for p in piezas:
            p["html"] = prefija(entabla(p["html"]), pre)
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
                '<article class="hoja" id="%s" data-hoja="%s" data-doc="%d">\n'
                '  <p class="hoja__de"><span>%s</span> %s%s</p>\n'
                '%s\n</article>'
                % (p["clave"], p["clave"], n, nn, H.escape(rotulo),
                   " · " + H.escape(p["grupo"]) if p["grupo"] else "", p["html"]))

        cuentas.append(len(piezas))
        arbol.append(
            '<details class="lado__doc" data-doc="%d"%s>\n'
            '  <summary><b>%s</b><span>%s</span><i>%d</i></summary>\n'
            '  <div class="lado__ramas">%s</div>\n</details>'
            % (n, " open" if n == 0 else "", nn, H.escape(rotulo), len(piezas), "".join(ramas)))
        indice.append(
            '<section class="idx__doc">\n'
            '  <header class="idx__cab"><p class="eyebrow">%s · %d apartados</p>'
            '<h3><span>%s</span>%s</h3><p>%s</p></header>\n'
            '  <div class="idx__lista">%s</div>\n</section>'
            % (H.escape(clase), len(piezas), nn, H.escape(rotulo), H.escape(que), "".join(filas)))

    return hojas, arbol, indice, orden, cuentas


CSS = """
/* ===========================================================================
   EL CENTRO GIRALDO · EL SISTEMA COMPLETO EN UN SITIO

   Ocho documentos, ciento treinta y cinco apartados y un millón seiscientos mil
   caracteres de literatura en una sola página. Para que eso se pueda recorrer
   hacen falta tres cosas y ninguna más: un índice completo que quepa de un
   vistazo, un apartado cada vez y un buscador que entre en el texto. Todo lo
   demás sobra y se ha dejado fuera a propósito.
   =========================================================================== */
:root{--lado:20.5rem; --cima:3.6rem}

body{background:var(--paper)}
.cen{display:grid;grid-template-columns:var(--lado) minmax(0,1fr);min-height:100vh}

/* --- el lado: marca, buscador e índice completo ------------------------- */
.lado{
  position:sticky;top:0;height:100vh;display:flex;flex-direction:column;
  background:var(--surface);border-right:1px solid var(--line);z-index:30;
}
.lado__cab{padding:1.15rem 1.15rem 1rem;border-bottom:1px solid var(--line-soft)}
.lado__marca{display:block;text-decoration:none;color:var(--tinta)}
.lado__marca b{font-weight:600}
.lado__marca span{
  display:block;margin-top:.2rem;font-family:var(--f-mono);font-size:.64rem;
  letter-spacing:.14em;text-transform:uppercase;color:var(--muted);
}
.lado__marca strong{font-family:var(--f-display);font-size:1.06rem;font-weight:500;letter-spacing:-.012em}
.busca{
  display:flex;align-items:center;gap:.55rem;margin-top:.95rem;padding:.55rem .8rem;
  background:var(--surface-2);border:1px solid var(--line);border-radius:999px;color:var(--muted);
}
.busca:focus-within{border-color:var(--accent);background:var(--surface);
  box-shadow:0 0 0 3px var(--accent-soft)}
.busca svg{flex:none}
.busca input{
  flex:1;min-width:0;border:0;background:none;outline:none;padding:0;
  font:inherit;font-size:.9rem;color:var(--ink);
}
.busca input::placeholder{color:var(--muted)}
.busca input::-webkit-search-cancel-button{-webkit-appearance:none;appearance:none}
.busca kbd{
  font-family:var(--f-mono);font-size:.64rem;color:var(--muted);background:var(--surface);
  border:1px solid var(--line);border-radius:5px;padding:.2rem .36rem;line-height:1;
}
.busca:focus-within kbd{opacity:0}

.arbol{flex:1;overflow-y:auto;padding:.7rem .7rem 3rem;scrollbar-width:thin}
.arbol__inicio{
  display:flex;align-items:center;gap:.6rem;text-decoration:none;
  padding:.6rem .7rem;border-radius:var(--radio-s);color:var(--ink-2);
  font-size:.9rem;font-weight:500;margin-bottom:.4rem;
}
.arbol__inicio:hover{background:var(--surface-2);color:var(--ink)}
.arbol__inicio.is-on{background:var(--tinta);color:#fff}
.lado__doc{border-top:1px solid var(--line-soft)}
.lado__doc > summary{
  display:flex;align-items:center;gap:.6rem;cursor:pointer;list-style:none;
  padding:.72rem .7rem;border-radius:var(--radio-s);
}
.lado__doc > summary::-webkit-details-marker{display:none}
.lado__doc > summary:hover{background:var(--surface-2)}
.lado__doc > summary b{font-family:var(--f-mono);font-size:.68rem;color:var(--muted);font-weight:500}
.lado__doc > summary span{flex:1;font-size:.9rem;font-weight:600;color:var(--tinta);line-height:1.3}
.lado__doc > summary i{
  font-style:normal;font-family:var(--f-mono);font-size:.64rem;color:var(--muted);
  background:var(--surface-2);border-radius:999px;padding:.14rem .45rem;
}
.lado__doc[open] > summary span{color:var(--accent-ink)}
.lado__ramas{padding:.1rem 0 .8rem .4rem;margin-left:1.05rem;border-left:1px solid var(--line)}
.lado__gt{
  margin:.7rem 0 .3rem;padding-left:.7rem;font-family:var(--f-mono);font-size:.6rem;
  letter-spacing:.14em;text-transform:uppercase;color:var(--muted);
}
.lado__ramas a{
  display:flex;gap:.55rem;align-items:baseline;text-decoration:none;color:var(--ink-2);
  font-size:.83rem;line-height:1.38;padding:.36rem .55rem;border-radius:6px;
}
.lado__ramas a span{font-family:var(--f-mono);font-size:.62rem;color:var(--muted);flex:none;min-width:1.1rem}
.lado__ramas a:hover{background:var(--surface-2);color:var(--ink)}
.lado__ramas a.is-on{background:var(--acido);color:var(--accent-fuerte);font-weight:600}
.lado__ramas a.is-on span{color:var(--accent-ink)}
.lado__doc.is-fuera,.lado__ramas a.is-fuera,.lado__gt.is-fuera{display:none}

/* --- la columna de lectura ---------------------------------------------- */
.cen__col{min-width:0;display:flex;flex-direction:column}
.cima{
  position:sticky;top:0;z-index:20;display:flex;align-items:center;gap:1rem;
  height:var(--cima);padding:0 1.6rem;background:rgba(246,248,249,.92);
  backdrop-filter:saturate(1.4) blur(8px);border-bottom:1px solid var(--line);
}
.miga{
  flex:1;min-width:0;display:flex;align-items:center;gap:.5rem;font-size:.82rem;
  color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
}
.miga b{color:var(--tinta);font-weight:600}
.miga em{font-style:normal;color:var(--line)}
.cima__n{font-family:var(--f-mono);font-size:.68rem;color:var(--muted);white-space:nowrap}
.cima__pasos{display:flex;gap:.4rem}
.cima__pasos button{
  font:inherit;cursor:pointer;width:2rem;height:2rem;border-radius:7px;
  border:1px solid var(--line);background:var(--surface);color:var(--ink-2);line-height:1;
}
.cima__pasos button:hover:not(:disabled){border-color:var(--accent);color:var(--accent-ink)}
.cima__pasos button:disabled{opacity:.35;cursor:default}
.cima__menu{display:none}

.lectura{flex:1;padding:2.2rem 1.6rem 6rem}
.hoja{
  max-width:74rem;margin:0 auto;background:var(--surface);
  border:1px solid var(--line);border-radius:var(--radio);
  padding:2.8rem 3rem 3.4rem;box-shadow:var(--sombra-1);
}
.hoja__de{
  margin:0 0 1.6rem;padding-bottom:1.1rem;border-bottom:1px solid var(--line-soft);
  font-family:var(--f-mono);font-size:.66rem;letter-spacing:.13em;text-transform:uppercase;
  color:var(--muted);
}
.hoja__de span{color:var(--accent);margin-right:.6rem}
/* La literatura llega con el envoltorio de su documento; aquí la caja ya la
   pone la hoja y no hacen falta dos. */
.hoja .wrap{padding:0;max-width:none}
.hoja .section{padding:0;background:none;border:0}
.hoja .section + .section{margin-top:3.4rem;padding-top:3.4rem;border-top:1px solid var(--line-soft)}
/* Las fases traen la marca de aparición progresiva de su documento y el guion
   que las destapa no viaja: sin esto se quedaban invisibles. */
.hoja .reveal{opacity:1!important;transform:none!important}
/* Su rejilla de dos columnas se enciende a 960 px de ventana, pero aquí la
   ventana no es la columna: con el índice a la izquierda se salían por la
   derecha. Se encienden más tarde, ya con sitio. */
@media(max-width:1479px){
  .hoja .phase__grid{grid-template-columns:minmax(0,1fr)}
  .hoja .phase__meta{position:static}
}
.hoja .tablewrap{overflow-x:auto}
a.fuera::after{content:"↗";font-size:.78em;margin-left:.2em;color:var(--muted)}

/* --- portada: el pórtico y el índice completo ---------------------------- */
.hoja--portada{padding:0;overflow:hidden;border:0;background:none;box-shadow:none;max-width:none}
.portico{background:var(--tinta);color:#fff;padding:4.6rem 3rem 4rem;border-radius:var(--radio)}
.portico .eyebrow{color:rgba(255,255,255,.5)}
.portico h1{font-size:clamp(2.6rem,6vw,4.6rem);line-height:1.03;letter-spacing:-.028em;margin:1.3rem 0 0}
.portico h1 em{font-style:normal;color:var(--acido);display:block}
.portico__p{
  margin:1.9rem 0 0;font-family:var(--f-display);font-size:clamp(1.05rem,2vw,1.35rem);
  line-height:1.45;color:rgba(255,255,255,.85);max-width:44ch;
}
.portico__p small{
  display:block;margin-top:.8rem;font-family:var(--f-mono);font-size:.68rem;
  letter-spacing:.13em;text-transform:uppercase;color:rgba(255,255,255,.42);
}
.portico__c{display:flex;flex-wrap:wrap;gap:2.6rem;margin-top:3rem;padding-top:1.9rem;
  border-top:1px solid rgba(255,255,255,.16)}
.portico__c b{display:block;font-family:var(--f-display);font-size:1.7rem;color:var(--acido)}
.portico__c span{display:block;margin-top:.3rem;font-family:var(--f-mono);font-size:.64rem;
  letter-spacing:.13em;text-transform:uppercase;color:rgba(255,255,255,.5)}

.idx{margin-top:2.4rem}
.idx__cabeza{
  display:flex;flex-wrap:wrap;align-items:flex-end;justify-content:space-between;gap:1.4rem;
  padding:0 0 1.4rem;border-bottom:1px solid var(--line);margin-bottom:2.2rem;
}
.idx__cabeza h2{margin:.5rem 0 0;font-size:clamp(1.7rem,3.4vw,2.5rem);letter-spacing:-.024em}
.idx__cabeza p{margin:.7rem 0 0;color:var(--ink-2);max-width:58ch;line-height:1.6}
.idx__doc{
  background:var(--surface);border:1px solid var(--line);border-radius:var(--radio);
  padding:2rem 2.2rem 2.2rem;margin-bottom:1.1rem;
}
.idx__cab h3{margin:.5rem 0 0;font-size:1.5rem;letter-spacing:-.018em;display:flex;gap:.85rem;align-items:baseline}
.idx__cab h3 span{font-family:var(--f-mono);font-size:.86rem;color:var(--accent);font-weight:500}
.idx__cab > p{margin:.6rem 0 0;color:var(--ink-2);font-size:.95rem;line-height:1.6;max-width:70ch}
.idx__lista{
  margin-top:1.7rem;padding-top:1.4rem;border-top:1px solid var(--line-soft);
  columns:2;column-gap:2.6rem;
}
.idx__gt{
  break-inside:avoid;margin:1.3rem 0 .5rem;font-family:var(--f-mono);font-size:.63rem;
  letter-spacing:.15em;text-transform:uppercase;color:var(--accent-ink);
}
.idx__gt:first-child{margin-top:0}
.idx__ap{break-inside:avoid;margin-bottom:.75rem}
.idx__ap a{display:flex;gap:.7rem;align-items:baseline;text-decoration:none;color:var(--ink-2)}
.idx__ap a span{font-family:var(--f-mono);font-size:.68rem;color:var(--muted);flex:none;min-width:1.4rem}
.idx__ap a b{font-size:.95rem;font-weight:500;line-height:1.4}
.idx__ap a:hover b{color:var(--accent-ink);text-decoration:underline}
.idx__t{
  margin:.25rem 0 0 2.1rem;font-size:.78rem;line-height:1.5;color:var(--muted);
}

/* --- resultados del buscador -------------------------------------------- */
.res{max-width:74rem;margin:0 auto}
.res__t{
  font-family:var(--f-mono);font-size:.68rem;letter-spacing:.14em;text-transform:uppercase;
  color:var(--muted);margin:0 0 1.2rem;
}
.res a{
  display:block;text-decoration:none;background:var(--surface);border:1px solid var(--line);
  border-radius:var(--radio-s);padding:1rem 1.2rem;margin-bottom:.6rem;
}
.res a:hover{border-color:var(--accent)}
.res a em{
  font-style:normal;font-family:var(--f-mono);font-size:.64rem;letter-spacing:.12em;
  text-transform:uppercase;color:var(--muted);display:block;
}
.res a b{display:block;margin-top:.3rem;font-size:1rem;color:var(--tinta)}
.res a p{margin:.45rem 0 0;font-size:.86rem;color:var(--ink-2);line-height:1.55}
.res a p mark{background:var(--acido);color:var(--accent-fuerte);padding:0 .12em;border-radius:2px}

/* --- las diapositivas, dentro del sitio --------------------------------- */
/* La presentación esconde todas las diapositivas menos una: allí se pasan con
   el teclado. Aquí se leen las cuarenta y tres seguidas, que es lo que hay. */
.deck--sitio{display:flex;flex-direction:column;gap:1.4rem}
.deck--sitio.deck{position:static;height:auto;overflow:visible}
.deck--sitio .slide{display:block!important;position:static!important;inset:auto!important;
  height:auto!important;min-height:0!important;opacity:1!important;transform:none!important;
  animation:none!important}
.deck--sitio .slide > *{max-width:none}
.deck--sitio .slide h2{font-size:clamp(1.5rem,2.6vw,2rem)}
.deck--sitio .slide{
  border:1px solid var(--line);border-radius:var(--radio-s);padding:2rem 2.2rem;
  background:var(--surface-2);
}
.deck--sitio .nota{display:none}

/* --- el pie -------------------------------------------------------------- */
.pieC{
  max-width:74rem;margin:2.4rem auto 0;padding-top:1.6rem;border-top:1px solid var(--line);
  display:flex;flex-wrap:wrap;gap:1.2rem;justify-content:space-between;
  font-size:.82rem;color:var(--muted);
}

/* Con guiones se lee un apartado cada vez; sin ellos —y al imprimir— se ven
   los ciento treinta y cinco seguidos, que es el sistema entero. La marca la
   pone el instalador: si el guion no llegara a correr, no queda una página en
   blanco sino el documento completo. */
.lectura--viva .hoja{display:none}
.lectura--viva .hoja.is-on{display:block}
.lectura--viva .hoja--portada.is-on{display:block}

@media(max-width:1080px){
  .cen{grid-template-columns:minmax(0,1fr)}
  .lado{
    position:fixed;inset:0 auto 0 0;width:min(22rem,86vw);transform:translateX(-101%);
    transition:transform .2s ease;box-shadow:0 0 40px rgba(18,35,43,.18);
  }
  .lado.is-abierto{transform:none}
  .cima__menu{
    display:inline-flex;align-items:center;gap:.5rem;font:inherit;font-size:.84rem;
    cursor:pointer;border:1px solid var(--line);background:var(--surface);
    color:var(--ink-2);border-radius:999px;padding:.4rem .85rem;
  }
  .hoja{padding:1.7rem 1.3rem 2.2rem}
  .portico{padding:3rem 1.5rem 2.6rem}
  .idx__doc{padding:1.4rem 1.3rem 1.6rem}
  .idx__lista{columns:1}
  .lectura{padding:1.4rem .9rem 4rem}
}
@media print{
  .lado,.cima,.pieC{display:none}
  .cen{display:block}
  .lectura--viva .hoja{display:block}
  .hoja{border:0;box-shadow:none;padding:0;margin-bottom:2rem;break-after:page}
}
"""


JS = """
<script>
(function(){
  "use strict";
  var lectura = document.getElementById("lectura");
  if(!lectura) return;
  var hojas = [].slice.call(lectura.querySelectorAll(".hoja"));
  var orden = window.__ORDEN__ || [];
  var lado  = document.getElementById("lado");
  var arbol = document.getElementById("arbol");
  var campo = document.getElementById("q");
  var miga  = document.getElementById("miga");
  var cuenta= document.getElementById("cuenta");
  var ant   = document.getElementById("ant");
  var sig   = document.getElementById("sig");
  var res   = document.getElementById("res");
  if(!hojas.length) return;

  /* La marca la pone el guion, no el marcado: si esto no corriera, se ven los
     ciento treinta y cinco apartados seguidos —el sistema entero— en vez de
     quedarse la página en blanco. */
  lectura.classList.add("lectura--viva");

  var porClave = {};
  hojas.forEach(function(h){ porClave[h.dataset.hoja] = h; });
  var claves = orden.map(function(o){ return o[0]; });

  function pon(clave, arriba){
    var h = porClave[clave] || hojas[0];
    hojas.forEach(function(x){ x.classList.toggle("is-on", x === h); });
    if(res) res.hidden = true;
    lectura.hidden = false;

    [].slice.call(arbol.querySelectorAll("a[data-ir]")).forEach(function(a){
      a.classList.toggle("is-on", a.dataset.ir === h.dataset.hoja);
    });
    var d = h.dataset.doc;
    if(d !== undefined){
      var caja = arbol.querySelector('.lado__doc[data-doc="' + d + '"]');
      if(caja && !caja.open) caja.open = true;
    }

    var vivo = arbol.querySelector('a[data-ir="' + h.dataset.hoja + '"]');
    if(vivo && vivo.scrollIntoView){
      var r = vivo.getBoundingClientRect(), c = arbol.getBoundingClientRect();
      if(r.top < c.top + 8 || r.bottom > c.bottom - 8){
        vivo.scrollIntoView({block:"center"});
      }
    }

    var i = claves.indexOf(h.dataset.hoja);
    if(miga){
      if(i < 0){
        miga.innerHTML = "<b>Portada e índice completo</b>";
      } else {
        var o = orden[i];
        miga.innerHTML = o[1].replace(/&/g,"&amp;") + (o[2] ? ' <em>&rsaquo;</em> ' + o[2] : "")
                       + ' <em>&rsaquo;</em> <b>' + o[3] + "</b>";
      }
    }
    if(cuenta) cuenta.textContent = i < 0 ? (claves.length + " apartados")
                                          : ((i + 1) + " / " + claves.length);
    if(ant) ant.disabled = i <= 0;
    if(sig) sig.disabled = i < 0 || i >= claves.length - 1;

    try { history.replaceState(null, "", "#" + h.dataset.hoja); } catch(e){}
    if(arriba !== false) window.scrollTo({top:0, behavior:"instant" in window ? "auto" : "auto"});
    if(lado) lado.classList.remove("is-abierto");
  }

  function salta(paso){
    var actual = hojas.filter(function(h){ return h.classList.contains("is-on"); })[0];
    var i = actual ? claves.indexOf(actual.dataset.hoja) : -1;
    var j = i < 0 ? (paso > 0 ? 0 : -1) : i + paso;
    if(j >= 0 && j < claves.length) pon(claves[j], true);
  }
  if(ant) ant.addEventListener("click", function(){ salta(-1); });
  if(sig) sig.addEventListener("click", function(){ salta(1); });

  /* Cualquier enlace de la página que apunte a algo que está aquí abre su
     apartado y baja hasta ello. Ese era el salto raro: caer en mitad de otro
     documento sin saber en qué parte se estaba. */
  document.addEventListener("click", function(e){
    var a = e.target.closest('a[href^="#"]');
    if(!a || a.classList.contains("fuera")) return;
    var destino = document.getElementById(a.getAttribute("href").slice(1));
    if(!destino) return;
    var duena = destino.closest(".hoja");
    if(!duena) return;
    e.preventDefault();
    pon(duena.dataset.hoja, true);
    if(destino !== duena){
      destino.scrollIntoView({block:"start", behavior:"smooth"});
      try { history.replaceState(null, "", a.getAttribute("href")); } catch(err){}
    }
  });

  var menu = document.getElementById("menu");
  if(menu) menu.addEventListener("click", function(){ lado.classList.toggle("is-abierto"); });

  /* ---- el buscador: entra en el texto, no solo en los títulos ----------
     El texto de cada apartado se saca una sola vez, la primera que se escribe,
     y se guarda. Son un millón seiscientos mil caracteres: sacarlos en cada
     tecla se notaría, sacarlos una vez no. */
  var cache = null;
  /* Quita acentos SIN cambiar la longitud: el recorte que se enseña sale del
     texto original, y para cortarlo por el mismo sitio los dos tienen que
     medir lo mismo. «normalize("NFD")» descompone y alarga, así que no vale. */
  var CON = "\u00e1\u00e0\u00e4\u00e2\u00e3\u00e9\u00e8\u00eb\u00ea\u00ed\u00ec\u00ef\u00ee"
          + "\u00f3\u00f2\u00f6\u00f4\u00f5\u00fa\u00f9\u00fc\u00fb\u00f1\u00e7";
  var SIN = "aaaaaeeeeiiiiooooouuuunc";
  function llano(s){
    s = s.toLowerCase();
    var fuera = "";
    for(var i = 0; i < s.length; i++){
      var j = CON.indexOf(s[i]);
      fuera += j < 0 ? s[i] : SIN[j];
    }
    return fuera;
  }
  function indexa(){
    if(cache) return cache;
    cache = hojas.filter(function(h){ return h.dataset.hoja !== "portada"; }).map(function(h){
      var o = orden[claves.indexOf(h.dataset.hoja)];
      var crudo = (h.innerText || h.textContent || "").replace(/\s+/g, " ");
      return {h:h, clave:h.dataset.hoja, doc:o ? o[1] : "", grupo:o ? o[2] : "",
              rot:o ? o[3] : "", crudo:crudo, txt:llano(crudo)};
    });
    return cache;
  }
  function escapa(s){
    return s.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
  }
  function recorte(d, q){
    var i = d.txt.indexOf(q);
    if(i < 0) return escapa(d.crudo.slice(0, 170)) + "…";
    var a = Math.max(0, i - 80), b = Math.min(d.crudo.length, i + q.length + 120);
    return (a ? "…" : "") + escapa(d.crudo.slice(a, i)) + "<mark>"
         + escapa(d.crudo.slice(i, i + q.length)) + "</mark>"
         + escapa(d.crudo.slice(i + q.length, b)) + (b < d.crudo.length ? "…" : "");
  }
  function busca(){
    var q = llano(campo.value.trim());
    var ramas = [].slice.call(arbol.querySelectorAll(".lado__ramas a"));
    var grupos = [].slice.call(arbol.querySelectorAll(".lado__gt"));
    var docs = [].slice.call(arbol.querySelectorAll(".lado__doc"));

    if(q.length < 2){
      ramas.concat(grupos).concat(docs).forEach(function(x){ x.classList.remove("is-fuera"); });
      if(res) res.hidden = true;
      var viva = hojas.filter(function(h){ return h.classList.contains("is-on"); })[0];
      if(!viva) pon(claves[0], false);
      return;
    }

    var datos = indexa();
    var vivos = {};
    var hits = datos.filter(function(d){
      var ok = d.txt.indexOf(q) > -1 || llano(d.rot).indexOf(q) > -1;
      if(ok) vivos[d.clave] = d;
      return ok;
    });

    ramas.forEach(function(a){ a.classList.toggle("is-fuera", !vivos[a.dataset.ir]); });
    docs.forEach(function(d){
      var hay = [].slice.call(d.querySelectorAll(".lado__ramas a")).some(function(a){
        return !a.classList.contains("is-fuera");
      });
      d.classList.toggle("is-fuera", !hay);
      if(hay) d.open = true;
    });
    grupos.forEach(function(g){
      var n = g.nextElementSibling, hay = false;
      while(n && n.tagName === "A"){
        if(!n.classList.contains("is-fuera")) hay = true;
        n = n.nextElementSibling;
      }
      g.classList.toggle("is-fuera", !hay);
    });

    if(!res) return;
    res.innerHTML = '<p class="res__t">' + hits.length + ' apartado' + (hits.length === 1 ? "" : "s")
                  + ' con «' + campo.value.trim().replace(/</g,"&lt;") + '» · de '
                  + datos.length + '</p>'
                  + hits.slice(0, 60).map(function(d){
                      return '<a href="#' + d.clave + '"><em>' + d.doc
                           + (d.grupo ? " · " + d.grupo : "") + '</em><b>' + d.rot + '</b>'
                           + '<p>' + recorte(d, q) + '</p></a>';
                    }).join("");
    hojas.forEach(function(h){ h.classList.remove("is-on"); });
    res.hidden = false;
  }
  if(campo){
    campo.addEventListener("input", busca);
    campo.addEventListener("keydown", function(e){
      if(e.key === "Escape"){ campo.value = ""; busca(); campo.blur(); }
      if(e.key === "Enter"){
        var p = res && !res.hidden && res.querySelector("a");
        if(p){ e.preventDefault(); p.click(); }
      }
    });
  }

  document.addEventListener("keydown", function(e){
    var d = e.target;
    var escribiendo = d && (d.tagName === "INPUT" || d.tagName === "TEXTAREA" || d.isContentEditable);
    if(!escribiendo && e.key === "/" && !e.ctrlKey && !e.metaKey){
      e.preventDefault(); if(campo) campo.focus(); return;
    }
    if(escribiendo || e.ctrlKey || e.metaKey || e.altKey) return;
    if(e.key === "ArrowRight"){ salta(1); }
    if(e.key === "ArrowLeft"){ salta(-1); }
  });

  window.addEventListener("hashchange", function(){
    var h = (location.hash || "").slice(1);
    var d = h && document.getElementById(h);
    var duena = d && d.closest ? d.closest(".hoja") : null;
    if(duena) pon(duena.dataset.hoja, d === duena);
  });

  var h0 = (location.hash || "").slice(1);
  var d0 = h0 && document.getElementById(h0);
  var duena0 = d0 && d0.closest ? d0.closest(".hoja") : null;
  pon(duena0 ? duena0.dataset.hoja : "portada", false);
  if(d0 && duena0 && d0 !== duena0) d0.scrollIntoView({block:"start"});
})();
</script>
"""


# ---------------------------------------------------------------------------
#  La página
# ---------------------------------------------------------------------------
def main():
    """Arma la página. Solo cuando se ejecuta: quien solo quiera el modelo
    —check-coherencia, por ejemplo— importa el archivo y no escribe nada."""
    global TOTAL, CARACTERES
    HOJAS, ARBOL, INDICE, ORDEN, CUENTAS = monta()
    TOTAL = sum(CUENTAS)
    CARACTERES = sum(len(sin_marcas(h)) for h in HOJAS)

    PORTADA = """
    <article class="hoja hoja--portada" id="portada" data-hoja="portada">
      <section class="portico">
        <p class="eyebrow">Centro de Excelencia Implantológica Giraldo · Rúa Bolivia nº 2 · Vigo</p>
        <h1>No medias <em>sonrisas</em></h1>
        <p class="portico__p">«Le devolvemos su sonrisa completa, en el menor tiempo posible, y le cuidamos para siempre.»
          <small>La promesa, completa · Plan de Dirección</small></p>
        <div class="portico__c">
          <div><b>8</b><span>documentos, completos</span></div>
          <div><b>@TOTAL@</b><span>apartados, ninguno fuera</span></div>
          <div><b>@MILES@</b><span>caracteres de literatura</span></div>
          <div><b>14</b><span>fases del recorrido</span></div>
          <div><b>1,2 M€</b><span>objetivo del ejercicio tercero</span></div>
        </div>
      </section>

      <div class="idx">
        <div class="idx__cabeza">
          <div>
            <p class="eyebrow">Índice completo</p>
            <h2>Todo lo que hay, y dónde está</h2>
            <p>Los ocho documentos del sistema con sus @TOTAL@ apartados, uno por uno, y debajo de cada uno los titulares que contiene. No hay nada fuera de esta lista: lo que no está aquí no está escrito. Pulse cualquiera y se abre; o escriba una palabra arriba a la izquierda y el buscador entra en el texto de los ocho documentos a la vez.</p>
          </div>
        </div>
        @@INDICE@@
      </div>
    </article>
    """

    CUERPO = """
    <a class="saltar" href="#lectura">Saltar al contenido</a>
    <div class="cen">

      <aside class="lado" id="lado">
        <div class="lado__cab">
          <a class="lado__marca" href="#portada" data-ir="portada">
            <strong>El Centro <b>Giraldo</b></strong>
            <span>Sistema completo · v@VERSION@</span>
          </a>
          <label class="busca">
            <svg width="14" height="14" viewBox="0 0 16 16" aria-hidden="true">
              <circle cx="7" cy="7" r="4.6" fill="none" stroke="currentColor" stroke-width="1.7"/>
              <path d="M10.4 10.4 L14.4 14.4" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/>
            </svg>
            <input id="q" type="search" autocomplete="off" spellcheck="false"
                   placeholder="Buscar en los ocho documentos" aria-label="Buscar en todo el sistema">
            <kbd>/</kbd>
          </label>
        </div>
        <nav class="arbol" id="arbol" aria-label="Índice completo del sistema">
          <a class="arbol__inicio" href="#portada" data-ir="portada">Portada e índice completo</a>
          @@ARBOL@@
        </nav>
      </aside>

      <div class="cen__col">
        <header class="cima">
          <button class="cima__menu" id="menu" type="button">Índice</button>
          <nav class="miga" id="miga" aria-label="Dónde está"></nav>
          <span class="cima__n" id="cuenta"></span>
          <div class="cima__pasos">
            <button id="ant" type="button" aria-label="Apartado anterior">&#8592;</button>
            <button id="sig" type="button" aria-label="Apartado siguiente">&#8594;</button>
          </div>
        </header>

        <main class="lectura" id="lectura" tabindex="-1">
          @@PORTADA@@
          @@HOJAS@@
          <div class="res" id="res" hidden></div>
          <div class="pieC">
            <span>Centro de Excelencia Implantológica Giraldo · Rúa Bolivia nº 2 · Vigo · Uso interno y confidencial</span>
            <span>v@VERSION@ · @FECHA@ · No medias sonrisas</span>
          </div>
        </main>
      </div>

    </div>
    """


    def sello(t):
        return (t.replace("@VERSION@", VERSION).replace("@FECHA@", FECHA)
                 .replace("@TOTAL@", str(TOTAL))
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
                    .replace("@@HOJAS@@", "\n".join(HOJAS)))

    datos = ('<script>window.__ORDEN__ = %s;</script>'
             % json.dumps([[c, d, g, r] for c, d, g, r in ORDEN], ensure_ascii=False))

    salida = RAIZ / "centro.html"
    salida.write_text(
        sello(cabecera + "\n" + cuerpo + "\n" + datos + "\n" + JS + "\n" + SELECTOR
              + "\n</body>\n</html>\n"),
        encoding="utf-8")
    print("centro.html · 8 documentos · %d apartados · %s caracteres · %d KB"
          % (TOTAL, "{:,}".format(CARACTERES).replace(",", "."), salida.stat().st_size // 1024))

if __name__ == "__main__":
    main()
