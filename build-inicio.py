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
    return (
        '<section class="idx__doc" data-doc="%d" data-buscable="%s">\n'
        '        <div class="idx__cab">\n'
        '          <h3><a href="%s">%s</a></h3>\n'
        '          <p class="idx__que">%s</p>\n'
        '        </div>\n'
        '        <ol class="idx__lista">%s</ol>\n'
        '      </section>' % (n, llano(x["rotulo"] + " " + x["que"]),
                             x["archivo"], x["rotulo"], x["que"], lista))


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
                  'de Excelencia Implantológica Giraldo: Tesis de Dirección, presentación de Junta, Manual '
                  'Maestro, Protocolo de Primera Visita, otros documentos del sistema y la hoja de captura '
                  'de la línea base.">', cabecera, count=1)

CSS = """
.puerta{display:grid;gap:1px;background:var(--line);border:1px solid var(--line);margin-top:1.6rem}
@media(min-width:820px){.puerta{grid-template-columns:repeat(2,minmax(0,1fr))}}
.puerta__ficha{
  background:var(--paper);padding:1.6rem;display:grid;gap:.6rem;align-content:start;
  text-decoration:none;color:inherit;transition:background .16s ease;min-width:0;
}
.puerta__ficha:hover{background:var(--surface)}
.puerta__ficha:hover h3{color:var(--accent-ink)}
.puerta__ficha--ancha{grid-column:1/-1;background:var(--accent-soft)}
.puerta__ficha--ancha:hover{background:rgba(14,124,116,.16)}
.puerta__ficha h3{font-size:var(--step-2);letter-spacing:-.015em}
.puerta__ficha p{color:var(--ink-2);font-size:.94rem;max-width:60ch}
.puerta__pie{
  margin-top:.4rem;display:flex;flex-wrap:wrap;gap:.4rem .9rem;
  font-family:var(--f-mono);font-size:.66rem;letter-spacing:.11em;
  text-transform:uppercase;color:var(--muted);
}
.puerta__pie b{color:var(--accent-ink);font-weight:400}
.puerta__flecha{font-family:var(--f-mono);color:var(--accent-ink);margin-left:auto}

/* ---------------------------------------------------------------------------
   Índice general. Va delante de todo lo demás porque es lo primero que uno
   quiere de un sistema de siete documentos: ver qué hay, entero, sin abrir nada.
   Dos niveles —apartado y subapartado— y un filtro, porque seiscientas líneas
   sin filtro no son un índice: son una pared.
   --------------------------------------------------------------------------- */
.idx__mando{
  display:flex;align-items:center;gap:.7rem 1rem;flex-wrap:wrap;margin-top:1.6rem;
  padding:.5rem .7rem;border:1px solid var(--line);background:var(--surface);
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
  font-family:var(--f-mono);font-size:.64rem;letter-spacing:.11em;text-transform:uppercase;
  color:var(--accent-ink);white-space:nowrap;
}
.idx__plegar{
  font:inherit;font-family:var(--f-mono);font-size:.62rem;letter-spacing:.1em;
  text-transform:uppercase;cursor:pointer;color:var(--ink-2);white-space:nowrap;
  background:var(--paper);border:1px solid var(--line);border-radius:999px;padding:.32rem .7rem;
}
.idx__plegar:hover{border-color:var(--ink-2);color:var(--ink)}
.idx__plegar[aria-pressed="true"]{
  background:var(--accent-soft);border-color:var(--accent);color:var(--accent-ink);
}

.idx{display:grid;gap:2.6rem;margin-top:2.2rem}
.idx__doc{background:var(--paper);min-width:0;padding-top:1.6rem;border-top:1px solid var(--line)}
.idx__doc[hidden]{display:none}
.idx__cab{max-width:62ch;margin-bottom:1.5rem}
.idx__cab h3{font-size:var(--step-2);letter-spacing:-.018em;margin:0 0 .35rem}
.idx__cab h3 a{color:inherit;text-decoration:none}
.idx__cab h3 a:hover{color:var(--accent-ink)}
.idx__que{color:var(--ink-2);font-size:.95rem;line-height:1.55}

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
 ("memoria.html", "Tesis de Dirección", "v@VERSION@ · 23 apartados · Anexos A y B",
  "El documento de gobierno. Posición competitiva y foso, sistema operativo y cartera de innovación, "
  "economía unitaria y creación de valor de empresa, riesgos y pre-mortem, el puente hasta el "
  "objetivo de 1,2 M€ con su cartera de nueve campañas, y las quince decisiones que se someten "
  "a la Junta. Incluye los dos cuadernillos: quince hojas de acta y nueve fichas de campaña.",
  "79 páginas en papel · lectura 55′", True),
 ("deck.html", "Presentación de Junta", "v@VERSION@ · %s diapositivas · 16:9" % DIAPOSITIVAS,
  "La tesis para proyectar. Se conduce con el teclado: <b>←</b> y <b>→</b> para pasar, "
  "<b>N</b> abre el guion del ponente con el minuto objetivo y la pregunta difícil, "
  "<b>E</b> filtra a la ruta corta de doce diapositivas para sesiones de veinte minutos.",
  "Proyección y guion del ponente", False),
 ("marketing.html", "Plan Maestro de Marketing", "v@VERSION@ · %s acciones · %s estados" % (ACCIONES, ESTADOS),
  "Todo lo que el centro puede hacer para que un paciente lo elija, lo entienda y se quede, "
  "organizado por el estado de su relación con su propia boca y no por canales. Catálogo completo "
  "con dueño, coste, plazo y semáforo legal; las diez piezas que nadie está haciendo en esta "
  "ciudad; el mapa de la ría y la Campaña de Mar.",
  "Documento de dirección", False),
 ("instrumentos/captura.html", "Captura de la línea base", "v@VERSION@ · 10 indicadores",
  "El instrumento del §7 y del §13: doce hojas mensuales, semáforo automático, resumen anual con "
  "tendencia y los cinco números. Se rellena aquí mismo y se guarda en este equipo.",
  "Se rellena en el navegador", False),
 ("manual.html", "Manual Maestro de Operaciones", "v@VERSION@ · 8 partes",
  "El documento troncal. Las catorce fases del recorrido del paciente, los manuales por puesto, la "
  "matriz RACI, los indicadores, el plan de incentivos y la puesta en marcha. Ocho partes "
  "numeradas, más el marco de vanguardia y los estándares transversales.",
  "204 páginas en papel", False),
 ("index.html", "Protocolo de Primera Visita", "v@VERSION@ · 12 fases de la primera visita",
  "El detalle minuto a minuto de la visita que decide la conversión, con estándares transversales, "
  "casos especiales, guiones contrastados y anexos.",
  "90 páginas en papel", False),
 ("otros.html", "Otros documentos del sistema", "v@VERSION@ · 14 documentos de apoyo",
  "Compendio maestro, verificación de 322 puntos, auditoría de la clínica adquirida, decisiones de "
  "Gerencia, programa de 100 días, protocolos por perfil, innovación, marca, «No medias sonrisas» y "
  "el programa Giraldo Te Cuida.",
  "135 páginas en papel", False),
]


# El número de documentos se cuenta; no se teclea. Decía «seis» con siete
# documentos y «siete» con ocho, que es el desfase de siempre.
LETRA = {5: "Cinco", 6: "Seis", 7: "Siete", 8: "Ocho", 9: "Nueve", 10: "Diez"}
CUANTOS = LETRA[len(FICHAS)]


def ficha(destino, titulo, etiqueta, texto, pie, ancha):
    return ('<a class="puerta__ficha%s" href="%s">\n'
            '        <p class="eyebrow">%s</p>\n'
            '        <h3>%s</h3>\n'
            '        <p>%s</p>\n'
            '        <p class="puerta__pie"><span>%s</span><span class="puerta__flecha">Abrir →</span></p>\n'
            '      </a>' % (" puerta__ficha--ancha" if ancha else "", destino, etiqueta, titulo, texto, pie))


CUERPO = """
<header class="topbar">
  <div class="wrap">
    <div class="topbar__in">
      <a class="brand" href="#portada">
        <span class="brand__mark">Sistema documental <b>Giraldo</b></span>
        <span class="brand__tag">v@VERSION@ · Uso interno</span>
      </a>
    </div>
  </div>
</header>

<main>

<section class="hero" id="portada">
  <div class="wrap">
    <div class="hero__grid">
      <div>
        <p class="eyebrow">Centro de Excelencia Implantológica Giraldo · Rúa Bolivia nº 2 · Vigo</p>
        <h1>No medias<br><em>sonrisas</em></h1>
        <p class="hero__lede">Lo que el centro cree, lo que decide y cómo lo ejecuta: @cuantos@ documentos que van de la tesis de dirección al minuto exacto en que se recibe a un paciente.</p>
      </div>
      <dl class="specs">
        <div class="spec"><dt>Documentos operativos</dt><dd>17<small>Tres troncales y catorce de apoyo. El censo completo, en §0.1 de la Tesis</small></dd></div>
        <div class="spec"><dt>Decisiones abiertas</dt><dd>15<small>Se someten a la Junta Directiva</small></dd></div>
        <div class="spec"><dt>Puntos de verificación</dt><dd>322<small>Físicos, documentales, de sistemas y de proceso</small></dd></div>
        <div class="spec"><dt>Objetivo</dt><dd>1,2 M€<small>Facturación anual en el ejercicio tercero, con nueve campañas</small></dd></div>
        <div class="spec"><dt>Acciones de marketing</dt><dd>@ACCIONES@<small>Sobre @ESTADOS@ estados del paciente. @SINCOSTE@ de ellas no cuestan dinero</small></dd></div>
        <div class="spec"><dt>Fases del recorrido</dt><dd>14<small>De la primera llamada al mantenimiento a largo plazo</small></dd></div>
      </dl>
    </div>
  </div>
</section>
<div class="wrap"><div class="ticks ticks--tall" aria-hidden="true"></div></div>

<section class="section" id="indice">
  <div class="wrap">
    <div class="section__head">
      <p class="eyebrow">Índice general</p>
      <h2>Todo lo que hay</h2>
    </div>

    <div class="idx__mando">
      <label class="idx__buscar">
        <svg width="15" height="15" viewBox="0 0 16 16" aria-hidden="true">
          <circle cx="7" cy="7" r="4.6" fill="none" stroke="currentColor" stroke-width="1.6"/>
          <path d="M10.4 10.4 L14.4 14.4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
        </svg>
        <input type="search" id="idx-filtro" autocomplete="off" spellcheck="false"
               placeholder="Filtrar el índice: escriba una palabra">
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

<section class="section">
  <div class="wrap">
    <div class="section__head">
      <p class="eyebrow">El sistema</p>
      <h2>Qué es cada cosa</h2>
      <p>El índice dice dónde está todo; esto dice para qué sirve cada pieza. La Tesis dirige, la presentación convence, el Plan de Marketing llena la agenda, el Manual y el Protocolo ejecutan, Otros documentos sostiene y la hoja de captura mide. Sin la última, todas las demás se apoyan en supuestos.</p>
    </div>
    <div class="puerta">
      @@FICHAS@@
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="callout" style="max-width:none">
      <p class="eyebrow">Sobre la naturaleza de las cifras</p>
      <p>Las cifras económicas de la Tesis y de la presentación son <strong>modelos sobre rangos del sector, marcados como tales</strong> en cada figura y registrados en su §18. No son datos del centro y no deben citarse como tales hasta que exista la línea base. Levantarla es exactamente para lo que sirve la hoja de captura.</p>
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
""".replace("@@FICHAS@@", "\n      ".join(ficha(*f) for f in FICHAS))


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
      ? "Puede estar en el cuerpo del texto: pulse <kbd>/</kbd> para buscar en los siete documentos enteros."
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
          .replace("@SINCOSTE@", SINCOSTE))
assert "@CUANTOS@" not in CUERPO and "@cuantos@" not in CUERPO, "queda alguna marca"

(RAIZ / "inicio.html").write_text(
    sello(cabecera + "\n" + CUERPO + "\n" + JS_INDICE + "\n</body>\n</html>\n"),
    encoding="utf-8")
print("inicio.html ·", (RAIZ / "inicio.html").stat().st_size // 1024, "KB")
