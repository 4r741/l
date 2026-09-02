#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""centro.html: el sistema documental contado como se cuenta un centro.

    python3 build-sitio.py

Los ocho documentos siguen siendo los que mandan y no se tocan. Lo que faltaba
era la otra puerta: una en la que no haga falta saber cómo se llama un
documento para encontrar lo que uno busca. Un paciente no pregunta «¿dónde está
el Manual Maestro?»; pregunta «¿qué me va a pasar el primer día?». Quien entra
a trabajar un lunes no pregunta por la Parte IV; pregunta «¿qué se espera de
mí?».

Doce áreas, una pregunta cada una, y debajo la literatura que la contesta —la
misma, entera, sin resumir y sin reescribir—, traída aquí en vez de enlazada.
Ahí estaba el salto raro: un enlace que sacaba al lector del protocolo de su
puesto y lo dejaba caer en mitad de otro documento, sin contexto y sin vuelta.
Aquí se lee donde se pregunta, y de cada pieza se dice de qué documento viene,
que es el que se cita en acta.
"""
import html as H
import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).parent
sys.path.insert(0, str(RAIZ))
import sitio as S  # noqa: E402

_v = {"__name__": "version_sitio", "__file__": "version.py"}
exec(compile((RAIZ / "version.py").read_text(encoding="utf-8"), "version.py", "exec"), _v)
VERSION, FECHA = _v["VERSION"], _v["FECHA"]

FUENTES = {}


def fuente(doc):
    if doc not in FUENTES:
        FUENTES[doc] = (RAIZ / doc).read_text(encoding="utf-8")
    return FUENTES[doc]


# ---------------------------------------------------------------------------
#  Sacar una pieza de literatura de su documento, entera y sin tocarla
# ---------------------------------------------------------------------------
ETIQUETA = re.compile(r"<([a-zA-Z][\w-]*)")
TITULARES = {"h1", "h2", "h3", "h4", "h5", "h6"}


def elemento(t, ini):
    """El elemento que empieza en «ini», entero, con sus etiquetas equilibradas.

    No vale cortar por el primer cierre: dentro hay secciones y artículos
    anidados —los bloques por puesto, las fichas de campaña, las fases— y el
    corte dejaba media pieza aquí y el resto del documento descolgado allí.
    """
    nombre = ETIQUETA.match(t, ini).group(1)
    abre = re.compile(r"<%s\b" % re.escape(nombre), re.I)
    cierra = re.compile(r"</%s\s*>" % re.escape(nombre), re.I)
    hondo, pos = 0, ini
    while True:
        a = abre.search(t, pos)
        c = cierra.search(t, pos)
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


def pieza(doc, ancla):
    """La literatura que cuelga de ese identificador.

    Si el identificador está en un titular, la pieza es la sección que lo
    contiene. Si está en el propio bloque —cada una de las doce fases de la
    primera visita es un <article> con su identificador—, la pieza es ese
    bloque. Esta segunda forma faltaba, y por eso las fases se quedaban en su
    documento mientras aquí solo llegaba el párrafo que las anuncia.
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


TABLA = re.compile(r"<table\b", re.I)


def entabla(cuerpo):
    """Toda tabla dentro de una caja que se desplace sola.

    En su documento las tablas anchas van envueltas; alguna suelta se quedó sin
    envolver y allí no se notaba, porque la columna era la página entera. Aquí
    la columna es más estrecha y en un teléfono la tabla se salía por la
    derecha y no había manera de leer la última columna.
    """
    fuera, pos = [], 0
    for m in TABLA.finditer(cuerpo):
        if m.start() < pos:
            continue
        antes = cuerpo[max(0, m.start() - 60):m.start()]
        entera = elemento(cuerpo, m.start())
        if entera is None:
            continue
        pos = m.start() + len(entera)
        if "tablewrap" in antes:
            continue
        fuera.append((m.start(), pos))
    for ini, fin in reversed(fuera):
        cuerpo = (cuerpo[:ini] + '<div class="tablewrap">' + cuerpo[ini:fin]
                  + "</div>" + cuerpo[fin:])
    return cuerpo


def prefija(cuerpo, marca):
    """Identificadores propios: doce áreas conviven en una página sin chocar."""
    cuerpo = re.sub(r'\bid="([^"]+)"', lambda m: 'id="%s%s"' % (marca, m.group(1)), cuerpo)
    for atr in ("headers", "aria-labelledby", "aria-describedby", "aria-controls"):
        cuerpo = re.sub(r'\b%s="([^"]+)"' % atr,
                        lambda m, a=atr: '%s="%s"' % (a, " ".join(marca + x
                                                                  for x in m.group(1).split())),
                        cuerpo)
    return cuerpo


def encabeza(cuerpo, n_area, n_pieza):
    """El número del apartado en su documento, por el de este sitio.

    Allí «02» quiere decir una cosa y aquí otra, y dos numeraciones a la vez no
    orientan a nadie. El titular baja de h2 a h3: el h2 de la página es el
    nombre del área.
    """
    cuerpo = re.sub(r'<b class="num">[^<]*</b>',
                    '<b class="num">%s.%d</b>' % (n_area, n_pieza), cuerpo, count=1)
    cuerpo = re.sub(r"<h2\b", "<h3", cuerpo, count=1)
    cuerpo = re.sub(r"</h2>", "</h3>", cuerpo, count=1)
    return cuerpo


def monta():
    """Las doce áreas, con su literatura dentro y sus enlaces cosidos."""
    areas, rail = [], []

    for i, area in enumerate(S.AREAS):
        marca = "s%s-" % area["n"]
        piezas, ids = [], set()
        for j, entrada in enumerate(area["enlaces"], 1):
            doc, ancla, rotulo = entrada[0], entrada[1], entrada[2]
            # Hay piezas que no se sostienen solas: el selector de puesto sin
            # sus seis fichas es un mando que no manda nada. Esas vienen juntas.
            crudo = pieza(doc, ancla)
            for extra in (entrada[3] if len(entrada) > 3 else []):
                crudo += "\n" + pieza(doc, extra)
            cuerpo = prefija(entabla(encabeza(crudo, area["n"], j)), marca)
            ids.update(re.findall(r'id="([^"]+)"', cuerpo))
            piezas.append((doc, ancla, rotulo, cuerpo))

        # Los enlaces internos que traía el texto: al de aquí si está aquí y,
        # si no, a su documento, marcados como salida. Ninguno muerto.
        def cose(m, ids=ids, marca=marca, doc=None):
            destino = m.group(1)
            if marca + destino in ids:
                return 'href="#%s%s"' % (marca, destino)
            return 'href="%s#%s" class="fuera"' % (doc, destino)

        cuerpos = []
        for j, (doc, ancla, rotulo, cuerpo) in enumerate(piezas, 1):
            cuerpo = re.sub(r'href="#([^"]+)"',
                            lambda m, d=doc: cose(m, doc=d), cuerpo)
            cuerpos.append(
                '<article class="pz" id="%s%s">\n'
                '  <p class="pz__de"><span>%s.%d</span> De <a href="%s#%s">%s</a></p>\n'
                '%s\n'
                '</article>' % (marca, ancla, area["n"], j, doc, ancla,
                                H.escape(S.ORIGEN[doc]), cuerpo))

        sig = S.AREAS[i + 1] if i + 1 < len(S.AREAS) else None
        ant = S.AREAS[i - 1] if i else None
        pasos = []
        if ant:
            pasos.append('<a class="pasa" href="#%s" data-va="%s">'
                         '<span>Área anterior</span><b>%s · %s</b></a>'
                         % (ant["id"], ant["id"], ant["n"], H.escape(ant["rotulo"])))
        if sig:
            pasos.append('<a class="pasa pasa--sig" href="#%s" data-va="%s">'
                         '<span>Área siguiente</span><b>%s · %s</b></a>'
                         % (sig["id"], sig["id"], sig["n"], H.escape(sig["rotulo"])))

        indice = "".join(
            '<li><a href="#%s%s"><span>%s.%d</span>%s</a></li>'
            % (marca, e[1], area["n"], j, H.escape(e[2]))
            for j, e in enumerate(area["enlaces"], 1))

        areas.append(
            '<section class="area" id="%s" data-area="%s">\n'
            '  <header class="area__cab">\n'
            '    <p class="area__n"><b>%s</b> Área %d de %d</p>\n'
            '    <h2>%s</h2>\n'
            '    <p class="area__q">%s</p>\n'
            '    <p class="area__que">%s</p>\n'
            '    <nav class="area__idx" aria-label="Lo que hay en esta área">\n'
            '      <p class="area__idx__t">%d piezas, en este orden</p>\n'
            '      <ol>%s</ol>\n'
            '    </nav>\n'
            '  </header>\n'
            '  <div class="area__cuerpo">\n%s\n  </div>\n'
            '  <nav class="pasos" aria-label="Áreas contiguas">%s</nav>\n'
            '</section>'
            % (area["id"], area["id"], area["n"], i + 1, len(S.AREAS),
               H.escape(area["rotulo"]), H.escape(area["pregunta"]), H.escape(area["que"]),
               len(cuerpos), indice, "\n".join(cuerpos), "".join(pasos)))

        # El raíl lleva un segundo nivel: las piezas del área abierta, para no
        # perderse dentro de un área larga —la primera visita son doce fases— y
        # poder saltar de una a otra sin volver arriba.
        sub = "".join(
            '<li><a href="#%s%s"><span>%s.%d</span>%s</a></li>'
            % (marca, e[1], area["n"], j, H.escape(e[2]))
            for j, e in enumerate(area["enlaces"], 1))
        rail.append(
            '<div class="rail__g" data-de="%s">'
            '<a class="rail__a" href="#%s" data-va="%s">'
            '<b>%s</b><span>%s</span><i>%s</i></a>'
            '<ol class="rail__sub">%s</ol></div>'
            % (area["id"], area["id"], area["id"], area["n"], H.escape(area["rotulo"]),
               H.escape(area["pregunta"]), sub))

    todo = "\n".join(areas)

    # ------------------------------------------------------------------
    #  Coser los enlaces entre documentos: aquí no se sale a ninguna parte
    # ------------------------------------------------------------------
    # Este era el salto raro. Dentro del protocolo de un puesto, la matriz RACI
    # enlazaba cada fase al Protocolo de Primera Visita: uno pulsaba «2 ·
    # Recepción y tour» y aparecía en mitad de otro documento, sin cabecera,
    # sin saber de dónde venía ni cómo volver. Aquí esa fase también está —es
    # el área 05—, así que el enlace se queda dentro y lleva a la pieza que la
    # cuenta. Solo sale fuera lo que de verdad no está en este sitio, y va
    # marcado con una flecha para que se vea antes de pulsar.
    aqui = {}
    for pref in re.findall(r'id="(s\d\d-[^"]+)"', todo):
        aqui.setdefault(pref.split("-", 1)[1], pref)

    docs = "|".join(re.escape(d) for d in S.ORIGEN)

    def dentro(m):
        destino = m.group(2)
        if destino in aqui:
            return 'href="#%s"' % aqui[destino]
        return 'href="%s#%s" class="fuera"' % (m.group(1), destino)

    # se traga el «class="fuera"» que pusiera la pasada anterior: un enlace que
    # ya se resolvió aquí dentro no puede seguir enseñando la flecha de salida
    todo = re.sub(r'href="(%s)#([^"]+)"(?: class="fuera")?' % docs, dentro, todo)
    # y el enlace al documento entero, sin ancla, que también sale
    todo = re.sub(r'href="(%s)"(?![^>]*class=)' % docs,
                  lambda m: 'href="%s" class="fuera"' % m.group(1), todo)
    return todo, "".join(rail)


# ---------------------------------------------------------------------------
#  La página
# ---------------------------------------------------------------------------
CSS = """
/* ---------------------------------------------------------------------------
   EL CENTRO, COMO SITIO

   Doce áreas y una sola columna de lectura. La navegación vive a la izquierda
   y no se mueve: se ve siempre dónde está uno, qué hay antes y qué hay después.
   Se lee un área cada vez —quinientos kilobytes de literatura en una columna
   continua no los recorre nadie— y cada pieza dice de qué documento viene.
   --------------------------------------------------------------------------- */
/* La altura de la barra: el raíl se pega justo debajo de ella. Sin este valor
   el «calc» quedaba inválido, «top» se resolvía en «auto» y el raíl no se
   pegaba a nada: se iba con la página en cuanto uno bajaba. El guion lo mide y
   lo corrige; esto es el valor de arranque. */
:root{--cabecera:70px}

.portico{
  background:var(--tinta);color:#fff;padding:5.5rem 0 5rem;margin-bottom:0;
}
.portico .eyebrow{color:rgba(255,255,255,.55)}
.portico h1{
  font-size:clamp(2.9rem,7vw,5.4rem);line-height:1.02;letter-spacing:-.028em;
  margin:1.6rem 0 0;max-width:16ch;
}
.portico h1 em{font-style:normal;color:var(--acido);display:block}
.portico__promesa{
  margin:2.4rem 0 0;font-family:var(--f-display);font-size:clamp(1.15rem,2.2vw,1.5rem);
  line-height:1.42;color:rgba(255,255,255,.86);max-width:42ch;
}
.portico__promesa small{
  display:block;margin-top:.9rem;font-family:var(--f-mono);font-size:.72rem;
  letter-spacing:.12em;text-transform:uppercase;color:rgba(255,255,255,.45);
}
.portico__pie{
  display:flex;flex-wrap:wrap;gap:2.4rem;margin-top:3.4rem;
  padding-top:2rem;border-top:1px solid rgba(255,255,255,.16);
}
.portico__pie div{min-width:9rem}
.portico__pie b{display:block;font-family:var(--f-display);font-size:1.6rem;color:var(--acido)}
.portico__pie span{
  display:block;margin-top:.35rem;font-family:var(--f-mono);font-size:.68rem;
  letter-spacing:.13em;text-transform:uppercase;color:rgba(255,255,255,.5);
}

/* --- el armazón: raíl fijo y una columna de lectura ---------------------- */
.sitio{
  display:grid;grid-template-columns:19rem minmax(0,1fr);gap:4rem;
  padding:3.4rem 0 5rem;
}
/* Sin esto la columna del raíl mide lo que mide el raíl y «sticky» no tiene
   dónde pegarse: se iba con el primer desplazamiento y el lector se quedaba
   sin saber en qué área estaba. */
.sitio > .rail{align-self:stretch}
.rail{
  position:sticky;top:calc(var(--cabecera) + 1.6rem);display:flex;flex-direction:column;gap:.15rem;
  /* doce áreas con su pregunta debajo no caben en una pantalla de portátil: el
     raíl se desplaza por dentro y no arrastra a la página */
  max-height:calc(100vh - var(--cabecera) - 3.2rem);overflow-y:auto;
  scrollbar-width:thin;padding-right:.4rem;
}
.rail__t{
  font-family:var(--f-mono);font-size:.66rem;letter-spacing:.16em;text-transform:uppercase;
  color:var(--muted);margin:0 0 1rem;padding-bottom:.7rem;border-bottom:1px solid var(--line);
}
.rail__a{
  display:grid;grid-template-columns:2.2rem 1fr;gap:.1rem .6rem;align-items:baseline;
  text-decoration:none;padding:.7rem .8rem;border-radius:var(--radio-s);
  border:1px solid transparent;transition:background .14s ease,border-color .14s ease;
}
.rail__a b{
  font-family:var(--f-mono);font-size:.7rem;font-weight:500;color:var(--muted);
  grid-row:1/3;
}
.rail__a span{font-size:.94rem;font-weight:500;color:var(--ink-2);line-height:1.3}
.rail__a i{
  grid-column:2;font-style:normal;font-size:.76rem;color:var(--muted);line-height:1.4;
  margin-top:.2rem;display:none;
}
.rail__a:hover{background:var(--surface-2)}
.rail__a:hover span{color:var(--ink)}
.rail__a.is-on{background:var(--surface);border-color:var(--line);box-shadow:var(--sombra-1)}
.rail__a.is-on b{color:var(--accent)}
.rail__a.is-on span{color:var(--tinta);font-weight:600}
.rail__a.is-on i{display:block}
.rail__g{display:contents}
.rail__sub{
  display:none;list-style:none;margin:.15rem 0 .9rem;padding:0 0 0 2.9rem;
  border-left:1px solid var(--line);margin-left:1.5rem;
}
.rail__g.is-on .rail__sub{display:block}
.rail__sub a{
  display:flex;gap:.55rem;align-items:baseline;text-decoration:none;
  color:var(--muted);font-size:.82rem;line-height:1.35;padding:.34rem .3rem;
  border-radius:5px;
}
.rail__sub a span{font-family:var(--f-mono);font-size:.63rem;flex:none}
.rail__sub a:hover{color:var(--ink);background:var(--surface-2)}
.rail__sub a.is-aqui{color:var(--accent-ink);font-weight:600}

/* --- la cabecera de cada área: la pregunta, delante ---------------------- */
.area{scroll-margin-top:calc(var(--cabecera) + 1rem)}
.area__cab{padding-bottom:3rem;margin-bottom:3.4rem;border-bottom:1px solid var(--line)}
.area__n{
  font-family:var(--f-mono);font-size:.7rem;letter-spacing:.15em;text-transform:uppercase;
  color:var(--muted);margin:0;
}
.area__n b{
  color:var(--accent-ink);background:var(--acido);border-radius:999px;
  padding:.16rem .55rem;margin-right:.7rem;font-weight:500;
}
.area__cab h2{font-size:clamp(2.1rem,4.6vw,3.3rem);margin:1.1rem 0 0;letter-spacing:-.025em}
.area__q{
  margin:1.4rem 0 0;font-family:var(--f-display);font-size:clamp(1.1rem,2.3vw,1.45rem);
  line-height:1.4;color:var(--accent-ink);max-width:34ch;font-weight:500;
}
.area__que{margin:1.5rem 0 0;font-size:1.02rem;line-height:1.65;color:var(--ink-2);max-width:62ch}
.area__idx{
  margin-top:2.6rem;background:var(--surface);border:1px solid var(--line);
  border-radius:var(--radio);padding:1.4rem 1.6rem 1.5rem;max-width:46rem;
}
.area__idx__t{
  margin:0 0 .9rem;font-family:var(--f-mono);font-size:.66rem;letter-spacing:.14em;
  text-transform:uppercase;color:var(--muted);
}
.area__idx ol{margin:0;padding:0;list-style:none;display:flex;flex-direction:column;gap:.1rem}
.area__idx a{
  display:flex;gap:.9rem;align-items:baseline;text-decoration:none;color:var(--ink-2);
  padding:.5rem .55rem;border-radius:var(--radio-s);font-size:.96rem;line-height:1.4;
}
.area__idx a span{font-family:var(--f-mono);font-size:.7rem;color:var(--muted);flex:none}
.area__idx a:hover{background:var(--surface-2);color:var(--ink)}

/* --- cada pieza de literatura, con su procedencia ------------------------ */
.pz{padding-top:.5rem}
.pz + .pz{margin-top:4.2rem;padding-top:4.2rem;border-top:1px solid var(--line-soft)}
.pz__de{
  margin:0 0 1.1rem;font-family:var(--f-mono);font-size:.68rem;letter-spacing:.1em;
  text-transform:uppercase;color:var(--muted);
}
.pz__de span{color:var(--accent);margin-right:.7rem}
.pz__de a{color:var(--ink-2)}
.pz__de a:hover{color:var(--accent-ink)}
/* La literatura llega con el envoltorio de su documento: aquí no hace falta
   otra caja dentro de la caja, ni otro ancho máximo distinto del de la columna. */
.pz .section{padding:0;background:none;border:0}
.pz .wrap{padding:0;max-width:none}
.pz .section__head{margin-bottom:1.8rem}
.pz h3{font-size:clamp(1.45rem,2.9vw,2rem);letter-spacing:-.02em;margin:.3rem 0 0}
/* La literatura del Manual y del Protocolo llega con la marca de aparición
   progresiva de su documento, que allí destapa un guion al hacer scroll. Aquí
   ese guion no viaja, y sin él las doce fases se quedaban invisibles: ochenta
   mil píxeles de página en blanco. */
.pz .reveal{opacity:1!important;transform:none!important}

/* Las fases traen una rejilla de dos columnas que su documento enciende a
   partir de 960 px de ventana. Aquí la ventana no es la columna: con el raíl a
   la izquierda, a 1280 px de pantalla la columna mide 850, y las tablas de la
   fase se salían por la derecha. Las dos columnas se encienden más tarde, ya
   con sitio de sobra. */
@media(max-width:1439px){
  .pz .phase__grid{grid-template-columns:minmax(0,1fr)}
  .pz .phase__meta{position:static}
}
.pz .phase__meta{top:calc(var(--cabecera) + 1.2rem)}
/* y lo que no quepa se desplaza dentro de su caja, nunca la página entera */
.pz .tablewrap{overflow-x:auto}

/* un enlace que sale del sitio se ve que sale */
a.fuera::after{content:"↗";font-size:.78em;margin-left:.22em;color:var(--muted)}

/* --- el paso al área siguiente, al final y no en mitad ------------------- */
.pasos{
  display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-top:5rem;
  padding-top:2.2rem;border-top:1px solid var(--line);
}
.pasa{
  display:block;text-decoration:none;padding:1.15rem 1.35rem;border-radius:var(--radio);
  border:1px solid var(--line);background:var(--surface);transition:border-color .14s ease;
}
.pasa:only-child{grid-column:2}
.pasa--sig{text-align:right}
.pasa span{
  display:block;font-family:var(--f-mono);font-size:.66rem;letter-spacing:.14em;
  text-transform:uppercase;color:var(--muted);
}
.pasa b{display:block;margin-top:.45rem;font-size:1.02rem;color:var(--tinta);font-weight:600}
.pasa:hover{border-color:var(--accent)}
.pasa:hover b{color:var(--accent-ink)}

/* Con guiones se lee un área cada vez; sin ellos —y al imprimir— se ven las
   doce seguidas, que es el documento entero. La marca la pone el instalador. */
.sitio--vivo .area{display:none}
.sitio--vivo .area.is-on{display:block;animation:entra .18s ease}
@media(prefers-reduced-motion:reduce){.sitio--vivo .area.is-on{animation:none}}

@media(max-width:1080px){
  .sitio{grid-template-columns:minmax(0,1fr);gap:2rem}
  .rail{
    position:sticky;top:var(--cabecera);z-index:20;flex-direction:row;gap:.5rem;
    overflow-x:auto;padding:.7rem 0;background:var(--paper);
    border-bottom:1px solid var(--line);scrollbar-width:none;
  }
  .rail::-webkit-scrollbar{display:none}
  .rail__t{display:none}
  .rail__a{
    grid-template-columns:auto;white-space:nowrap;flex:none;
    border:1px solid var(--line);background:var(--surface);padding:.5rem .9rem;
  }
  .rail__a b{grid-row:auto;margin-right:.45rem}
  .rail__a i{display:none!important}
  .rail__a.is-on{background:var(--tinta);border-color:var(--tinta)}
  .rail__a.is-on b,.rail__a.is-on span{color:#fff}
  .rail__g{display:contents}
  .rail__sub{display:none!important}
  .pasos{grid-template-columns:1fr}
  .pasa:only-child{grid-column:1}
  .pasa--sig{text-align:left}
}
@media print{
  .rail,.pasos,.portico__pie{display:none}
  .sitio{display:block}
  .area{break-before:page}
}
"""

JS = """
<script>
(function(){
  "use strict";
  var caja = document.querySelector(".sitio");
  if(!caja) return;
  var areas = [].slice.call(caja.querySelectorAll(".area"));
  var botones = [].slice.call(document.querySelectorAll(".rail__a, .pasa"));
  var grupos = [].slice.call(document.querySelectorAll(".rail__g"));
  if(!areas.length) return;
  /* La marca la pone el guion y no el marcado: si esto no llegara a correr, se
     ven las doce áreas seguidas —que es toda la literatura— en vez de una
     página en blanco. */
  caja.classList.add("sitio--vivo");

  /* La barra mide lo que mide —una línea en el escritorio, dos si el rótulo
     parte— y el raíl se pega justo debajo. */
  var barra = document.querySelector(".topbar");
  function mide(){
    if(!barra) return;
    document.documentElement.style.setProperty(
      "--cabecera", Math.round(barra.getBoundingClientRect().height) + "px");
  }
  mide();
  window.addEventListener("resize", mide);

  function pon(id, arriba, callado){
    var hay = false;
    areas.forEach(function(a){
      var si = a.dataset.area === id;
      a.classList.toggle("is-on", si);
      if(si) hay = true;
    });
    if(!hay){ return pon(areas[0].dataset.area, arriba, callado); }
    botones.forEach(function(b){
      b.classList.toggle("is-on", b.dataset.va === id && b.classList.contains("rail__a"));
    });
    grupos.forEach(function(g){ g.classList.toggle("is-on", g.dataset.de === id); });
    vigila();
    /* Al entrar sin dirección no se escribe ninguna: escribirla hacía que el
       navegador saltara al fragmento y el pórtico quedaba arriba, fuera de la
       pantalla, sin que nadie lo hubiera pedido. */
    if(!callado){ try { history.replaceState(null, "", "#" + id); } catch(e){} }
    if(arriba) window.scrollTo({top:0, behavior:"smooth"});
    return true;
  }

  /* Dentro de un área larga, cuál es la pieza que se está leyendo. Sin esto,
     doce fases seguidas son otra vez un río: se ve por dónde se va bajando. */
  var mirando = null;
  function vigila(){
    if(mirando) mirando.disconnect();
    var viva = areas.filter(function(a){ return a.classList.contains("is-on"); })[0];
    if(!viva || !("IntersectionObserver" in window)) return;
    var sub = document.querySelector('.rail__g[data-de="' + viva.dataset.area + '"] .rail__sub');
    if(!sub) return;
    var enlaces = {};
    [].slice.call(sub.querySelectorAll("a")).forEach(function(a){
      enlaces[a.getAttribute("href").slice(1)] = a;
    });
    mirando = new IntersectionObserver(function(entradas){
      entradas.forEach(function(en){
        var a = enlaces[en.target.id];
        if(!a) return;
        if(en.isIntersecting){
          [].slice.call(sub.querySelectorAll("a")).forEach(function(x){ x.classList.remove("is-aqui"); });
          a.classList.add("is-aqui");
        }
      });
    }, {rootMargin: "-18% 0px -70% 0px"});
    [].slice.call(viva.querySelectorAll(".pz")).forEach(function(z){ mirando.observe(z); });
  }

  document.addEventListener("click", function(e){
    var a = e.target.closest("a[data-va]");
    if(!a) return;
    e.preventDefault();
    pon(a.dataset.va, true);
  });

  /* Un enlace a una pieza concreta abre su área y baja hasta ella: ese era el
     salto raro, caer en mitad de un texto sin saber en qué parte se está. */
  document.addEventListener("click", function(e){
    var a = e.target.closest('a[href^="#"]');
    if(!a || a.dataset.va) return;
    var destino = document.getElementById(a.getAttribute("href").slice(1));
    if(!destino) return;
    var dueno = destino.closest(".area");
    if(!dueno) return;
    e.preventDefault();
    pon(dueno.dataset.area, false);
    destino.scrollIntoView({block:"start", behavior:"smooth"});
    try { history.replaceState(null, "", a.getAttribute("href")); } catch(err){}
  });

  window.addEventListener("hashchange", function(){
    var h = (location.hash || "").slice(1);
    if(!h) return;
    var d = document.getElementById(h);
    var dueno = d && d.closest(".area");
    if(dueno) pon(dueno.dataset.area, !d.classList.contains("pz"));
  });

  var h = (location.hash || "").slice(1);
  var d = h && document.getElementById(h);
  var dueno = d && d.closest ? d.closest(".area") : null;
  pon(dueno ? dueno.dataset.area : areas[0].dataset.area, false, !h);
  if(d && dueno && d !== dueno) d.scrollIntoView({block:"start"});
})();
</script>
"""

def hoja_propia(doc, marca):
    """El bloque de estilos que ese documento añade sobre el sistema común."""
    for b in re.findall(r"<style>(.*?)</style>", fuente(doc), re.S):
        if marca in b:
            return b
    raise SystemExit("  %s: no se encuentra su hoja propia (%s)" % (doc, marca))


def guion_propio(doc, marca):
    for g in re.findall(r"<script>.*?</script>", fuente(doc), re.S):
        if marca in g:
            return g
    raise SystemExit("  %s: no se encuentra su guion propio (%s)" % (doc, marca))


AREAS_HTML, RAIL_HTML = monta()

# El selector de puesto viaja con su hoja y su mando. Sin la hoja salían seis
# botones crudos del navegador; sin el guion, un mando que no manda nada.
CSS += "\n" + hoja_propia("protocolos.html", "PROTOCOLOS POR PUESTO")
SELECTOR = guion_propio("protocolos.html", "ES_PERFIL")
# Allí la dirección de la página nombra el puesto; aquí nombra el área, y son
# dos cosas distintas. El selector cambia de ficha sin tocar la dirección.
SELECTOR = re.sub(r"\n\s*var actual = location\.hash.*?\n\s*\}\n",
                  "\n", SELECTOR, count=1, flags=re.S)
SELECTOR = SELECTOR.replace(
    'var h = (location.hash || "").replace(ES_PERFIL, "");',
    'var h = "";')

manual = fuente("manual.html")
i = manual.index("<body>")
cabecera = manual[:i + len("<body>")]
cabecera = cabecera.replace("<title>Manual Maestro Giraldo</title>",
                            "<title>El Centro Giraldo · el sistema, por áreas</title>")
cabecera = re.sub(r'<meta name="description" content="[^"]*">',
                  '<meta name="description" content="El Centro de Excelencia Implantológica '
                  'Giraldo contado por áreas: quiénes somos, en qué creemos, cuál es el método, '
                  'quién es el equipo, cómo es la primera visita, qué hacemos, con qué, cómo '
                  'llega el paciente, los números, quién decide y cómo se pone en marcha.">',
                  cabecera, count=1)
k = cabecera.rindex("</style>")
cabecera = cabecera[:k] + CSS + "\n" + cabecera[k:]

CUERPO = """
<header class="topbar">
  <div class="wrap">
    <div class="topbar__in">
      <a class="brand" href="#a-quien-es-giraldo">
        <span class="brand__mark">El Centro <b>Giraldo</b></span>
        <span class="brand__tag">El sistema por áreas · v@VERSION@</span>
      </a>
      <a class="crosslink" href="inicio.html">Los ocho documentos</a>
      <a class="crosslink" href="protocolos.html">Protocolos por puesto</a>
      <a class="crosslink" href="instrumentos/captura.html">Los números</a>
    </div>
@@BARRA@@
  </div>
</header>

<main id="contenido" tabindex="-1">

<section class="portico">
  <div class="wrap">
    <p class="eyebrow">Centro de Excelencia Implantológica Giraldo · Rúa Bolivia nº 2 · Vigo</p>
    <h1>No medias <em>sonrisas</em></h1>
    <p class="portico__promesa">«Le devolvemos su sonrisa completa, en el menor tiempo posible, y le cuidamos para siempre.»
      <small>La promesa, completa · Plan de Dirección</small></p>
    <div class="portico__pie">
      <div><b>@AREAS@</b><span>áreas, una pregunta cada una</span></div>
      <div><b>@PIEZAS@</b><span>piezas de literatura, enteras</span></div>
      <div><b>8</b><span>documentos detrás, sin resumir</span></div>
      <div><b>14</b><span>fases del recorrido del paciente</span></div>
    </div>
  </div>
</section>

<div class="wrap">
  <div class="sitio">
    <nav class="rail" aria-label="Áreas del centro">
      <p class="rail__t">El centro, por áreas</p>
      @@RAIL@@
    </nav>
    <div class="sitio__lectura">
@@AREAS@@
    </div>
  </div>
</div>

</main>

<footer class="foot">
  <div class="wrap">
    <div class="foot__grid">
      <div><p><strong>Centro de Excelencia Implantológica Giraldo</strong><br>Rúa Bolivia nº 2 · Vigo · Uso interno y confidencial</p></div>
      <div><p class="eyebrow">Lema</p><p>No medias sonrisas.<br>Ni medias decisiones.</p></div>
      <div><p class="eyebrow">Versión</p><p>v@VERSION@ · @FECHA@<br>La misma de los ocho documentos</p></div>
    </div>
    <p class="foot__nota">Esta página no sustituye a ningún documento: los trae. Cada pieza dice de cuál viene, y ese es el que se cita en acta.</p>
  </div>
</footer>
"""


def sello(t):
    return (t.replace("@VERSION@", VERSION).replace("@FECHA@", FECHA)
             .replace("@AREAS@", str(len(S.AREAS)))
             .replace("@PIEZAS@", str(sum(len(a["enlaces"]) for a in S.AREAS))))


cuerpo = (CUERPO.replace("@@RAIL@@", RAIL_HTML)
                .replace("@@AREAS@@", AREAS_HTML)
                .replace("@@BARRA@@", ""))

salida = RAIZ / "centro.html"
salida.write_text(sello(cabecera + "\n" + cuerpo + "\n" + JS + "\n" + SELECTOR
                        + "\n</body>\n</html>\n"),
                  encoding="utf-8")
print("centro.html · %d áreas · %d piezas · %d KB"
      % (len(S.AREAS), sum(len(a["enlaces"]) for a in S.AREAS), salida.stat().st_size // 1024))
