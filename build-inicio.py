#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera inicio.html: la puerta de entrada a todo el sistema documental.

    python3 build-inicio.py
"""
import re
from pathlib import Path

RAIZ = Path(__file__).parent

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



_check = (RAIZ / "check-coherencia.py").read_text(encoding="utf-8")
def canonica(nombre):
    return re.search(r'"%s": (\d+)' % nombre, _check).group(1)
DIAPOSITIVAS = canonica("diapositivas de la presentación")
ACCIONES = canonica("acciones del catálogo de marketing")
ESTADOS = canonica("estados del paciente")
_cat = (RAIZ / "catalogo-acciones.py").read_text(encoding="utf-8")
_ns = {"__name__": "catalogo_portada", "__file__": "catalogo-acciones.py"}
exec(compile(_cat, "catalogo-acciones.py", "exec"), _ns)
SINCOSTE = str(_ns["calcula"]()["sin_coste"])

_menu = {"__name__": "menu_portada", "__file__": "menu.py"}
exec(compile((RAIZ / "menu.py").read_text(encoding="utf-8"), "menu.py", "exec"), _menu)
BARRA_MENU = _menu["dibuja"]("inicio.html", "    ")

_idx = {"__name__": "indice_portada", "__file__": "indice.py"}
exec(compile((RAIZ / "indice.py").read_text(encoding="utf-8"), "indice.py", "exec"), _idx)
INDICE = _idx["calcula"]()
APARTADOS = sum(len(x["entradas"]) for x in INDICE)


def bloque_indice(x, n):
    """Un documento del índice: qué es y qué contiene.

    El detalle no se enseña de entrada. Con 646 líneas abiertas a la vez el
    índice dejaba de ser un índice y pasaba a ser una pared de letra pequeña: no
    se lee, se sufre. Ahora se ve el documento y sus apartados, y el que tiene
    detalle lo dice con un número a la derecha; se abre el que interese.
    """
    filas = []
    for e in x["entradas"]:
        hijos = "".join(
            '<li><a href="%s#%s" data-buscable="%s">%s</a></li>'
            % (x["archivo"], h["ancla"], llano(h["rotulo"]), h["rotulo"])
            for h in e["hijos"])
        abre = ""
        if hijos:
            abre = ('<button class="idx__abre" type="button" aria-expanded="false" '
                    'aria-label="Ver los %d apartados de %s">%d</button>'
                    % (len(e["hijos"]), e["rotulo"].replace('"', "&quot;"), len(e["hijos"])))
        filas.append(
            '<li class="idx__rama">'
            '<span class="idx__fila">'
            '<a class="idx__uno" href="%s#%s" data-buscable="%s">%s</a>%s</span>%s</li>'
            % (x["archivo"], e["ancla"], llano(e["rotulo"]), e["rotulo"], abre,
               ('<ol class="idx__dos" hidden>%s</ol>' % hijos) if hijos else ""))
    lista = "".join(filas) or '<li class="idx__sin">Se recorre entera, diapositiva a diapositiva.</li>'
    cuenta = ("%d apartados" % len(x["entradas"])) if x["entradas"] else "sin apartados"
    # Cada documento nace plegado, y con <details>, que se abre y se cierra sin
    # una línea de guion. Desplegados los siete a la vez eran tres mil
    # ochocientos píxeles de lista: un índice que no se recorre no es un índice.
    return (
        '<details class="idx__doc" data-doc="%d" data-buscable="%s">\n'
        '        <summary class="idx__sum">\n'
        '          <span class="idx__sum__t">\n'
        '            <h3>%s</h3>\n'
        '            <p class="idx__que">%s</p>\n'
        '          </span>\n'
        '          <span class="idx__sum__n">%s</span>\n'
        '        </summary>\n'
        '        <div class="idx__cuerpo">\n'
        '          <ol class="idx__lista">%s</ol>\n'
        '          <p class="idx__ir"><a href="%s">Abrir %s &#8594;</a></p>\n'
        '        </div>\n'
        '      </details>' % (n, llano(x["rotulo"] + " " + x["que"]),
                             x["rotulo"], x["que"], cuenta, lista,
                             x["archivo"], x["rotulo"]))


def llano(s):
    """Sin tildes y en minúscula, para que el filtro no exija acentuar."""
    import unicodedata
    s = unicodedata.normalize("NFD", s)
    return "".join(c for c in s if unicodedata.category(c) != "Mn").lower()


INDICE_HTML = "\n      ".join(bloque_indice(x, n) for n, x in enumerate(INDICE))
SUBAPARTADOS = sum(len(e["hijos"]) for x in INDICE for e in x["entradas"])

manual = (RAIZ / "manual.html").read_text(encoding="utf-8")
i = manual.index("<body>")
cabecera = manual[:i + len("<body>")]
cabecera = cabecera.replace("<title>Manual Maestro Giraldo</title>",
                            "<title>Sistema documental Giraldo</title>")
cabecera = re.sub(r'<meta name="description" content="[^"]*">',
                  '<meta name="description" content="Puerta de entrada al sistema documental del Centro '
                  'de Excelencia Implantológica Giraldo: Plan de Dirección, presentación de Junta, Manual '
                  'Maestro, Protocolo de Primera Visita, otros documentos del sistema y la hoja '
                  'mensual de los números del centro.">', cabecera, count=1)

CSS = """
/* ---------------------------------------------------------------------------
   LA PORTADA

   Estaba del revés. Lo primero era un índice de ciento veinticuatro apartados
   con seiscientos cuarenta y seis titulares debajo, y las siete puertas —lo
   único que uno viene a hacer aquí, que es abrir un documento— quedaban a
   cuatro mil cuatrocientos píxeles de scroll. Se entraba a la portada por el
   índice analítico. Ahora: quién es esto, qué documento abro, y sólo después,
   para el que busca algo concreto, el índice de todo el sistema.
   --------------------------------------------------------------------------- */

/* La franja de cifras: seis datos en un renglón, sin cajas. Antes eran seis
   fichas con borde compitiendo con el titular, y ninguna llevaba a ningún
   sitio: son contexto, no navegación, y deben pesar como contexto. */
/* La portada del sistema, en el mismo lenguaje que el tablero de cada
   documento: una rejilla bento con el lema en negro, la cifra que manda en
   verde pleno y el resto en gris. */
.bento{
  display:grid;gap:.6rem;margin:0 0 .6rem;
  grid-template-columns:repeat(2,minmax(0,1fr));
}
@media(min-width:820px){.bento{grid-template-columns:repeat(4,minmax(0,1fr))}}
@media(min-width:1180px){.bento{grid-template-columns:repeat(6,minmax(0,1fr))}}
.bento__lema{
  grid-column:1/-1;background:var(--tinta);color:#fff;border-radius:var(--radio);
  padding:2.4rem 2rem 2.2rem;display:flex;flex-direction:column;justify-content:flex-end;
  min-height:16rem;
}
@media(min-width:820px){.bento__lema{grid-column:span 4;grid-row:span 2}}
.bento__lema .eyebrow{
  font-family:var(--f-mono);font-size:.68rem;letter-spacing:.14em;
  text-transform:uppercase;color:var(--acido);margin:0 0 1rem;
}
.bento__lema h1{
  font-size:var(--step-4);font-weight:800;font-variation-settings:"wdth" 112;
  letter-spacing:-.045em;line-height:.9;color:#fff;margin:0;
}
.bento__lema h1 em{font-style:normal;color:var(--acido)}
.bento__lema p{
  margin:1.1rem 0 0;max-width:48ch;font-size:var(--step-0);line-height:1.5;
  color:rgba(255,255,255,.7);
}
.cifras{
  display:contents;list-style:none;margin:0;padding:0;
}
.cifras li{
  background:var(--surface-2);border-radius:var(--radio-s);
  padding:1.15rem 1.2rem 1.2rem;min-width:0;
  display:flex;flex-direction:column;justify-content:flex-end;
}
@media(min-width:820px){.cifras li{grid-column:span 2}}
.cifras b{
  display:block;font-weight:700;font-variation-settings:"wdth" 112;
  font-size:clamp(1.9rem,3.4vw,2.9rem);letter-spacing:-.045em;line-height:.9;
  color:var(--tinta);font-variant-numeric:tabular-nums;
}
.cifras i{
  display:block;font-style:normal;margin-top:.7rem;font-size:.74rem;font-weight:600;
  letter-spacing:.06em;text-transform:uppercase;color:var(--accent-ink);
}
.cifras span{display:block;font-size:.78rem;line-height:1.4;color:var(--muted);margin-top:.3rem}
.cifras li:first-child{background:var(--accent);color:#fff}
@media(min-width:1180px){.cifras li:first-child{grid-column:span 2;grid-row:span 2}}
.cifras li:first-child b{color:#fff;font-size:clamp(2.4rem,4.6vw,4rem)}
.cifras li:first-child i{color:var(--acido)}
.cifras li:first-child span{color:rgba(255,255,255,.75)}
@media(max-width:640px){
  .bento__lema{min-height:0;padding:1.6rem 1.3rem 1.5rem}
  .cifras li{padding:.9rem .95rem 1rem}
  .cifras b{font-size:1.7rem}
  .cifras i{font-size:.68rem;margin-top:.5rem}
  .cifras span{display:none}
  .cifras li:first-child span{display:block;font-size:.72rem}
}

/* Las siete puertas. Tarjetas de borde fino que se invierten al pasar por
   encima: negro pleno y la flecha en ácido. */
.puerta{
  display:grid;gap:.6rem;margin-top:1.8rem;
  grid-template-columns:repeat(auto-fill,minmax(min(320px,100%),1fr));
}
.puerta__ficha{
  background:var(--surface);border:1px solid var(--line);border-radius:var(--radio);
  padding:1.5rem 1.5rem 1.3rem;
  display:grid;gap:.5rem;align-content:start;grid-template-rows:auto auto 1fr auto;
  text-decoration:none;color:inherit;min-width:0;
  transition:background .18s ease,color .18s ease,border-color .18s ease,transform .18s ease;
}
.puerta__ficha:hover{
  background:var(--tinta);border-color:var(--tinta);color:#fff;transform:translateY(-3px);
}
.puerta__para{
  font-family:var(--f-mono);font-size:.66rem;letter-spacing:.12em;
  text-transform:uppercase;color:var(--accent-ink);margin:0;
}
.puerta__ficha:hover .puerta__para{color:var(--acido)}
.puerta__ficha h3{
  font-size:1.35rem;font-weight:700;font-variation-settings:"wdth" 104;
  letter-spacing:-.028em;line-height:1.1;margin:0;
}
.puerta__que{color:var(--ink-2);font-size:.92rem;line-height:1.5;margin:0}
.puerta__ficha:hover .puerta__que{color:rgba(255,255,255,.72)}
.puerta__pie{
  margin:1rem 0 0;padding-top:.85rem;border-top:1px solid var(--line-soft);
  display:flex;flex-wrap:wrap;gap:.3rem .9rem;align-items:baseline;
  font-family:var(--f-mono);font-size:.68rem;letter-spacing:.03em;color:var(--muted);
}
.puerta__ficha:hover .puerta__pie{border-top-color:rgba(255,255,255,.18);color:rgba(255,255,255,.6)}
.puerta__flecha{color:var(--accent-ink)}
.puerta__para{
  font-size:.74rem;font-weight:600;letter-spacing:.02em;
  color:var(--accent-ink);margin:0;
}
.puerta__ficha h3{
  font-size:1.18rem;line-height:1.22;letter-spacing:-.015em;margin:0;
  transition:color .16s ease;
}
.puerta__que{color:var(--ink-2);font-size:.9rem;line-height:1.5;margin:0}
.puerta__pie{
  margin:.85rem 0 0;padding-top:.75rem;border-top:1px solid var(--line-soft);
  display:flex;flex-wrap:wrap;gap:.3rem .9rem;align-items:baseline;
  font-size:.76rem;color:var(--muted);
}
.puerta__flecha{margin-left:auto;color:var(--accent-ink);font-weight:500}
.puerta__ficha:hover .puerta__flecha{color:var(--acido)}

/* La portada no necesita ocupar seiscientos píxeles antes de la primera
   puerta: dice quién es y sigue. */
.hero{padding:clamp(1.6rem,3.5vw,2.6rem) 0 2rem}
.hero h1{margin:.3rem 0 0}
.hero__lede{margin-top:1rem;max-width:58ch;font-size:var(--step-1);color:var(--ink-2)}
.section--puertas{padding-top:0}

/* ---------------------------------------------------------------------------
   Índice general. Ya no abre la página: la cierra. Cada documento nace
   plegado, porque ciento veinticuatro apartados desplegados de golpe son tres
   mil ochocientos píxeles de lista que nadie recorre. Se abre el que interese,
   o se escribe una palabra y el filtro abre los que la llevan.
   --------------------------------------------------------------------------- */
.idx__mando{
  display:flex;align-items:center;gap:.7rem 1rem;flex-wrap:wrap;margin-top:1.6rem;
  padding:.6rem .85rem;border:1px solid var(--line);border-radius:var(--radio);
  background:var(--surface);box-shadow:var(--sombra-1);
  /* Se queda a la vista mientras se recorre el índice, pero por debajo de la
     barra y no detrás de ella: pegado a top:0 el filtro se metía bajo la
     cabecera fija justo cuando hay 649 líneas que filtrar. */
  position:sticky;top:var(--barra);z-index:20;
}
.idx__buscar{display:flex;align-items:center;gap:.55rem;flex:1 1 260px;min-width:0;color:var(--muted)}
.idx__buscar input{
  flex:1;min-width:0;font:inherit;font-family:var(--f-body);font-size:.95rem;
  color:var(--ink);background:transparent;border:0;outline:none;padding:.3rem 0;
}
.idx__buscar input::placeholder{color:var(--muted)}
.idx__buscar input::-webkit-search-cancel-button{display:none}
.idx__marcador{
  font-size:.82rem;font-weight:600;color:var(--accent-ink);white-space:nowrap;
}
.idx__plegar{
  font:inherit;font-size:.84rem;font-weight:500;cursor:pointer;color:var(--ink-2);
  white-space:nowrap;background:var(--surface);border:1px solid var(--line);
  border-radius:999px;padding:.38rem .9rem;box-shadow:var(--sombra-1);
}
.idx__plegar:hover{border-color:var(--ink-2);color:var(--ink)}
.idx__plegar[aria-pressed="true"]{
  background:var(--accent-soft);border-color:var(--accent);color:var(--accent-ink);
}

.idx{
  display:grid;gap:1px;margin-top:1.6rem;background:var(--line);
  border:1px solid var(--line);border-radius:var(--radio);overflow:hidden;
}
.idx__doc{background:var(--surface);min-width:0}
.idx__doc[hidden]{display:none}
.idx__sum{
  display:flex;align-items:baseline;gap:1rem;cursor:pointer;list-style:none;
  padding:1.05rem 1.3rem;transition:background .14s ease;
}
.idx__sum::-webkit-details-marker{display:none}
.idx__sum::marker{content:""}
.idx__sum:hover{background:var(--accent-soft)}
.idx__sum:hover h3{color:var(--accent-ink)}
.idx__sum:focus-visible{outline:2px solid var(--accent);outline-offset:-2px}
.idx__sum__t{min-width:0;flex:1}
.idx__sum h3{
  font-size:1.16rem;letter-spacing:-.015em;margin:0;transition:color .14s ease;
}
.idx__que{color:var(--muted);font-size:.88rem;line-height:1.5;margin:.2rem 0 0}
.idx__sum__n{
  flex:0 0 auto;font-family:var(--f-mono);font-size:.68rem;letter-spacing:.06em;
  color:var(--muted);white-space:nowrap;
}
/* El triángulo lo dibujamos: el nativo cambia de forma en cada navegador. */
.idx__sum__n::after{
  content:"";display:inline-block;margin-left:.7rem;vertical-align:.06em;
  border:4px solid transparent;border-top-color:var(--muted);
  transform-origin:50% 25%;transition:transform .16s ease;
}
.idx__doc[open] .idx__sum__n::after{transform:rotate(180deg)}
.idx__doc[open] .idx__sum{background:var(--accent-soft)}
.idx__doc[open] .idx__sum h3{color:var(--accent-ink)}
.idx__cuerpo{padding:.2rem 1.3rem 1.3rem;border-top:1px solid var(--line)}
.idx__ir{margin:1rem 0 0}
.idx__ir a{
  font-family:var(--f-mono);font-size:.7rem;letter-spacing:.06em;
  color:var(--accent-ink);text-decoration:none;
}
.idx__ir a:hover{text-decoration:underline}

/* Los apartados en columnas, con aire. Antes cada línea llevaba una barra
   vertical a la izquierda: setecientas barras no ordenan nada, solo ensucian. */
.idx__lista{list-style:none;margin:0;padding:0;columns:2;column-gap:3rem}
@media(max-width:860px){.idx__lista{columns:1}}
.idx__rama{break-inside:avoid;margin:0 0 .1rem}
.idx__rama[hidden]{display:none}
/* El tirador va pegado al título y no al borde de la columna: sueltos a la
   derecha parecían etiquetas puestas ahí por casualidad. */
.idx__fila{display:flex;align-items:center;gap:.15rem}
.idx__uno{
  min-width:0;font-size:.96rem;line-height:1.45;
  color:var(--ink);text-decoration:none;padding:.34rem 0;
  border-bottom:1px solid transparent;transition:color .14s ease,border-color .14s ease;
}
.idx__uno:hover{color:var(--accent-ink);border-bottom-color:var(--accent)}

/* Cuánto hay dentro, y el modo de verlo. Sin caja ni relleno: una cifra
   pequeña al lado del título, que solo se dibuja cuando el ratón pasa por
   encima. Un apartado sin cifra es un apartado sin más detalle. */
.idx__abre{
  flex:0 0 auto;font:inherit;font-family:var(--f-mono);font-size:.63rem;
  color:var(--muted);background:transparent;border:1px solid transparent;
  border-radius:999px;min-width:1.45rem;height:1.45rem;cursor:pointer;
  display:flex;align-items:center;justify-content:center;
  transition:color .14s ease,border-color .14s ease,background .14s ease;
}
.idx__rama:hover .idx__abre{border-color:var(--line)}
.idx__abre:hover{color:var(--accent-ink);border-color:var(--accent)}
.idx__abre:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-color:var(--accent)}
.idx__abre[aria-expanded="true"]{
  background:var(--accent-soft);border-color:var(--accent);color:var(--accent-ink);
}

.idx__dos{list-style:none;margin:.05rem 0 .8rem;padding:0 0 0 .9rem;border-left:1px solid var(--line)}
.idx__dos[hidden]{display:none}
.idx__dos li[hidden]{display:none}
.idx__dos a{
  display:block;font-size:.87rem;line-height:1.45;color:var(--ink-2);text-decoration:none;
  padding:.26rem 0;transition:color .14s ease;
}
.idx__dos a:hover{color:var(--accent-ink)}
.idx__uno mark,.idx__dos mark{background:rgba(14,143,132,.2);color:inherit;border-radius:2px;padding:0 .05em}
/* Donde se toca con el dedo, cada línea tiene que ser un blanco de verdad. */
@media(pointer:coarse),(max-width:640px){
  .idx__uno{padding-top:.45rem;padding-bottom:.45rem}
  .idx__dos a{padding-top:.4rem;padding-bottom:.4rem}
  .idx__abre{height:1.9rem;min-width:2.2rem}
}
.idx__sin{color:var(--muted);font-size:.85rem}
.idx__vacio{margin-top:1.4rem;color:var(--muted)}
.idx__vacio b{color:var(--ink-2);font-weight:500}
.idx__vacio-mas{display:block;margin-top:.3rem;font-size:.94em}
.idx__vacio-mas kbd{
  font-family:var(--f-mono);font-size:.8em;background:var(--surface);
  border:1px solid var(--line);border-radius:3px;padding:.05rem .32rem;color:var(--ink-2);
}
.idx__vacio[hidden]{display:none}

@media print{
  .idx__mando{display:none}
  .idx__abre{display:none}
  /* En papel no hay nada que pulsar: el índice sale entero. */
  .idx__dos[hidden]{display:block!important}
  .idx__doc{break-inside:avoid}
  .idx__cab{position:static}
  .idx__lista{columns:2}
  .idx__uno,.idx__dos a{color:var(--ink-2)}
}
"""
k = cabecera.rindex("</style>")
cabecera = cabecera[:k] + CSS + "\n" + cabecera[k:]

FICHAS = [
 ("memoria.html", "Plan de Dirección", "El documento de gobierno",
  "Posición, sistema, economía y riesgo, el puente hasta 1,2 M€ y las quince "
  "decisiones que se someten a la Junta.",
  "23 apartados · 79 páginas · lectura 55′"),
 ("deck.html", "Presentación de Junta", "Para proyectar en la sesión",
  "La apuesta en @DIAPOS@ diapositivas. Se conduce con el teclado: <b>←</b> y <b>→</b> pasan, "
  "<b>N</b> abre el guion del ponente, <b>E</b> deja la ruta corta de veinte minutos.",
  "@DIAPOS@ diapositivas · 16:9"),
 ("protocolos.html", "Protocolos por puesto", "Qué se espera de cada uno",
  "Elija Dirección, Doctor, Recepción, RAC, Auxiliar o Higienista y vea en qué fases "
  "interviene, con qué papel y qué procedimientos tiene escritos.",
  "6 puestos · 14 fases"),
 ("manual.html", "Manual Maestro de Operaciones", "El documento troncal",
  "Las catorce fases del recorrido, los manuales por puesto, la matriz RACI, "
  "los indicadores, los incentivos y la puesta en marcha.",
  "8 partes · 204 páginas"),
 ("index.html", "Protocolo de Primera Visita", "La visita que decide",
  "Las doce fases minuto a minuto, con estándares, casos especiales, guiones "
  "contrastados y anexos.",
  "12 fases · 90 páginas"),
 ("marketing.html", "Plan Maestro de Marketing", "Cómo llega el paciente",
  "Las @ACCIONES@ acciones ordenadas por el estado de la relación del paciente con su "
  "propia boca, y el programa Giraldo Te Cuida, que es lo que hace que se quede.",
  "@ACCIONES@ acciones · @ESTADOS@ estados"),
 ("otros.html", "Otros documentos del sistema", "Los catorce de apoyo",
  "Compendio maestro, verificación de 322 puntos, auditoría de la clínica adquirida, "
  "100 días, protocolos por perfil, innovación, marca y continuidad legal.",
  "14 documentos · 135 páginas"),
 ("instrumentos/captura.html", "Los números del centro", "El instrumento que mide",
  "Doce hojas mensuales con semáforo automático, resumen anual y los cinco números. "
  "Se rellena aquí mismo y se guarda en este equipo.",
  "10 indicadores · se rellena en el navegador"),
]


# El número de documentos se cuenta; no se teclea. Decía «seis» con siete
# documentos y «siete» con ocho, que es el desfase de siempre.
LETRA = {5: "Cinco", 6: "Seis", 7: "Siete", 8: "Ocho", 9: "Nueve", 10: "Diez"}
CUANTOS = LETRA[len(FICHAS)]


def ficha(destino, titulo, para, texto, medida):
    """Una puerta. Las siete iguales.

    La del Plan de Dirección ocupaba dos columnas y su texto se quedaba en la
    mitad izquierda: novecientos píxeles de verde vacío a la derecha. Y el
    texto de cada una tenía seis renglones, que en una rejilla de puertas nadie
    lee: lo que hace falta ahí es saber cuál abrir.
    """
    return ('<a class="puerta__ficha" href="%s">\n'
            '        <p class="puerta__para">%s</p>\n'
            '        <h3>%s</h3>\n'
            '        <p class="puerta__que">%s</p>\n'
            '        <p class="puerta__pie"><span>%s</span>'
            '<span class="puerta__flecha">Abrir &#8594;</span></p>\n'
            '      </a>' % (destino, para, titulo, texto, medida))


CUERPO = """
<header class="topbar">
  <div class="wrap">
    <div class="topbar__in">
      <a class="brand" href="#portada">
        <span class="brand__mark">Sistema documental <b>Giraldo</b></span>
        <span class="brand__tag">v@VERSION@ · Uso interno</span>
      </a>
    </div>
@@BARRA@@
  </div>
</header>

<main>

<section class="hero" id="portada">
  <div class="wrap">
    <div class="bento">
      <div class="bento__lema">
        <p class="eyebrow">Centro de Excelencia Implantológica Giraldo · Rúa Bolivia nº 2 · Vigo</p>
        <h1>No medias <em>sonrisas</em></h1>
        <p>Lo que el centro cree, lo que decide y cómo lo ejecuta: @cuantos@ documentos que van del plan de dirección al minuto exacto en que se recibe a un paciente.</p>
      </div>
    <ul class="cifras">
      <li><b>1,2 M€</b><i>Objetivo</i><span>facturación anual del ejercicio tercero</span></li>
      <li><b>15</b><i>Decisiones abiertas</i><span>se someten a la Junta Directiva</span></li>
      <li><b>17</b><i>Normativa interna</i><span>tres troncales y catorce de apoyo</span></li>
      <li><b>322</b><i>Puntos de verificación</i><span>físicos, documentales y de proceso</span></li>
      <li><b>@ACCIONES@</b><i>Acciones de marketing</i><span>@SINCOSTE@ de ellas no cuestan dinero</span></li>
      <li><b>14</b><i>Fases del recorrido</i><span>de la primera llamada al mantenimiento</span></li>
    </ul>
    </div>
  </div>
</section>

<section class="section section--puertas" id="documentos">
  <div class="wrap">
    <div class="section__head">
      <p class="eyebrow">Por dónde se empieza</p>
      <h2>@CUANTOS@ documentos</h2>
      <p>El Plan de Dirección dirige, la presentación convence, el Manual y el Protocolo ejecutan, los Protocolos por puesto dicen a cada uno qué le toca, el Plan de Marketing llena la agenda, Otros documentos sostiene y los números del centro miden. Sin la última, todas las demás se apoyan en supuestos.</p>
    </div>
    <div class="puerta">
      @@FICHAS@@
    </div>
  </div>
</section>

<div class="wrap"><div class="ticks" aria-hidden="true"></div></div>

<section class="section" id="indice">
  <div class="wrap">
    <div class="section__head">
      <p class="eyebrow">Índice general</p>
      <h2>Buscar en todo el sistema</h2>
      <p>@APARTADOS@ apartados y @SUBAPARTADOS@ titulares, de los @cuantos@ documentos a la vez. Escriba una palabra y el índice se queda con lo que la lleva; o abra el documento que le interese.</p>
    </div>

    <div class="idx__mando">
      <label class="idx__buscar">
        <svg width="15" height="15" viewBox="0 0 16 16" aria-hidden="true">
          <circle cx="7" cy="7" r="4.6" fill="none" stroke="currentColor" stroke-width="1.6"/>
          <path d="M10.4 10.4 L14.4 14.4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
        </svg>
        <input type="search" id="idx-filtro" autocomplete="off" spellcheck="false"
               placeholder="Escriba una palabra: «RACI», «pre-mortem», «consentimiento»…">
      </label>
      <p class="idx__marcador" id="idx-marcador" role="status" aria-live="polite" aria-atomic="true">@APARTADOS@ apartados</p>
      <button type="button" class="idx__plegar" id="idx-plegar" aria-pressed="false">Abrir todo el detalle</button>
    </div>

    <div class="idx" id="idx">
      @INDICE@
    </div>
    <p class="idx__vacio" id="idx-vacio" hidden>Ningún <b>titular</b> lleva ese texto.<span class="idx__vacio-mas"></span></p>
  </div>
</section>

<div class="wrap"><div class="ticks" aria-hidden="true"></div></div>

<section class="section" id="cifras">
  <div class="wrap">
    <div class="callout" style="max-width:none">
      <p class="eyebrow">Sobre la naturaleza de las cifras</p>
      <p>Las cifras económicas del Plan de Dirección y de la presentación son <strong>modelos sobre rangos del sector, marcados como tales</strong> en cada figura y registrados en su apartado 18. No son datos del centro y no deben citarse como tales hasta que exista la línea base. Levantarla es exactamente para lo que sirve la hoja de los números del centro.</p>
    </div>
  </div>
</section>

</main>

<footer class="foot">
  <div class="wrap">
    <div class="ticks" aria-hidden="true" style="margin-bottom:2rem"></div>
    <div class="foot__grid">
      <div>
        <p><strong>Centro de Excelencia Implantológica Giraldo</strong><br>Sistema documental · Uso interno y confidencial</p>
      </div>
      <div><p class="eyebrow">Lema</p><p>No medias sonrisas.<br>Ni medias decisiones.</p></div>
      <div><p class="eyebrow">Versiones</p><p>Versión única del sistema<br><strong>v@VERSION@ · @FECHA@</strong></p></div>
    </div>
  </div>
</footer>
""".replace("@@FICHAS@@", "\n      ".join(ficha(*f) for f in FICHAS)) \
         .replace("@@BARRA@@", BARRA_MENU)


# ---------------------------------------------------------------------------
# El comportamiento del índice. Vive aquí y no en el guion común porque es lo
# único que tiene la portada, y porque dentro del archivo único ese guion se
# sustituye entero: si estuviera allí, se perdería.
# ---------------------------------------------------------------------------
JS_INDICE = """
<script>
(function(){
  "use strict";

  /* ---- por dónde sigue una tira que se desplaza ---- */
  (function(){
    if(window.__TIRAS__) return; window.__TIRAS__ = 1;
    var tiras = [].slice.call(document.querySelectorAll(".strip,.strip--nota,.cabecera__docs"));
    if(!tiras.length) return;
    function estado(t){
      var mas = t.scrollWidth - t.clientWidth;
      t.classList.toggle("hay-izq", mas > 2 && t.scrollLeft > 2);
      t.classList.toggle("hay-der", mas > 2 && t.scrollLeft < mas - 2);
    }
    tiras.forEach(function(t){
      estado(t);
      t.addEventListener("scroll", function(){ estado(t); }, {passive:true});
      if("ResizeObserver" in window) new ResizeObserver(function(){ estado(t); }).observe(t);
    });
    window.addEventListener("resize", function(){ tiras.forEach(estado); });
    /* al conmutar de documento la tira cambia de contenido sin que nada haga
       scroll: hay que volver a mirarla */
    document.addEventListener("click", function(){ setTimeout(function(){ tiras.forEach(estado); }, 60); }, true);
  })();


  /* ---- saltar al contenido ---- */
  (function(){
    if(document.querySelector(".saltar")) return;
    var a = document.createElement("a");
    a.className = "saltar";
    a.href = "#";
    a.textContent = "Saltar al contenido";
    function cuerpo(){
      var todos = [].slice.call(document.querySelectorAll("main"));
      for(var i = 0; i < todos.length; i++){
        if(todos[i].getBoundingClientRect().height > 0) return todos[i];
      }
      return todos[0] || null;
    }
    /* El destino se calcula al enfocar y no al cargar: en el archivo único el
       documento visible cambia, y con él el contenido al que hay que saltar. */
    a.addEventListener("focus", function(){
      var m = cuerpo();
      /* Si el contenido no tiene identificador se le pone uno, para que el
         enlace sea un enlace de verdad y no un «#» que solo funciona con
         guion. */
      if(m && !m.id) m.id = "contenido";
      a.href = (m && m.id) ? "#" + m.id : "#";
    });
    a.addEventListener("click", function(e){
      var m = cuerpo();
      if(!m) return;
      e.preventDefault();
      m.setAttribute("tabindex", "-1");
      m.focus();
      m.scrollIntoView({behavior:"instant", block:"start"});
    });
    document.body.insertBefore(a, document.body.firstChild);
  })();

  /* ---- una tabla ancha se recorre también con el teclado ---- */
  (function(){
    if(window.__TABLAS__) return; window.__TABLAS__ = 1;
    function limpio(el){
      return el ? el.textContent.trim().replace(/\s+/g, " ").slice(0, 70) : "";
    }
    function titulo(t){
      /* Lo más cercano por encima: primero los hermanos anteriores, que es donde
         suele estar el titular de la tabla; si no, el titular del apartado que
         la contiene. Una tabla anunciada solo como «tabla desplazable» no dice
         de qué es, y en Otros documentos hay veintiuna. */
      var n = t.previousElementSibling, saltos = 0;
      while(n && saltos < 5){
        if(/^H[2-5]$/.test(n.tagName)) return limpio(n);
        var h = n.querySelector && n.querySelector("h2,h3,h4,h5");
        if(h) return limpio(h);
        n = n.previousElementSibling; saltos++;
      }
      var caja = t.closest("section,article,.phase,.section");
      while(caja){
        var d = caja.querySelector("h2,h3,h4");
        if(d) return limpio(d);
        caja = caja.parentElement && caja.parentElement.closest("section,article");
      }
      return "";
    }
    function repasar(){
      [].slice.call(document.querySelectorAll(".tablewrap")).forEach(function(t){
        var ancha = t.scrollWidth > t.clientWidth + 2;
        if(ancha && !t.hasAttribute("tabindex")){
          t.setAttribute("tabindex", "0");
          t.setAttribute("role", "region");
          var q = titulo(t);
          t.setAttribute("aria-label", q ? "Tabla desplazable: " + q : "Tabla desplazable");
        } else if(!ancha && t.hasAttribute("tabindex")){
          t.removeAttribute("tabindex"); t.removeAttribute("role"); t.removeAttribute("aria-label");
        }
      });
    }
    repasar();
    window.addEventListener("resize", repasar);
    window.addEventListener("load", repasar);
    document.addEventListener("click", function(){ setTimeout(repasar, 80); }, true);
  })();


  /* ---- mapa del documento ---- */
  (function(){
    if(window.__MAPA__) return; window.__MAPA__ = 1;

    function construye(raiz, tira){
      var enlaces = [].slice.call(tira.querySelectorAll("a[href^='#']"));
      /* Con pocos apartados el mapa no aporta: la tira ya los enseña todos. */
      if(enlaces.length < 6) return null;
      var destinos = [];
      enlaces.forEach(function(a){
        var d = document.getElementById(a.getAttribute("href").slice(1));
        if(d) destinos.push({a:a, d:d, r:a.textContent.trim()});
      });
      if(destinos.length < 6) return null;

      var mapa = document.createElement("nav");
      mapa.className = "mapa";
      mapa.setAttribute("aria-label", "Mapa del documento");
      destinos.forEach(function(x, i){
        var b = document.createElement("button");
        b.type = "button";
        b.className = "mapa__m";
        b.dataset.i = String(i);
        b.setAttribute("aria-label", "Ir a " + x.r);
        var r = document.createElement("span");
        r.className = "mapa__r";
        r.textContent = x.r;
        b.appendChild(r);
        mapa.appendChild(b);
        x.b = b;
      });
      document.body.appendChild(mapa);
      return {mapa:mapa, destinos:destinos};
    }

    /* La altura de cada marca es la que ocupa su apartado, con un mínimo para
       que los cortos sigan siendo pulsables. */
    function reparte(m){
      var alto = m.mapa.clientHeight - (m.destinos.length - 1) * 2;
      var tramos = m.destinos.map(function(x, i){
        var fin = (i + 1 < m.destinos.length)
          ? m.destinos[i + 1].d.getBoundingClientRect().top + window.scrollY
          : document.documentElement.scrollHeight;
        return Math.max(1, fin - (x.d.getBoundingClientRect().top + window.scrollY));
      });
      var suma = tramos.reduce(function(a, b){ return a + b; }, 0) || 1;
      m.destinos.forEach(function(x, i){
        x.b.style.height = Math.max(9, Math.round(alto * tramos[i] / suma)) + "px";
      });
    }

    var estado = null;
    function arranca(){
      /* Dentro del archivo único solo vale la tira del documento que está
         abierto. Si ese documento no tiene tira —la portada y la presentación no
         la tienen—, no hay mapa: cayendo al primer `.strip` que apareciera se
         dibujaba el mapa de otro documento encima del que se está leyendo. */
      var tira = document.querySelector(".cabecera")
        ? document.querySelector(".cabecera .strip:not([hidden]):not(.strip--nota)")
        : (document.querySelector("#strip") || document.querySelector(".strip:not(.strip--nota)"));
      if(estado){ estado.mapa.remove(); estado = null; }
      if(!tira) return;
      estado = construye(document, tira);
      if(!estado) return;
      var m = estado;
      m.mapa.addEventListener("click", function(e){
        var b = e.target.closest(".mapa__m");
        if(!b) return;
        var x = m.destinos[+b.dataset.i];
        if(x) x.d.scrollIntoView({behavior:"instant", block:"start"});
      });
      reparte(m);
      window.addEventListener("resize", function(){ reparte(m); });
      marca();
    }

    function marca(){
      if(!estado) return;
      var y = window.scrollY + window.innerHeight * 0.35, actual = 0;
      estado.destinos.forEach(function(x, i){
        if(x.d.getBoundingClientRect().top + window.scrollY <= y) actual = i;
      });
      estado.destinos.forEach(function(x, i){
        x.b.setAttribute("aria-current", String(i === actual));
      });
    }
    window.addEventListener("scroll", marca, {passive:true});

    arranca();
    window.addEventListener("load", function(){ if(estado) reparte(estado); });
    /* En el archivo único el documento visible cambia y con él su mapa. */
    document.addEventListener("click", function(e){
      if(e.target.closest("[data-ir-a]")) setTimeout(arranca, 120);
    }, true);
  })();

  /* ---- volver arriba ---- */
  (function(){
    if(document.querySelector(".volver")) return;
    var quieto = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var caja = document.createElement("div");
    caja.className = "volver";
    function boton(rotulo, etiqueta, dibujo){
      var b = document.createElement("button");
      b.type = "button";
      b.setAttribute("aria-label", etiqueta);
      b.innerHTML = dibujo + "<span>" + rotulo + "</span>";
      caja.appendChild(b);
      return b;
    }
    var FLECHA = '<svg width="11" height="11" viewBox="0 0 12 12" aria-hidden="true">' +
      '<path d="M6 10.5V2M6 2 2.2 5.8M6 2l3.8 3.8" fill="none" stroke="currentColor" ' +
      'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>';
    var LISTA = '<svg width="11" height="11" viewBox="0 0 12 12" aria-hidden="true">' +
      '<path d="M1.6 2.5h8.8M1.6 6h8.8M1.6 9.5h5.6" fill="none" stroke="currentColor" ' +
      'stroke-width="1.6" stroke-linecap="round"/></svg>';
    boton("Arriba", "Volver al principio del documento", FLECHA)
      .addEventListener("click", function(){
        window.scrollTo({top:0, behavior: quieto ? "auto" : "smooth"});
      });
    document.body.appendChild(caja);
    var visible = false;
    function mirar(){
      var debe = window.scrollY > window.innerHeight * 1.2;
      if(debe !== visible){ visible = debe; caja.classList.toggle("se-ve", debe); }
    }
    mirar();
    window.addEventListener("scroll", mirar, {passive:true});
    window.addEventListener("resize", mirar);
  })();


  /* ---- alto real de la barra, para que ningún salto quede debajo ----
     En el archivo único esta barra no existe —la sustituye la cabecera común,
     que se mide sola— y esta parte se retira sin hacer nada. */
  (function(){
    var barra = document.querySelector(".topbar");
    if(!barra) return;
    function medir(){
      document.documentElement.style.setProperty(
        "--barra", Math.round(barra.getBoundingClientRect().height) + "px");
    }
    medir();
    window.addEventListener("resize", medir);
    if("ResizeObserver" in window) new ResizeObserver(medir).observe(barra);
  })();

  /* Se busca por clase y no por identificador a propósito: el archivo único
     prefija todos los id al fundir los siete documentos en uno, y un
     getElementById fijo dejaba el filtro muerto justo en el archivo, que es
     donde más falta hace. */
  var caja = document.querySelector(".idx");
  var campo = document.querySelector(".idx__buscar input");
  if(!caja || !campo) return;
  var marcador = document.querySelector(".idx__marcador");
  var vacio = document.querySelector(".idx__vacio");
  var plegar = document.querySelector(".idx__plegar");

  /* El índice busca en titulares, no en el texto. Una palabra puede estar en
     el sistema sin ser el título de nada —«miedo» lo está cinco veces y no
     encabeza ningún apartado—, y un «no hay nada» ahí sería mentira. Donde
     existe la búsqueda a texto completo, el vacío la ofrece. */
  var mas = document.querySelector(".idx__vacio-mas");
  if(mas){
    mas.innerHTML = document.querySelector(".paleta")
      ? "Puede estar en el cuerpo del texto: pulse <kbd>/</kbd> para buscar en los ocho documentos enteros."
      : "El índice recorre titulares, no el cuerpo del texto. Pruebe con menos palabras o abra el documento.";
  }
  var docs = [].slice.call(caja.querySelectorAll(".idx__doc"));
  var ramas = [].slice.call(caja.querySelectorAll(".idx__rama"));
  var hijos = [].slice.call(caja.querySelectorAll(".idx__dos li"));
  var total = ramas.length;

  function llano(s){
    return s.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  }
  /* Principio de palabra: si no, «acta» sale dentro de «exactamente». */
  function casa(texto, trozo){
    var i = texto.indexOf(trozo);
    while(i > -1){
      if(i === 0 || !/[a-z0-9]/.test(texto.charAt(i - 1))) return true;
      i = texto.indexOf(trozo, i + 1);
    }
    return false;
  }
  function casan(texto, trozos){
    for(var i = 0; i < trozos.length; i++) if(!casa(texto, trozos[i])) return false;
    return true;
  }
  function pinta(a, trozos){
    var texto = a.textContent;
    if(!trozos.length){ a.textContent = texto; return; }
    var plano = llano(texto), mejor = -1, largo = 0;
    trozos.forEach(function(p){
      var i = plano.indexOf(p);
      while(i > -1 && !(i === 0 || !/[a-z0-9]/.test(plano.charAt(i - 1)))) i = plano.indexOf(p, i + 1);
      if(i > -1 && (mejor < 0 || i < mejor)){ mejor = i; largo = p.length; }
    });
    if(mejor < 0){ a.textContent = texto; return; }
    a.textContent = "";
    a.appendChild(document.createTextNode(texto.slice(0, mejor)));
    var m = document.createElement("mark");
    m.textContent = texto.slice(mejor, mejor + largo);
    a.appendChild(m);
    a.appendChild(document.createTextNode(texto.slice(mejor + largo)));
  }

  /* Abrir y cerrar un apartado. El estado vive en el botón, que es quien lo
     anuncia, y la lista solo obedece. */
  function abre(rama, si){
    var b = rama.querySelector(".idx__abre");
    var ol = rama.querySelector(".idx__dos");
    if(!b || !ol) return;
    b.setAttribute("aria-expanded", String(si));
    ol.hidden = !si;
  }

  caja.addEventListener("click", function(e){
    var b = e.target.closest(".idx__abre");
    if(!b) return;
    var rama = b.closest(".idx__rama");
    abre(rama, b.getAttribute("aria-expanded") !== "true");
    sincroniza();
  });

  /* El botón del mando dice lo que va a pasar, no lo que pasó: si queda algo
     cerrado, abre; si está todo abierto, cierra. */
  function sincroniza(){
    if(!plegar) return;
    var conDetalle = ramas.filter(function(r){ return r.querySelector(".idx__abre"); });
    var abiertas = conDetalle.filter(function(r){
      return r.querySelector(".idx__abre").getAttribute("aria-expanded") === "true";
    }).length;
    var todo = abiertas === conDetalle.length && conDetalle.length > 0;
    plegar.setAttribute("aria-pressed", String(abiertas > 0));
    plegar.textContent = todo ? "Cerrar el detalle" : "Abrir todo el detalle";
  }

  function filtra(){
    var trozos = llano(campo.value).split(/\s+/).filter(Boolean);
    var apartados = 0, sueltos = 0;
    docs.forEach(function(doc){
      var suyas = 0;
      [].slice.call(doc.querySelectorAll(".idx__rama")).forEach(function(rama){
        var uno = rama.querySelector(".idx__uno");
        var propios = [].slice.call(rama.querySelectorAll(".idx__dos li"));
        var padreCasa = !trozos.length || casan(uno.dataset.buscable, trozos);
        var conHijos = 0;
        propios.forEach(function(li){
          var a = li.querySelector("a");
          /* Si el apartado casa, se enseñan todos sus hijos: el lector busca un
             capítulo y quiere verlo entero, no recortado. */
          var ok = padreCasa || casan(a.dataset.buscable, trozos);
          li.hidden = !ok;
          if(ok){ conHijos++; pinta(a, padreCasa ? [] : trozos); }
        });
        var ok = padreCasa || conHijos > 0;
        rama.hidden = !ok;
        if(ok){
          pinta(uno, trozos);
          apartados++; suyas++;
          /* Buscando, lo encontrado se abre solo; con el campo vacío se vuelve
             al estado de reposo, que es cerrado. */
          if(trozos.length) abre(rama, !padreCasa && conHijos > 0);
          else abre(rama, false);
          if(trozos.length && !padreCasa) sueltos += conHijos;
        }
      });
      /* Un documento se ve si le queda algún apartado a la vista, o si es él
         mismo lo que se busca. La presentación no tiene apartados —es un pase
         de diapositivas, no un texto con secciones— y aun así forma parte del
         sistema: desaparecer del índice por no tener índice propio sería una
         manera rara de contar lo que hay. */
      var propio = !trozos.length || casan(doc.dataset.buscable || "", trozos);
      doc.hidden = !suyas && !propio;
      if(propio && !suyas) apartados++;
      /* Buscando, el documento que tiene algo se abre solo; con el campo vacío
         se vuelve al reposo, que es cerrado. */
      if(trozos.length) doc.open = !doc.hidden;
      else doc.open = false;
    });
    if(vacio) vacio.hidden = apartados > 0;
    if(marcador){
      var n = apartados + sueltos;
      marcador.textContent = trozos.length
        ? (n + (n === 1 ? " resultado" : " resultados"))
        : total + " apartados";
    }
    sincroniza();
  }

  campo.addEventListener("input", filtra);
  campo.addEventListener("keydown", function(e){
    if(e.key === "Escape"){ campo.value = ""; filtra(); }
  });
  if(plegar){
    plegar.addEventListener("click", function(){
      var conDetalle = ramas.filter(function(r){ return r.querySelector(".idx__abre"); });
      var abiertas = conDetalle.filter(function(r){
        return r.querySelector(".idx__abre").getAttribute("aria-expanded") === "true";
      }).length;
      var todo = abiertas === conDetalle.length && conDetalle.length > 0;
      conDetalle.forEach(function(r){ abre(r, !todo); });
      docs.forEach(function(d){ d.open = !todo; });
      sincroniza();
    });
  }
  /* La barra inclinada lleva al filtro, como en el resto del sistema. */
  document.addEventListener("keydown", function(e){
    var t = e.target;
    if(t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.isContentEditable)) return;
    if(e.key === "/" && !e.ctrlKey && !e.metaKey){
      e.preventDefault();
      campo.scrollIntoView({block:"center", behavior:"smooth"});
      campo.focus();
    }
  });
  filtra();
})();
</script>
"""


CUERPO = (CUERPO.replace("@INDICE@", INDICE_HTML)
          .replace("@APARTADOS@", str(APARTADOS))
          .replace("@SUBAPARTADOS@", str(SUBAPARTADOS))
          .replace("@LINEAS@", str(APARTADOS + SUBAPARTADOS))
          .replace("@CUANTOS@", CUANTOS).replace("@cuantos@", CUANTOS.lower())
          .replace("@ACCIONES@", ACCIONES).replace("@ESTADOS@", ESTADOS)
          .replace("@SINCOSTE@", SINCOSTE)
          .replace("@DIAPOS@", str(DIAPOSITIVAS)))
assert "@CUANTOS@" not in CUERPO and "@cuantos@" not in CUERPO, "queda alguna marca"

(RAIZ / "inicio.html").write_text(
    sello(cabecera + "\n" + CUERPO + "\n" + JS_INDICE + "\n</body>\n</html>\n"),
    encoding="utf-8")
print("inicio.html ·", (RAIZ / "inicio.html").stat().st_size // 1024, "KB")
