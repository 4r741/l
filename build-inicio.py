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


def bloque_indice(x):
    """Un documento del índice: qué es, para quién, y todos sus apartados."""
    enlaces = "".join(
        '<li><a href="%s#%s">%s</a></li>' % (x["archivo"], e["ancla"], e["rotulo"])
        for e in x["entradas"]) or '<li class="idx__sin">Sin apartados numerados</li>'
    return (
        '<section class="idx__doc">\n'
        '        <div class="idx__cab">\n'
        '          <p class="eyebrow">%s</p>\n'
        '          <h3><a href="%s">%s</a></h3>\n'
        '          <p class="idx__que">%s</p>\n'
        '          <p class="idx__quien">Para <b>%s</b> · <span>%d apartados</span></p>\n'
        '        </div>\n'
        '        <ol class="idx__lista">%s</ol>\n'
        '      </section>' % (x["clase"], x["archivo"], x["rotulo"], x["que"],
                             x["quien"], len(x["entradas"]), enlaces))


INDICE_HTML = "\n      ".join(bloque_indice(x) for x in INDICE)

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
   --------------------------------------------------------------------------- */
.idx{display:grid;gap:1px;background:var(--line);border:1px solid var(--line);margin-top:1.8rem}
.idx__doc{background:var(--paper);padding:1.5rem 1.6rem 1.7rem;display:grid;gap:1rem;min-width:0}
@media(min-width:900px){.idx__doc{grid-template-columns:minmax(0,270px) minmax(0,1fr);gap:2.4rem}}
.idx__cab{align-self:start}
.idx__cab h3{font-size:var(--step-1);letter-spacing:-.015em;margin:.15rem 0 .4rem}
.idx__cab h3 a{color:inherit;text-decoration:none;border-bottom:1px solid var(--line)}
.idx__cab h3 a:hover{color:var(--accent-ink);border-color:var(--accent)}
.idx__que{color:var(--ink-2);font-size:.9rem;max-width:44ch}
.idx__quien{
  margin-top:.5rem;font-family:var(--f-mono);font-size:.64rem;letter-spacing:.1em;
  text-transform:uppercase;color:var(--muted);
}
.idx__quien b{color:var(--ink-2);font-weight:400}
.idx__quien span{color:var(--accent-ink)}
.idx__lista{
  list-style:none;margin:0;padding:0;columns:2;column-gap:2rem;
  font-size:.88rem;line-height:1.45;
}
@media(max-width:620px){.idx__lista{columns:1}}
.idx__lista li{break-inside:avoid;margin:0 0 .2rem}
.idx__lista a{
  color:var(--ink-2);text-decoration:none;display:block;padding:.14rem .3rem .14rem 0;
  border-left:2px solid transparent;padding-left:.55rem;transition:color .14s ease,border-color .14s ease;
}
.idx__lista a:hover{color:var(--accent-ink);border-left-color:var(--accent)}
.idx__sin{color:var(--muted);font-size:.85rem;padding-left:.55rem}
@media print{
  .idx__doc{break-inside:avoid}
  .idx__lista a{color:var(--ink-2)}
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
        <p class="hero__lede">@CUANTOS@ documentos que se abren en cualquier navegador, sin instalar nada y sin conexión. Todos comparten la versión <strong>v@VERSION@</strong>: si uno cambia lo bastante como para merecer versión nueva, la reciben todos.</p>
        <p class="hero__note">Uso interno y confidencial. Contiene información económica, laboral y estratégica. No se difunde fuera de la organización sin autorización expresa de la Dirección General.</p>
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
      <p>@APARTADOS@ apartados repartidos en @cuantos@ documentos. Está entero: no es una selección ni un resumen. Cualquier línea de esta lista abre el apartado correspondiente en su documento.</p>
    </div>
    <div class="idx">
      @INDICE@
    </div>
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
    <div class="section__head">
      <p class="eyebrow">Cómo se abren</p>
      <h2>Sin instalar nada</h2>
    </div>
    <div class="cards" style="grid-template-columns:repeat(auto-fit,minmax(min(280px,100%),1fr))">
      <div class="card"><p class="eyebrow">En este equipo</p><h3>Doble clic</h3><p>Cada archivo es una página completa: se abre en el navegador que tenga instalado, sin conexión y sin ningún programa adicional. Mantenga los @cuantos@ en la misma carpeta para que los enlaces entre ellos funcionen.</p></div>
      <div class="card"><p class="eyebrow">En papel</p><h3>Imprimir</h3><p>Todos llevan hoja de estilos de impresión: A4 con cabecera de clasificación, numeración y tablas que repiten su encabezado. La presentación sale apaisada, una diapositiva por página.</p></div>
      <div class="card"><p class="eyebrow">Para repartir</p><h3>La carpeta entera</h3><p>Copie la carpeta completa en una memoria o envíela comprimida. No hay servidor, ni cuenta, ni dependencia externa: lo que ve aquí es todo lo que hace falta.</p></div>
    </div>
    <div class="callout" style="max-width:none">
      <p class="eyebrow">Una advertencia que no conviene saltarse</p>
      <p>Las cifras económicas de la Tesis y de la presentación son <strong>modelos sobre rangos del sector, marcados como tales</strong> en cada figura y registradas en su §18. No son datos del centro y no deben citarse como tales hasta que exista la línea base. Levantarla es exactamente para lo que sirve la hoja de captura.</p>
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

CUERPO = (CUERPO.replace("@INDICE@", INDICE_HTML)
          .replace("@APARTADOS@", str(APARTADOS))
          .replace("@CUANTOS@", CUANTOS).replace("@cuantos@", CUANTOS.lower())
          .replace("@ACCIONES@", ACCIONES).replace("@ESTADOS@", ESTADOS)
          .replace("@SINCOSTE@", SINCOSTE))
assert "@CUANTOS@" not in CUERPO and "@cuantos@" not in CUERPO, "queda alguna marca"

(RAIZ / "inicio.html").write_text(sello(cabecera + "\n" + CUERPO + "\n</body>\n</html>\n"), encoding="utf-8")
print("inicio.html ·", (RAIZ / "inicio.html").stat().st_size // 1024, "KB")
