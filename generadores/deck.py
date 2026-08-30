#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ensambla deck.html, la presentación de Junta en 16:9.

Conserva las quince diapositivas de la versión anterior —renumeradas— y les
añade la capa del plan y la Parte VI. Cada diapositiva lleva su nota de ponente
con el minuto objetivo y la pregunta difícil; doce están marcadas como ruta
corta. El sistema de diseño y las figuras vienen de fuentes/.
"""
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

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


SP = RAIZ / "fuentes"

manual = (RAIZ / "manual.html").read_text(encoding="utf-8")
tokens = re.search(r"(:root\{.*?\n\})", manual, re.S).group(1)
fuentes = re.search(r'(<link rel="preconnect".*?display=swap">)', manual, re.S).group(1)

figuras = "\n".join((SP / n).read_text(encoding="utf-8")
                    for n in ("figuras-1-3.html", "figuras-4-6.html", "figuras-8-12.html"))


def figura(marca):
    return figuras.split("<!--%s-->" % marca)[1].split("<!--")[0].strip()


CSS = """
*{box-sizing:border-box}
html,body{height:100%}
body{
  margin:0;background:var(--paper);color:var(--ink);
  font-family:var(--f-body);font-size:clamp(14px,1.15vw,19px);line-height:1.55;
  -webkit-font-smoothing:antialiased;
}
h1,h2,h3{font-family:var(--f-display);font-weight:500;margin:0;line-height:1.08;text-wrap:balance}
p{margin:0}
.deck{position:relative;height:100vh;overflow:hidden}
.slide{
  position:absolute;inset:0;display:none;
  padding:clamp(2.4rem,4.4vw,4.6rem) clamp(2.4rem,5vw,6rem) clamp(3.6rem,6vw,5.4rem);
  flex-direction:column;justify-content:center;gap:clamp(1rem,1.6vw,1.8rem);
}
.slide.is-on{display:flex;animation:entra .34s cubic-bezier(.2,.7,.3,1) both}
@keyframes entra{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
@media(prefers-reduced-motion:reduce){.slide.is-on{animation:none}}
.eyebrow{
  font-family:var(--f-mono);font-size:.7rem;letter-spacing:.18em;text-transform:uppercase;
  color:var(--muted);margin:0;
}
.slide h2{font-size:clamp(1.9rem,3.5vw,3.2rem);letter-spacing:-.02em;max-width:22ch}
.slide h2 em{font-style:italic;color:var(--accent-ink)}
.lede{font-size:clamp(1rem,1.4vw,1.35rem);color:var(--ink-2);max-width:58ch}
.slide--portada h1{font-size:clamp(2.6rem,6vw,5.2rem);letter-spacing:-.03em;font-variation-settings:"opsz" 144}
.slide--portada h1 em{font-style:italic;color:var(--accent-ink)}
.slide--cierre{background:var(--surface)}
.cols{display:grid;gap:clamp(1rem,2vw,2.4rem);grid-template-columns:repeat(auto-fit,minmax(min(240px,100%),1fr))}
.cols>*{min-width:0}
.tile{background:var(--surface);border:1px solid var(--line);padding:clamp(.9rem,1.4vw,1.4rem)}
.tile dt,.tile .k{font-family:var(--f-mono);font-size:.66rem;letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}
.tile .v{font-family:var(--f-display);font-size:clamp(1.6rem,3vw,2.6rem);line-height:1;margin:.3rem 0 .35rem}
.tile p{font-size:.86rem;color:var(--ink-2)}
ul.bul{list-style:none;margin:0;padding:0;display:grid;gap:.75rem;max-width:62ch}
ul.bul li{position:relative;padding-left:1.4rem;color:var(--ink-2)}
ul.bul li::before{content:"";position:absolute;left:0;top:.62em;width:9px;height:1px;background:var(--accent)}
ul.bul li b,ul.bul li strong{color:var(--ink)}
table{border-collapse:collapse;width:100%;font-size:clamp(.76rem,.95vw,.95rem)}
th,td{text-align:left;padding:.42rem .7rem;border-bottom:1px solid var(--line-soft);vertical-align:top}
thead th{font-family:var(--f-mono);font-size:.62rem;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);white-space:nowrap}
td.c{font-family:var(--f-mono);white-space:nowrap;color:var(--accent-ink)}
.quote{border-left:3px solid var(--accent);padding:.4rem 0 .4rem 1.2rem;max-width:52ch}
.quote p{font-family:var(--f-display);font-style:italic;font-size:clamp(1.2rem,2vw,1.8rem);line-height:1.3}
.fig{margin:0;background:var(--surface);border:1px solid var(--line);padding:clamp(.8rem,1.4vw,1.4rem);overflow-x:auto;min-height:0}
.fig svg{width:100%;height:auto;max-height:min(46vh,440px);display:block}
.fig figcaption{margin-top:.7rem;font-size:.78rem;color:var(--muted);max-width:80ch}
.sem{font-family:var(--f-mono);font-size:.66rem;letter-spacing:.08em;text-transform:uppercase;padding:.1rem .4rem;border-radius:3px;white-space:nowrap}
.sem--rojo{background:rgba(168,27,27,.12);color:#8E1B1B}
.sem--ambar{background:rgba(168,99,27,.14);color:#8A5015}
.sem--verde{background:rgba(14,124,116,.12);color:var(--accent-ink)}
/* --- diapositiva de declaración: la que se recuerda al salir --- */
.slide--stmt{background:var(--ink);color:var(--surface);justify-content:center}
.slide--stmt .eyebrow{color:rgba(247,248,245,.5)}
.slide--stmt h2{
  font-size:clamp(2rem,4.4vw,4rem);max-width:20ch;color:var(--surface);
  font-style:italic;font-weight:400;letter-spacing:-.03em;line-height:1.06;
}
.slide--stmt h2 em{font-style:normal;color:#7FD3C9}
.slide--stmt .lede{color:rgba(247,248,245,.72);max-width:52ch}
.slide--stmt ul.bul li{color:rgba(247,248,245,.88)}
.slide--stmt ul.bul li b,.slide--stmt ul.bul li strong{color:var(--surface)}
.slide--stmt ul.bul li::before{background:#7FD3C9}
.slide--stmt table{color:rgba(247,248,245,.88)}
.slide--stmt th,.slide--stmt td{border-color:rgba(247,248,245,.18)}
.slide--stmt thead th{color:rgba(247,248,245,.5)}
.slide--stmt td.c{color:#7FD3C9}

/* --- separador de parte --- */
.slide--div{background:var(--surface);justify-content:center}
.slide--div .rom{
  font-family:var(--f-display);font-size:clamp(4rem,11vw,9rem);line-height:.82;
  letter-spacing:-.05em;color:var(--accent-ink);font-variation-settings:"opsz" 144;
}
.slide--div h2{font-size:clamp(1.7rem,3.2vw,2.9rem);max-width:24ch}
.slide--div .lede{max-width:60ch}

/* --- horizontes y escalones dentro de la presentación --- */
.hz{display:grid;gap:clamp(.7rem,1.4vw,1.4rem);grid-template-columns:repeat(auto-fit,minmax(min(230px,100%),1fr))}
.hz>div{background:var(--surface);border:1px solid var(--line);padding:clamp(.85rem,1.3vw,1.3rem);min-width:0}
.hz b{font-family:var(--f-display);font-size:clamp(1.4rem,2.4vw,2rem);line-height:1;display:block}
.hz span{display:block;margin:.25rem 0 .6rem;font-family:var(--f-mono);font-size:.62rem;letter-spacing:.13em;text-transform:uppercase;color:var(--muted)}
.hz ul{list-style:none;margin:0;padding:0;display:grid;gap:.4rem}
.hz li{font-size:.84rem;color:var(--ink-2);padding-left:.9rem;position:relative}
.hz li::before{content:"";position:absolute;left:0;top:.6em;width:4px;height:4px;background:currentColor;opacity:.5}
.hz--a b{color:#0E8F84}.hz--b b{color:#A8631B}.hz--c b{color:#7A4FA3}

/* --- pasos numerados --- */
ol.pasos{list-style:none;margin:0;padding:0;display:grid;gap:.55rem;counter-reset:p}
ol.pasos li{
  counter-increment:p;position:relative;padding-left:2.6rem;color:var(--ink-2);
  border-top:1px solid var(--line-soft);padding-top:.55rem;
}
ol.pasos li::before{
  content:counter(p);position:absolute;left:0;top:.5rem;
  font-family:var(--f-mono);font-size:.72rem;color:var(--accent-ink);
  border:1px solid var(--line);width:1.7rem;height:1.7rem;
  display:grid;place-items:center;border-radius:999px;
}
ol.pasos li b{color:var(--ink)}
.barra{position:fixed;left:0;right:0;bottom:0;height:3px;background:var(--line-soft)}
.barra i{display:block;height:100%;background:var(--accent);transition:width .3s ease}
.hud{
  position:fixed;left:0;right:0;bottom:14px;display:flex;align-items:center;gap:1rem;
  padding:0 clamp(1.2rem,3vw,2.4rem);font-family:var(--f-mono);font-size:.7rem;color:var(--muted);
}
.hud__marca{margin-right:auto;letter-spacing:.1em;text-transform:uppercase}
.hud button{
  font:inherit;background:transparent;border:1px solid var(--line);color:var(--ink-2);
  padding:.28rem .6rem;border-radius:999px;cursor:pointer;
}
.hud button:hover{border-color:var(--accent);color:var(--accent-ink)}
.hud__n{font-variant-numeric:tabular-nums}
/* --- guion del ponente: solo visible en modo ponente (tecla N) --- */
.nota{display:none}
body.modo-ponente .nota{
  display:grid;gap:1rem;position:fixed;left:0;right:0;bottom:0;z-index:40;
  background:var(--ink);color:rgba(247,248,245,.9);
  padding:1rem clamp(1.2rem,3vw,2.4rem) 2.6rem;
  border-top:2px solid #7FD3C9;max-height:42vh;overflow:auto;
  font-size:clamp(13px,1vw,15px);line-height:1.5;
}
@media(min-width:900px){body.modo-ponente .nota{grid-template-columns:minmax(0,1.35fr) minmax(0,1fr);gap:2.4rem}}
body.modo-ponente .nota b{
  display:block;font-family:var(--f-mono);font-size:.64rem;letter-spacing:.14em;
  text-transform:uppercase;color:#7FD3C9;margin-bottom:.35rem;font-weight:500;
}
body.modo-ponente .nota__dura{border-left:2px solid rgba(247,248,245,.28);padding-left:1rem}
body.modo-ponente .nota__q{
  font-family:var(--f-display);font-style:italic;font-size:1.05rem;
  color:var(--surface);margin-bottom:.4rem;
}
body.modo-ponente .slide{padding-bottom:clamp(12rem,44vh,26rem)}
/* con el guion abierto queda menos alto: la figura se encoge en lugar de recortarse */
body.modo-ponente .fig svg{max-height:min(30vh,290px)}
body.modo-ponente .slide h2{font-size:clamp(1.5rem,2.6vw,2.3rem)}
body.modo-ponente .slide{gap:clamp(.7rem,1.1vw,1.2rem)}
body.modo-ponente .hud{color:rgba(247,248,245,.6);z-index:41}
body.modo-ponente .hud button{border-color:rgba(247,248,245,.28);color:rgba(247,248,245,.82)}
body.modo-ponente .barra{z-index:41;background:rgba(247,248,245,.16)}
body.modo-ponente .barra i{background:#7FD3C9}
.hud__modo{
  font-family:var(--f-mono);font-size:.62rem;letter-spacing:.12em;text-transform:uppercase;
  color:var(--accent-ink);border:1px solid var(--accent);border-radius:999px;
  padding:.16rem .5rem;
}
.hud__modo[hidden]{display:none}
.hud__min{font-variant-numeric:tabular-nums;opacity:.75}
/* la barra de estado se aclara sobre las diapositivas de tinta */
body:has(.slide--stmt.is-on) .hud{color:rgba(247,248,245,.6)}
body:has(.slide--stmt.is-on) .hud button{border-color:rgba(247,248,245,.28);color:rgba(247,248,245,.82)}
body:has(.slide--stmt.is-on) .hud button:hover{border-color:#7FD3C9;color:#7FD3C9}
body:has(.slide--stmt.is-on) .barra{background:rgba(247,248,245,.16)}
body:has(.slide--stmt.is-on) .barra i{background:#7FD3C9}
:focus-visible{outline:2px solid var(--accent);outline-offset:3px}
@media print{
  @page{size:297mm 167mm;margin:0}
  @page guion{size:297mm 210mm;margin:0}
  html,body{height:auto;background:#fff}
  .deck{height:auto;overflow:visible}
  .slide{position:static;display:flex!important;height:167mm;break-after:page;animation:none;padding:16mm 18mm}
  .hud,.barra{display:none}
  .tile,.fig{background:#fff}
  .slide--stmt{background:#fff;color:#000}
  .slide--stmt h2,.slide--stmt .lede,.slide--stmt ul.bul li{color:#000}
  .slide--stmt ul.bul li::before{background:#0A5C56}
  .slide--stmt h2 em{color:#0A5C56}
  .slide--stmt .eyebrow{color:#555}
  .slide--div{background:#fff}
  body.modo-ponente .nota{
    display:block;position:static;background:#fff;color:#000;max-height:none;
    border-top:1pt solid #000;padding:6pt 0 0;margin-top:8pt;font-size:8.5pt;
  }
  body.modo-ponente .nota b{color:#0A5C56}
  body.modo-ponente .nota__q{color:#000}
  body.modo-ponente .nota__dura{border-color:#BBB;margin-top:5pt}
  /* el guion impreso no es una proyección: usa hoja A4 apaisada, más alta,
     y reparte la nota en dos columnas para que quepa entera */
  body.modo-ponente .slide{
    page:guion;height:198mm;padding:11mm 15mm;justify-content:flex-start;overflow:hidden;
    gap:4mm;font-size:9pt;
  }
  body.modo-ponente .slide h2{font-size:19pt;max-width:34ch}
  body.modo-ponente .slide--stmt h2{font-size:21pt}
  body.modo-ponente .lede{font-size:9pt;max-width:none}
  body.modo-ponente table{font-size:7.4pt}
  body.modo-ponente th,body.modo-ponente td{padding:.28rem .5rem}
  body.modo-ponente ul.bul{gap:.35rem;max-width:none}
  body.modo-ponente ul.bul li,body.modo-ponente ol.pasos li,
  body.modo-ponente .hz li,body.modo-ponente .tile p{font-size:8.2pt}
  body.modo-ponente .tile .v{font-size:15pt}
  body.modo-ponente .fig figcaption{font-size:7.4pt}
  body.modo-ponente .fig svg{max-height:74mm}
  body.modo-ponente .nota{display:grid;grid-template-columns:1.3fr 1fr;gap:8mm;
    margin-top:auto;padding-top:5mm;font-size:8.2pt;break-inside:avoid}
  body.modo-ponente .nota__dura{border-left:1pt solid #BBB;padding-left:5mm;margin-top:0}
}
"""

JS = """
(function(){
  "use strict";
  var raiz = document.querySelector(".deck-raiz");
  if(!raiz) return;
  function pieza(nombre){ return raiz.querySelector('[data-deck="' + nombre + '"]'); }
  function visible(){ return !raiz.closest("[hidden]") && raiz.offsetParent !== null; }
  var todas = Array.prototype.slice.call(raiz.querySelectorAll(".slide"));
  var esenciales = todas.filter(function(s){ return s.hasAttribute("data-esencial"); });
  var vista = todas, actual = 0, corta = false;

  var num = pieza("n");
  var barra = pieza("progreso");
  var minuto = pieza("minuto");
  var rotuloRuta = pieza("rotulo-ruta");
  var rotuloPonente = pieza("rotulo-ponente");
  var botonRuta = pieza("ruta");
  var botonPonente = pieza("ponente");

  function ir(i){
    actual = Math.max(0, Math.min(vista.length - 1, i));
    todas.forEach(function(s){ s.classList.remove("is-on"); });
    var activa = vista[actual];
    activa.classList.add("is-on");
    num.textContent = (actual + 1) + " / " + vista.length;
    barra.style.width = ((actual + 1) / vista.length * 100) + "%";
    minuto.textContent = activa.getAttribute("data-min") || "";
    try { history.replaceState(null, "", "#" + (actual + 1)); } catch(e){}
  }

  function ruta(){
    if(!esenciales.length) return;
    var actualEl = vista[actual];
    corta = !corta;
    vista = corta ? esenciales : todas;
    rotuloRuta.hidden = !corta;
    botonRuta.setAttribute("aria-pressed", corta ? "true" : "false");
    // conservar el sitio: si la actual no está en la ruta, ir a la anterior que sí
    var i = vista.indexOf(actualEl);
    if(i < 0){
      i = 0;
      for(var k = 0; k < vista.length; k++){
        if(todas.indexOf(vista[k]) <= todas.indexOf(actualEl)) i = k;
      }
    }
    ir(i);
  }

  function ponente(){
    var on = document.body.classList.toggle("modo-ponente");
    raiz.querySelectorAll(".nota").forEach(function(n){ n.hidden = !on; });
    rotuloPonente.hidden = !on;
    botonPonente.setAttribute("aria-pressed", on ? "true" : "false");
  }

  pieza("prev").addEventListener("click", function(){ ir(actual - 1); });
  pieza("next").addEventListener("click", function(){ ir(actual + 1); });
  botonRuta.addEventListener("click", ruta);
  botonPonente.addEventListener("click", ponente);

  document.addEventListener("keydown", function(e){
    if(e.metaKey || e.ctrlKey || e.altKey || !visible()) return;
    var foco = document.activeElement;
    if(foco && /^(INPUT|TEXTAREA|SELECT)$/.test(foco.tagName)) return;
    var k = e.key;
    if(k === "ArrowRight" || k === "PageDown" || k === " ") { e.preventDefault(); ir(actual + 1); }
    else if(k === "ArrowLeft" || k === "PageUp") { e.preventDefault(); ir(actual - 1); }
    else if(k === "Home") ir(0);
    else if(k === "End") ir(vista.length - 1);
    else if(k === "e" || k === "E") ruta();
    else if(k === "n" || k === "N") ponente();
  });

  var inicio = parseInt((location.hash || "").slice(1), 10);
  ir(isNaN(inicio) ? 0 : inicio - 1);
})();
"""

DIAPOSITIVAS = []
A = DIAPOSITIVAS.append

A('''<section class="slide slide--portada">
  <p class="eyebrow">Junta Directiva · @FECHA@ · Uso interno y confidencial</p>
  <h1>Memoria de<br><em>Dirección</em></h1>
  <p class="lede">Centro de Excelencia Implantológica Giraldo. Estado del proyecto, línea base, riesgos, hoja de ruta y las ocho decisiones que se someten a aprobación.</p>
</section>''')

A('''<section class="slide">
  <p class="eyebrow">02 · La apuesta</p>
  <h2>Un centro que resuelve lo que otros rechazan y no termina la relación cuando cobra</h2>
  <div class="quote"><p>«Le devolvemos su sonrisa completa, en el menor tiempo posible, y le cuidamos para siempre.»</p></div>
  <p class="lede">La primera mitad es el resultado: ningún tratamiento se deja a medias. La segunda es la relación, y tiene instrumento propio: el programa de cuidado anual. La ventaja competitiva no es el equipamiento —lo reivindican todos— sino la ejecución sistemática.</p>
</section>''')

A('''<section class="slide">
  <p class="eyebrow">03 · Qué se ha construido</p>
  <h2>Un sistema operativo, no un plan</h2>
  <div class="cols">
    <div class="tile"><p class="k">Recorrido del paciente</p><p class="v">14</p><p>Fases, de la primera llamada al mantenimiento</p></div>
    <div class="tile"><p class="k">Puestos normalizados</p><p class="v">6</p><p>Con límites, checklists, derivaciones y reporte</p></div>
    <div class="tile"><p class="k">Puntos de verificación</p><p class="v">322</p><p>Físicos, documentales, de sistemas y de proceso</p></div>
    <div class="tile"><p class="k">Documentos vigentes</p><p class="v">17</p><p>Tres troncales y catorce de apoyo</p></div>
  </div>
  <p class="lede">Normativa interna con criterios de salida, registros obligatorios e indicador por fase. Escrita para ejecutarse y para auditarse.</p>
</section>''')

A('''<section class="slide">
  <p class="eyebrow">03 · Los tres documentos troncales</p>
  <h2>Qué garantiza tenerlo por escrito</h2>
  <ul class="bul">
    <li><b>Manual Maestro de Operaciones</b> — la norma: catorce fases, manuales de puesto, responsabilidades, indicadores e incentivos</li>
    <li><b>Protocolo de Primera Visita</b> — el detalle minuto a minuto de la visita que decide la conversión</li>
    <li><b>Otros documentos del sistema</b> — verificación, auditoría, 100 días, innovación, marca, posicionamiento y programa de cuidado</li>
  </ul>
  <p class="lede">Que la calidad no dependa de quién esté de turno; que un profesional nuevo sea productivo en semanas; que una inspección encuentre trazabilidad y no explicaciones; y que la Dirección pueda delegar sin perder control. En términos de Junta: la diferencia entre un negocio dependiente de personas y un negocio con activos transferibles.</p>
</section>''')

A('''<section class="slide">
  <p class="eyebrow">02 · Dónde está la oportunidad</p>
  <h2>Tres segmentos que casi nadie atiende</h2>
  <table>
    <thead><tr><th>Segmento</th><th>Por qué está desatendido</th><th>Barrera de entrada</th></tr></thead>
    <tbody>
      <tr><td><b>Casos de alta complejidad</b></td><td>Es más cómodo decir que no</td><td>Criterio y sistema, no equipamiento</td></tr>
      <tr><td><b>Ansiedad dental severa</b></td><td>Casi nadie lo comunica explícitamente</td><td>Circuito de sedación con habilitación</td></tr>
      <tr><td><b>Mantenimiento implantológico</b></td><td>No produce caja inmediata</td><td>Constancia y sistema; decisivo a largo plazo</td></tr>
    </tbody>
  </table>
  <p class="lede">Ninguno compra precio: los tres compran solución. Es el terreno donde la competencia en tarifa no llega.</p>
</section>''')

A('''<section class="slide">
  <p class="eyebrow">04 · Dónde estamos</p>
  <h2>Los cinco números que <em>aún no tenemos</em></h2>
  <ul class="bul">
    <li><b>Costes fijos mensuales</b> — día 15</li>
    <li><b>Punto de equilibrio mensual</b> — día 15</li>
    <li><b>Primeras visitas necesarias al día</b> — día 30</li>
    <li><b>Producto pendiente heredado</b> — día 15</li>
    <li><b>Meses de colchón de tesorería</b> — día 21</li>
  </ul>
  <p class="lede">Sin estas cinco cifras, cualquier objetivo comercial es una opinión. Esta memoria no contiene ni un solo dato real de explotación: donde hace falta un orden de magnitud, se usa un supuesto de trabajo declarado.</p>
</section>''')

A('''<section class="slide">
  <p class="eyebrow">05 · Riesgos</p>
  <h2>Cinco riesgos críticos, con dueño</h2>
  <table>
    <thead><tr><th>#</th><th>Riesgo</th><th>Mitigación</th><th>Propietario</th></tr></thead>
    <tbody>
      <tr><td class="c">R1</td><td>Cobertura aseguradora insuficiente para tratamientos previos</td><td>Verificación documental antes de abrir</td><td>Gerencia</td></tr>
      <tr><td class="c">R2</td><td>Producto pendiente heredado sin cuantificar</td><td>Inventario en los tres primeros días</td><td>Dirección</td></tr>
      <tr><td class="c">R3</td><td>Pérdida de un profesional clave</td><td>Entrevistas tempranas y formación cruzada</td><td>Gerencia</td></tr>
      <tr><td class="c">R4</td><td>Incumplimiento regulatorio latente</td><td>Auditoría de las once verificaciones</td><td>Gerencia</td></tr>
      <tr><td class="c">R5</td><td>Deterioro de la percepción del paciente</td><td>Contacto proactivo y escalado único</td><td>Dirección</td></tr>
    </tbody>
  </table>
  <p class="lede"><b>La única regla que detiene la clínica:</b> sin verificación positiva de la cobertura aseguradora no se realiza actividad clínica. Es el riesgo cuyo coste no tiene techo.</p>
</section>''')

A('''<section class="slide">
  <p class="eyebrow">06 · Cuadro de mando</p>
  <h2>Diez indicadores, ninguno con serie propia todavía</h2>
  <div class="cols">
    <div class="tile"><p class="k">Integridad del sistema</p><p class="v">4</p><p>Verificaciones cerradas · bajas voluntarias · reclamaciones heredadas · documentación en el día</p></div>
    <div class="tile"><p class="k">Resultado</p><p class="v">4</p><p>Producto pendiente · conversión · mantenimiento activo · captación por recomendación</p></div>
    <div class="tile"><p class="k">Exigidos por D13 y D14</p><p class="v">2</p><p>Ofrecimiento del programa de cuidado · auditorías ejecutadas en fecha</p></div>
    <div class="tile"><p class="k">Con dato hoy</p><p class="v">0 / 10</p><p><span class="sem sem--ambar">Primera lectura este trimestre</span></p></div>
  </div>
  <p class="lede">Diez casillas vacías no son una debilidad del documento: son el diagnóstico honesto de dónde estamos. La Junta debe exigir que en la revisión trimestral las diez tengan valor y tendencia.</p>
</section>''')

A('''<section class="slide">
  <p class="eyebrow">06 · Política de precios <span class="sem sem--ambar">Modelo</span></p>
  <h2>Lo que cuesta de verdad un descuento</h2>
  <figure class="fig">%s
    <figcaption>Los costes del caso no bajan cuando baja el precio: el descuento sale íntegramente del beneficio. Un 10 %% de descuento cuesta el 25 %% del beneficio del caso; compensarlo exige vender un 33 %% más. Margen del 40 %% como supuesto de trabajo.</figcaption>
  </figure>
</section>''' % figura("F1"))

A('''<section class="slide">
  <p class="eyebrow">04 · La palanca más barata <span class="sem sem--ambar">Modelo</span></p>
  <h2>Cada diez puntos de conversión valen una visita diaria</h2>
  <figure class="fig">%s
    <figcaption>Primeras visitas necesarias al día para alcanzar el equilibrio, según la tasa de conversión. Supuestos: 60.000 € de punto de equilibrio mensual, 1.800 € de ticket medio aceptado y 21 días laborables. Mejorar la conversión no requiere captar a nadie más.</figcaption>
  </figure>
</section>''' % figura("F2"))

A('''<section class="slide">
  <p class="eyebrow">06 · Relación frente a transacción <span class="sem sem--ambar">Modelo</span></p>
  <h2>La relación vale del orden del doble</h2>
  <figure class="fig">%s
    <figcaption>Valor estimado de un paciente a cinco años. El programa de cuidado no se justifica por su cuota, que es marginal, sino por lo que arrastra: revisiones que detectan a tiempo, tratamientos que se hacen cuando aún son sencillos y familiares que entran por la puerta.</figcaption>
  </figure>
</section>''' % figura("F3"))

A('''<section class="slide">
  <p class="eyebrow">07 · Palancas de valor</p>
  <h2>Por dónde se crece, <em>y en qué orden</em></h2>
  <table>
    <thead><tr><th>Orden</th><th>Palanca</th><th>Coste de activación</th><th>Horizonte</th></tr></thead>
    <tbody>
      <tr><td class="c">1</td><td>Producto pendiente: caja ya cobrada que se convierte en producción</td><td>Solo gestión</td><td>Semanas</td></tr>
      <tr><td class="c">2</td><td>Conversión de la primera visita</td><td>Formación y disciplina</td><td>1-2 trimestres</td></tr>
      <tr><td class="c">3</td><td>Cartera propia dormida</td><td>Bajo</td><td>1 trimestre</td></tr>
      <tr><td class="c">4</td><td>Programa de cuidado y mantenimiento</td><td>Bajo, con encaje legal previo</td><td>2-4 trimestres</td></tr>
      <tr><td class="c">5</td><td>Captación externa</td><td>Medio-alto</td><td>3-6 trimestres</td></tr>
    </tbody>
  </table>
  <p class="lede"><b>Sostener → recuperar → fidelizar → captar.</b> Invertir en captación con la cartera propia desatendida es la asignación de recursos menos eficiente posible.</p>
</section>''')

A('''<section class="slide">
  <p class="eyebrow">08 · Hoja de ruta</p>
  <h2>Tres horizontes, tres puertas</h2>
  <div class="cols">
    <div class="tile"><p class="k">Horizonte 1 · 100 días</p><p class="v">Estabilizar</p><p>Riesgo neutralizado, equipo retenido, continuidad asegurada, línea base establecida</p></div>
    <div class="tile"><p class="k">Horizonte 2 · 12 meses</p><p class="v">Consolidar</p><p>Protocolo implantado, producto pendiente residual, marca reposicionada, indicadores con serie propia</p></div>
    <div class="tile"><p class="k">Horizonte 3 · 36 meses</p><p class="v">Liderar</p><p>Referencia en implantología compleja, captación mayoritariamente por recomendación</p></div>
  </div>
  <p class="lede">El programa no avanza por calendario, sino por criterios de salida verificados en los días 30, 60 y 100. Ninguna fase se adelanta.</p>
</section>''')

A('''<section class="slide">
  <p class="eyebrow">09 · Lo que se pide hoy</p>
  <h2>Ocho decisiones</h2>
  <table>
    <thead><tr><th>Cód.</th><th>Materia</th><th>Plazo</th></tr></thead>
    <tbody>
      <tr><td class="c">D1</td><td>Política de precios y tabla de descuentos</td><td><span class="sem sem--rojo">Inmediato</span></td></tr>
      <tr><td class="c">D2</td><td>Garantías publicadas por tipo de tratamiento</td><td><span class="sem sem--rojo">Inmediato</span></td></tr>
      <tr><td class="c">D5</td><td>Programa de cuidado: precio, catálogo y validación jurídica</td><td><span class="sem sem--rojo">Inmediato</span></td></tr>
      <tr><td class="c">D8</td><td>Responsables funcionales y Comité de Transición</td><td><span class="sem sem--rojo">Inmediato</span></td></tr>
      <tr><td class="c">D3</td><td>Arquitectura de marca y verificación legal del naming</td><td><span class="sem sem--ambar">Trimestre</span></td></tr>
      <tr><td class="c">D4</td><td>Presupuesto anual de captación y modelo de ejecución</td><td><span class="sem sem--ambar">Trimestre</span></td></tr>
      <tr><td class="c">D6</td><td>Línea de sedación consciente</td><td><span class="sem sem--ambar">Trimestre</span></td></tr>
      <tr><td class="c">D7</td><td>Marco de inversión en flujo digital</td><td><span class="sem sem--ambar">2.º trimestre</span></td></tr>
    </tbody>
  </table>
</section>''')

A('''<section class="slide slide--cierre">
  <p class="eyebrow">Cierre</p>
  <h2>Qué mide el éxito de este año</h2>
  <ul class="bul">
    <li><b>Que el equipo permanezca.</b> El conocimiento operativo reside en las personas y su reposición exige plazos que ningún plan comprime</li>
    <li><b>Que los pacientes heredados no perciban discontinuidad.</b> Son la base de ingresos inmediata y el primer canal de prescripción</li>
    <li><b>Que la organización acepte un estándar superior al preexistente.</b> La ventana para establecerlo se cierra en el primer trimestre</li>
  </ul>
  <p class="lede">Lo que se pide hoy no es respaldo genérico: es resolver las ocho decisiones y fijar la fecha de la próxima revisión.</p>
</section>''')

# --------------------------------------------------------------- capa del plan
import pathlib as _pl
import sys as _sys
_sys.path.insert(0, str(_pl.Path(__file__).parent.parent))
from renum_apartados import renumera as _renumera

ORIGINALES = [_renumera(s) for s in DIAPOSITIVAS]
# tres rótulos que la renumeración deja en el apartado equivocado
ORIGINALES[8] = ORIGINALES[8].replace("apartado 13 · Política de precios", "apartado 14 · Política de precios")
ORIGINALES[9] = ORIGINALES[9].replace("apartado 7 · La palanca más barata", "apartado 8 · La palanca más barata")
ORIGINALES[10] = ORIGINALES[10].replace("apartado 13 · Relación frente a transacción",
                                        "apartado 9 · Relación frente a transacción")
ORIGINALES[13] = (ORIGINALES[13].replace("<h2>Ocho decisiones</h2>",
                                         "<h2>Las ocho de la operación</h2>")
                  .replace("apartado 17 · Lo que se pide hoy", "apartado 17 · Lo que se pide hoy · 1 de 2"))
ORIGINALES[14] = ORIGINALES[14].replace("resolver las ocho decisiones",
                                        "resolver las quince decisiones")

DIAPOSITIVAS = []
A = DIAPOSITIVAS.append


def parte(numero, rotulo, titulo, lede):
    A('''<section class="slide slide--div">
  <p class="eyebrow">Parte %s · %s</p>
  <p class="rom">%s</p>
  <h2>%s</h2>
  <p class="lede">%s</p>
</section>''' % (numero, rotulo, numero, titulo, lede))


# 1 · portada de declaración
A('''<section class="slide slide--stmt">
  <p class="eyebrow">Junta Directiva · @FECHA@ · Uso interno y confidencial</p>
  <h2>No medias sonrisas.<br><em>Ni medias decisiones.</em></h2>
  <p class="lede">Centro de Excelencia Implantológica Giraldo · Plan de Dirección v@VERSION@ · Seis partes, veintitrés apartados y quince decisiones que solo puede tomar este órgano.</p>
</section>''')

# 2 · la pregunta de la sesión
A('''<section class="slide">
  <p class="eyebrow">El planteamiento</p>
  <h2>Un plan, no <em>un informe</em></h2>
  <div class="cols">
    <div class="tile"><p class="k">Pregunta 1</p><p class="v">¿Qué?</p><p>Qué creemos que es cierto sobre este mercado y por qué la posición que ocupamos está libre</p></div>
    <div class="tile"><p class="k">Pregunta 2</p><p class="v">¿Cuánto?</p><p>Qué vale cada palanca, en euros y con los supuestos declarados sobre la mesa</p></div>
    <div class="tile"><p class="k">Pregunta 3</p><p class="v">¿Y si no?</p><p>Bajo qué condiciones estaríamos equivocados, y qué señal lo avisaría a tiempo</p></div>
  </div>
  <p class="lede">Un informe cuenta lo que ha pasado. Un plan afirma, apuesta y se expone a ser refutada. Cada cifra de esta presentación lleva marcada su naturaleza: <b>hecho</b>, <b>modelo</b> o <b>pendiente</b>.</p>
</section>''')

parte("I", "La posición", "Dónde estamos parados y <em>por qué ahí</em>",
      "La apuesta del proyecto, los segmentos desatendidos, el mapa competitivo de Vigo y el foso: qué tendría que hacer un competidor para quitarnos el sitio y cuánto tardaría.")

A(ORIGINALES[1])   # apartado 2 · la apuesta
A(ORIGINALES[4])   # apartado 2 · tres segmentos desatendidos

# mapa competitivo
A('''<section class="slide">
  <p class="eyebrow">03 · El mapa competitivo</p>
  <h2>Cuatro formas de vender implantes en Vigo, y la que dejamos libre</h2>
  <table>
    <thead><tr><th>Posición</th><th>Cómo compite</th><th>Dónde se rompe</th></tr></thead>
    <tbody>
      <tr><td class="c">A</td><td><b>Cadena de precio</b> — captación masiva y financiación</td><td>El profesional rota: en la segunda intervención el paciente no encuentra a quien le operó</td></tr>
      <tr><td class="c">B</td><td><b>Generalista con implantes</b> — vínculo personal, agenda mixta</td><td>Casuística baja: su límite no es la voluntad, es el número de casos al año</td></tr>
      <tr><td class="c">C</td><td><b>Especialista aislado</b> — excelencia técnica real</td><td>No hay sistema debajo: su reputación no es transferible ni vendible</td></tr>
      <tr><td class="c">D</td><td><b>La nuestra</b> — casuística de especialista, estándar verificable y seguimiento contratado</td><td>Solo se rompe por abandono propio</td></tr>
    </tbody>
  </table>
  <p class="lede">El mercado no se segmenta por precio, sino por <b>quién asume el riesgo del resultado</b>. A, B y C compiten por vender el acto; nosotros vendemos que alguien siga respondiendo cuando el acto ya se cobró. <span class="sem sem--ambar">Modelo</span></p>
</section>''')

# el foso
A('''<section class="slide">
  <p class="eyebrow">04 · El foso</p>
  <h2>Lo que un competidor <em>no puede comprar</em></h2>
  <table>
    <thead><tr><th>Activo</th><th>¿Se compra?</th><th>Réplica</th></tr></thead>
    <tbody>
      <tr><td>Equipamiento: CBCT, escáner, cirugía guiada</td><td>Sí, con una llamada</td><td class="c">2-3 meses</td></tr>
      <tr><td>Instalaciones y ubicación</td><td>Sí</td><td class="c">6-12 meses</td></tr>
      <tr><td>Un cirujano de prestigio</td><td>Sí, fichándolo</td><td class="c">3-9 meses</td></tr>
      <tr><td><b>Protocolo escrito y verificable</b></td><td>No: se escribe</td><td class="c">18-36 meses</td></tr>
      <tr><td><b>Equipo que lo ejecuta sin supervisión</b></td><td>No</td><td class="c">24-48 meses</td></tr>
      <tr><td><b>Base de pacientes en seguimiento contratado</b></td><td>No</td><td class="c">36-60 meses</td></tr>
      <tr><td><b>Serie clínica propia a cinco años</b></td><td>No</td><td class="c">60 meses+</td></tr>
    </tbody>
  </table>
  <p class="lede">Los tres primeros cuestan dinero. Los cuatro últimos dan ventaja. Estamos invirtiendo, deliberadamente, en la mitad de abajo. <span class="sem sem--ambar">Modelo</span></p>
</section>''')

A('''<section class="slide slide--stmt">
  <p class="eyebrow">La consecuencia presupuestaria</p>
  <h2>Un euro en equipamiento nos iguala con cualquiera.<br><em>Un euro en sistema nos separa durante años.</em></h2>
  <p class="lede">Por eso el gasto en formación, verificación y programa de seguimiento no es estructura ni coste indirecto: es la única partida del presupuesto que compra tiempo de ventaja frente a un competidor con más capital. Y es siempre la primera candidata al recorte.</p>
</section>''')

parte("II", "El sistema", "El activo se llama <em>sistema operativo</em>, no clínica",
      "Una clínica es un local con pacientes. Un sistema operativo es un conjunto de decisiones ya tomadas que hacen que el resultado no dependa de quién esté ese martes. Lo primero se vende al peso; lo segundo, por múltiplo.")

A(ORIGINALES[2])   # apartado 5 · un sistema operativo, no un plan
A(ORIGINALES[3])   # apartado 5 · los tres documentos troncales

# cartera de innovación
A('''<section class="slide">
  <p class="eyebrow">06 · Cartera de innovación</p>
  <h2>Tres horizontes, <em>tres criterios distintos</em></h2>
  <div class="hz">
    <div class="hz--a"><b>H1</b><span>0-12 meses · Explotar · ~70 %</span>
      <ul><li>Cirugía guiada como estándar</li><li>Flujo digital completo en prótesis</li><li>Recordatorio automatizado de revisiones</li><li>Panel semanal de indicadores</li><li>Programa de cuidado en el 100 % de los cierres</li></ul></div>
    <div class="hz--b"><b>H2</b><span>12-36 meses · Construir · ~20 %</span>
      <ul><li>Unidad de casos complejos</li><li>Programa formal de derivación</li><li>Registro propio de resultados a 3 y 5 años</li><li>Segunda unidad preparada</li><li>Itinerario formativo por puesto</li></ul></div>
    <div class="hz--c"><b>H3</b><span>36 meses+ · Explorar · ~10 %</span>
      <ul><li>Docencia y publicación de casuística</li><li>Diagnóstico asistido sobre serie propia</li><li>Licencia del sistema a terceros</li><li>Red de dos a cuatro unidades</li></ul></div>
  </div>
  <p class="lede">El H1 se juzga por retorno, el H2 por hitos de aprendizaje y el H3 por mantener abierta la opción a coste bajo. Confundir los criterios mata el horizonte largo sin que nadie decida matarlo. <b>Decisión D9.</b></p>
</section>''')

parte("III", "La economía", "De dónde sale el dinero y <em>qué lo destruye</em>",
      "Cuánto vale cada primera visita según cómo la trabajemos, qué le pasa a la facturación si movemos las dos únicas palancas que la gobiernan, y por qué un paciente en seguimiento vale más del doble que un paciente atendido.")

A(ORIGINALES[5])   # apartado 7 · los cinco números que aún no tenemos

A('''<section class="slide">
  <p class="eyebrow">08 · Escenarios <span class="sem sem--ambar">Modelo</span></p>
  <h2>Tres trayectorias a treinta y seis meses</h2>
  <figure class="fig">%s
    <figcaption>Base: el centro sostiene lo heredado sin cambio de sistema. Objetivo: el sistema operativo en marcha con las palancas activas. Ambición: además, segunda unidad y líneas nuevas del H2. La distancia entre base y objetivo —del orden de 380 k€ anuales en el mes 36— es lo que está en juego en esta sesión.</figcaption>
  </figure>
</section>''' % figura("F4"))

A('''<section class="slide">
  <p class="eyebrow">08 · Sensibilidad <span class="sem sem--ambar">Modelo</span></p>
  <h2>Dos variables gobiernan el resultado; <em>el resto son consecuencias</em></h2>
  <figure class="fig">%s
    <figcaption>Facturación anual con capacidad fija de cuatro primeras visitas al día. Pasar del 30 %% al 50 %% de conversión multiplica por 1,67 sin tocar el precio. Subir el ticket de 1.400 € a 2.200 € multiplica por 1,57. Hacer las dos cosas multiplica por 2,6: las palancas no se suman, se multiplican.</figcaption>
  </figure>
</section>''' % figura("F5"))

A(ORIGINALES[8])   # apartado 14 · lo que cuesta de verdad un descuento (F1)
A(ORIGINALES[9])   # apartado 8 · cada diez puntos de conversión (F2)
A(ORIGINALES[10])  # apartado 9 · la relación vale el doble (F3)

A('''<section class="slide">
  <p class="eyebrow">09 · El activo <span class="sem sem--ambar">Modelo</span></p>
  <h2>Lo que hoy se deja <em>sobre la mesa</em></h2>
  <figure class="fig">%s
    <figcaption>Valor acumulado por paciente a cinco años, con y sin programa de seguimiento. El área sombreada no se pierde por competencia: se pierde por no volver a llamar. Es también la parte del ingreso que un comprador valora con múltiplo superior, porque es previsible.</figcaption>
  </figure>
</section>''' % figura("F6"))

A('''<section class="slide">
  <p class="eyebrow">09 · Creación de valor de empresa</p>
  <h2>Por qué esto vale más que <em>la suma de sus sillones</em></h2>
  <ol class="pasos">
    <li><b>Beneficio</b> — lo que el centro gana este año. Es lo único que existe si no hay sistema.</li>
    <li><b>Beneficio sin dependencia del titular</b> — la parte que sobrevive a que el fundador se aparte. La produce el protocolo escrito, no el talento.</li>
    <li><b>Ingreso recurrente contratado</b> — cuotas y mantenimientos de la base en seguimiento. Se valora con múltiplo superior al ingreso por acto.</li>
    <li><b>Sistema replicable</b> — capacidad demostrada de abrir una segunda unidad con el mismo resultado. Convierte un centro en una plataforma.</li>
    <li><b>Serie clínica propia</b> — resultados documentados a cinco años. El único activo que no se acelera con dinero.</li>
  </ol>
  <p class="lede">Cada decisión de hoy puede leerse dos veces: por su efecto en la cuenta de este año y por el nivel de esta escalera al que lleva al centro. La segunda lectura rara vez aparece en el consejo de una clínica.</p>
</section>''')

A('''<section class="slide">
  <p class="eyebrow">10 · La apuesta de escalado</p>
  <h2>De un centro a una red: <em>el orden es innegociable</em></h2>
  <ol class="pasos">
    <li><b>Estándar escrito</b> <span class="sem sem--verde">Hecho</span> — 12 fases, 322 puntos, manual por puesto</li>
    <li><b>Estándar verificado</b> <span class="sem sem--ambar">En curso</span> — auditoría con resultado registrado, no autoevaluación</li>
    <li><b>Estándar sostenido sin el titular</b> <span class="sem sem--rojo">Pendiente</span> — un trimestre en umbral sin intervención de Dirección</li>
    <li><b>Formador formado</b> <span class="sem sem--rojo">Pendiente</span> — alguien distinto del fundador capaz de incorporar a un profesional al estándar</li>
    <li><b>Segunda unidad</b> — solo después de 3 y 4. Antes, no.</li>
  </ol>
  <p class="lede">Los centros que fracasan al escalar casi nunca fallan por falta de demanda en la segunda plaza: replicaron una operación que nunca había funcionado sin su fundador delante. <b>Decisión D11.</b></p>
</section>''')

parte("IV", "El riesgo", "Cómo fracasa esto, contado <em>antes</em> de que ocurra",
      "Un registro de riesgos enumera lo que puede salir mal. Un pre-mortem se sitúa tres años en el futuro, da por hecho el fracaso y pide explicar la causa. Cambia la pregunta, y con ella el nivel de honestidad de las respuestas.")

A(ORIGINALES[6])   # apartado 11 · cinco riesgos críticos con dueño

A('''<section class="slide">
  <p class="eyebrow">12 · Pre-mortem</p>
  <h2>Agosto de 2029: el proyecto ha fracasado. <em>¿Qué pasó?</em></h2>
  <table>
    <thead><tr><th>Causa</th><th>Señal temprana</th></tr></thead>
    <tbody>
      <tr><td><b>1 · El sistema se convirtió en papel.</b> La verificación se espació, primero por una urgencia y luego por costumbre</td><td>Una auditoría aplazada dos veces seguidas</td></tr>
      <tr><td><b>2 · Se perdió al equipo en los primeros cien días.</b> Se gestionó como un cambio de procedimientos, no de vida laboral</td><td>Una conversación de salida no mantenida a tiempo</td></tr>
      <tr><td><b>3 · Se compró crecimiento con descuento.</b> Subieron los casos, bajó el margen y el precio de referencia quedó fijado a la baja</td><td>El primer descuento fuera de la tipología cerrada</td></tr>
      <tr><td><b>4 · El programa de cuidado nunca llegó a venderse.</b> Se ofrecía «cuando encajaba»</td><td>Tasa de ofrecimiento por debajo del 90 %</td></tr>
      <tr><td><b>5 · Se abrió la segunda unidad demasiado pronto.</b> Se deterioraron las dos</td><td>«Esta oportunidad no se va a repetir» como criterio</td></tr>
      <tr><td><b>6 · Nunca se supo si iba bien.</b> Se decidió sobre la sensación del último mes</td><td>El primer comité en que se discute sin un número delante</td></tr>
    </tbody>
  </table>
  <p class="lede">Ninguna es un accidente externo: las seis son decisiones que tomamos nosotros o dejamos de tomar.</p>
</section>''')

A('''<section class="slide slide--stmt">
  <p class="eyebrow">12 · Decisión D13</p>
  <h2>Cinco disparadores que obligan a convocar <em>sin valorar la gravedad</em></h2>
  <ul class="bul">
    <li>Dos auditorías aplazadas</li>
    <li>Una salida no prevista en un puesto clave</li>
    <li>Un descuento fuera de tipología autorizado</li>
    <li>Ofrecimiento del programa de cuidado bajo el 90 % dos meses seguidos</li>
    <li>Una apertura planteada sin los pasos 3 y 4 acreditados</li>
  </ul>
  <p class="lede">Los seis modos de fallo son lentos y cómodos: nunca parecen suficientemente graves el día en que aún son baratos de corregir. Un disparador automático protege a la Junta de la propia Dirección en ese momento exacto.</p>
</section>''')

A(ORIGINALES[7])   # apartado 13 · cuadro de mando

parte("V", "La decisión", "Qué se pide hoy, y <em>qué cuesta no pedirlo</em>",
      "Las palancas de valor, el orden en que se asigna el capital, la hoja de ruta a treinta y seis meses y las quince decisiones que solo puede tomar este órgano.")

A(ORIGINALES[11])  # apartado 14 · palancas de valor

A('''<section class="slide">
  <p class="eyebrow">15 · Asignación de capital</p>
  <h2>Un orden de prelación, <em>no una lista de deseos</em></h2>
  <ol class="pasos">
    <li><b>Continuidad</b> — nóminas, obligaciones, mantenimiento y colchón de tesorería. No se discute.</li>
    <li><b>El foso</b> — formación, verificación, documentación y programa de seguimiento. Compra años de ventaja y es lo primero que se recorta en cualquier centro con prisa.</li>
    <li><b>Conversión</b> — todo lo que mejora la primera visita. Retorno más alto y más rápido que cualquier captación.</li>
    <li><b>Captación</b> — solo cuando la conversión ya está en umbral: captar más para convertir igual es pagar por desperdicio.</li>
    <li><b>Capacidad</b> — sillones, equipos, segunda unidad. Se financia con lo producido, no con deuda contra una previsión.</li>
  </ol>
  <p class="lede">Excepción legítima, una sola: cuando una prioridad inferior es condición técnica de una superior. Se documenta y se presenta en la Junta siguiente. <b>Decisión D10.</b></p>
</section>''')

A(ORIGINALES[12])  # apartado 16 · hoja de ruta
A(ORIGINALES[13])  # apartado 17 · las ocho de la operación

A('''<section class="slide">
  <p class="eyebrow">17 · Lo que se pide hoy · 2 de 2</p>
  <h2>Las siete de <em>la estrategia</em></h2>
  <table>
    <thead><tr><th>Cód.</th><th>Materia</th><th>Alternativa descartada</th><th>Plazo</th></tr></thead>
    <tbody>
      <tr><td class="c">D9</td><td>Regla de cartera de innovación 70/20/10</td><td>Decidir caso a caso: todo acaba en H1</td><td><span class="sem sem--rojo">Hoy</span></td></tr>
      <tr><td class="c">D10</td><td>Orden de prelación del capital</td><td>Presupuesto por partidas sin orden</td><td><span class="sem sem--rojo">Hoy</span></td></tr>
      <tr><td class="c">D11</td><td>Condición de apertura de segunda unidad</td><td>Decidir por oportunidad de mercado</td><td><span class="sem sem--rojo">Hoy</span></td></tr>
      <tr><td class="c">D12</td><td>Suelo anual de inversión en el foso</td><td>Tratarlo como gasto variable ajustable</td><td><span class="sem sem--rojo">Hoy</span></td></tr>
      <tr><td class="c">D13</td><td>Disparadores de Junta extraordinaria</td><td>Convocar cuando Dirección lo considere</td><td><span class="sem sem--rojo">Hoy</span></td></tr>
      <tr><td class="c">D14</td><td>Programa de cuidado obligatorio en el cierre</td><td>Dejarlo a criterio comercial</td><td><span class="sem sem--ambar">Tras D5</span></td></tr>
      <tr><td class="c">D15</td><td><b>Objetivo de facturación y horizonte: 1,2 M€ en el ejercicio tercero</b></td><td>Exigirlo en el primero: con 4 visitas al día no da la aritmética</td><td><span class="sem sem--rojo">Hoy</span></td></tr>
    </tbody>
  </table>
  <p class="lede">Las ocho anteriores resuelven la operación. Estas siete fijan las reglas con las que la Junta decidirá lo que todavía no está sobre la mesa. Es la diferencia entre gobernar y reaccionar.</p>
</section>''')

parte("VI", "La cifra", "Cómo se llega a <em>1,2 M€</em>",
      "El objetivo, descompuesto hasta el último euro: de dónde sale cada bloque, si cabe en la agenda que tenemos y qué nueve campañas lo sostienen.")

A('''<section class="slide">
  <p class="eyebrow">20 · El puente <span class="sem sem--ambar">Modelo</span></p>
  <h2>De 720 k€ a 1,2 M€, <em>bloque a bloque</em></h2>
  <figure class="fig">%s
    <figcaption>Se planifican 1.440 k€ para comprometer 1.200. Un plan que suma exactamente el objetivo es un plan que lo falla: de nueve campañas, dos no arrancarán a tiempo y una rendirá la mitad. El colchón no es holgura, es lo que hace creíble la cifra.</figcaption>
  </figure>
</section>''' % figura("F8"))

A('''<section class="slide">
  <p class="eyebrow">20 · La pregunta previa</p>
  <h2>¿Cabe 1,2 M€ en <em>la agenda que tenemos</em>?</h2>
  <div class="cols">
    <div class="tile"><p class="k">Capacidad instalada</p><p class="v">1.008</p><p>Primeras visitas al año: 4 al día × 21 días × 12 meses</p></div>
    <div class="tile"><p class="k">Valor de una visita hoy</p><p class="v">810 €</p><p>45 % × 1.800 €. Es la vara con la que se mide toda campaña</p></div>
    <div class="tile"><p class="k">Agenda que piden las nueve</p><p class="v">608</p><p>De las 1.008 que hay. La cartera cabe, y el modelo lo comprueba</p></div>
    <div class="tile"><p class="k">Si fuera solo captación</p><p class="v">5,9/día</p><p>Las visitas diarias que harían falta al ticket de hoy. La agenda da cuatro</p></div>
  </div>
  <p class="lede"><b>La agenda no admite más volumen.</b> El objetivo no se alcanza captando más pacientes: se alcanza sacando un 10 % más de los que ya vienen y construyendo 300 k€ de ingreso que hoy no existe.</p>
</section>''')

A('''<section class="slide">
  <p class="eyebrow">20 · Composición <span class="sem sem--ambar">Modelo</span></p>
  <h2>Dos tercios del salto <em>no son implantes</em></h2>
  <figure class="fig">%s
    <figcaption>El bloque de primera visita crece un 42 %%. El de seguimiento parte de cero: son 343 k€ que no existen hoy y que no dependen de ver a un solo paciente nuevo.</figcaption>
  </figure>
</section>''' % figura("F10"))

A('''<section class="slide">
  <p class="eyebrow">21 · La cartera <span class="sem sem--ambar">Modelo</span></p>
  <h2>Nueve campañas, <em>ordenadas por lo que aportan</em></h2>
  <table>
    <thead><tr><th>Cód.</th><th>Campaña</th><th>Visitas</th><th>Aporta</th><th>Retorno</th></tr></thead>
    <tbody>
      <tr><td class="c">C6</td><td><b>«La revisión que evita la cirugía»</b></td><td class="c">—</td><td class="c">172 k€</td><td class="c">34.4×</td></tr>
      <tr><td class="c">C1</td><td><b>Giraldo Te Cuida</b></td><td class="c">—</td><td class="c">171 k€</td><td class="c">28.5×</td></tr>
      <tr><td class="c">C2</td><td><b>«Su caso no es imposible»</b></td><td class="c">80</td><td class="c">71 k€</td><td class="c">5.1×</td></tr>
      <tr><td class="c">C4</td><td><b>Red de derivación</b></td><td class="c">70</td><td class="c">44 k€</td><td class="c">4.0×</td></tr>
      <tr><td class="c">C8</td><td><b>Prescripción de pacientes</b></td><td class="c">120</td><td class="c">35 k€</td><td class="c">34.8×</td></tr>
      <tr><td class="c">C5</td><td><b>«Sin miedo»</b></td><td class="c">55</td><td class="c">25 k€</td><td class="c">2.8×</td></tr>
      <tr><td class="c">C7</td><td><b>«Segunda opinión, sin compromiso»</b></td><td class="c">70</td><td class="c">20 k€</td><td class="c">4.9×</td></tr>
      <tr><td class="c">C3</td><td><b>«Volvemos a llamarle»</b></td><td class="c">130</td><td class="c">13 k€</td><td class="c">4.4×</td></tr>
      <tr><td class="c">C9</td><td><b>Presencia digital y reseñas</b></td><td class="c">83</td><td class="c">-4 k€</td><td class="c">negativo</td></tr>
    </tbody>
  </table>
  <p class="lede"><b>Las dos que más aportan son las dos más baratas, y ninguna capta pacientes:</b> trabajan sobre los que ya son del centro. La única con gasto externo relevante es la única con retorno negativo, y aun así se aprueba: sin presencia digital, cuatro de las otras no encuentran a nadie.</p>
</section>''')

A('''<section class="slide slide--stmt">
  <p class="eyebrow">21 · Lo que devuelve el modelo</p>
  <h2>D14 no es un detalle del programa de cuidado.<br><em>Es el 63 % del objetivo.</em></h2>
  <ul class="bul">
    <li><b>C6 · 172 k€ y C1 · 171 k€</b> — el 63 % de todo lo que aportan las nueve campañas</li>
    <li>Las dos dependen del mismo gesto repetido: <b>que el seguimiento se ofrezca y quede registrado en cada cierre</b></li>
    <li>El colchón del 12 % no cubre que falle ninguna de las dos: si cae una, cae el objetivo</li>
  </ul>
  <p class="lede">Un plan concentrado no es un plan malo, pero hay que saber dónde está concentrado. Aquí no está en la campaña más cara: está en la más barata y en la más fácil de dejar de hacer un martes con prisa.</p>
</section>''')

A('''<section class="slide">
  <p class="eyebrow">22 · Calendario <span class="sem sem--ambar">Modelo</span></p>
  <h2>Cuándo se enciende cada una</h2>
  <figure class="fig">%s
    <figcaption>En oscuro el arranque, en claro el sostenimiento. Nunca más de dos arranques a la vez: el equipo no sostiene más, y una campaña mal atendida hace más daño que ninguna. Enero y septiembre son los meses en que la gente decide; en julio y agosto no se enciende nada caro.</figcaption>
  </figure>
</section>''' % figura("F9"))

A('''<section class="slide slide--stmt">
  <p class="eyebrow">22 · La senda</p>
  <h2>1,2 M€ es un objetivo de <em>año tres</em></h2>
  <ul class="bul">
    <li><b>Año 1 · 890 k€</b> — C1, C3, C8 y C9. Protocolo completo y línea base levantada</li>
    <li><b>Año 2 · 1.060 k€</b> — entran C2, C6 y C7. El ticket sube por composición de casos</li>
    <li><b>Año 3 · 1.200 k€</b> — cartera completa con C4 y C5, sin abrir una segunda unidad</li>
  </ul>
  <p class="lede">Comprimirlo a dieciocho meses no se consigue acelerando campañas —maduran a su ritmo— sino ampliando capacidad, y eso anticipa la prioridad 5 del apartado 15. Es legítimo, tiene precio, y debe constar en el acta. Es la decisión <b>D15</b>.</p>
</section>''')

A('''<section class="slide">
  <p class="eyebrow">23 · Condiciones</p>
  <h2>Qué tiene que ser cierto</h2>
  <table>
    <thead><tr><th>Condición</th><th>Qué se cae si falla</th><th>Cómo se comprueba</th></tr></thead>
    <tbody>
      <tr><td><b>1 · Que el protocolo se ejecute completo</b></td><td>Con 35 % de conversión en vez de 45 %, el bloque de primera visita cae de 900 a 700 k€</td><td>Indicador 6, cohorte a 60 días</td></tr>
      <tr><td><b>2 · Que exista cartera propia que reactivar</b></td><td>Si es la mitad de lo supuesto, se van 116 k€ de los 232</td><td>Inventario, dos primeras semanas</td></tr>
      <tr><td><b>3 · Que las decisiones se resuelvan a tiempo</b></td><td>274 k€ esperan a D1, D3, D4, D5, D6 y D14</td><td>Acta de esta sesión</td></tr>
      <tr><td><b>4 · Que el ticket suba por complejidad, no por precio</b></td><td>Si sube por tarifa, la conversión cae y el efecto neto es negativo</td><td>Ticket y conversión, leídos juntos</td></tr>
      <tr><td><b>5 · Que el equipo aguante</b></td><td>La más silenciosa: no falla la demanda, falla quien tiene que atenderla</td><td>Indicador 2 y la regla de dos arranques</td></tr>
    </tbody>
  </table>
  <p class="lede">Ninguna de las cinco es una campaña. Son condiciones: si alguna no se cumple, el objetivo no baja un poco, se cae el bloque entero que dependía de ella.</p>
</section>''')

A(ORIGINALES[14])  # cierre

# ---------------------------------------------------------------- guion del ponente
# (minuto objetivo, qué decir, la pregunta difícil, la respuesta preparada)
# La ruta corta es el subconjunto marcado con ESENCIAL: doce diapositivas, 22 minutos.
ESENCIAL = {1, 7, 16, 20, 25, 34, 36, 37, 39, 40, 42, 43}

NOTAS = [
 ("0:00", "Abrir sin preámbulo, leyendo la frase. Dejar tres segundos de silencio antes de continuar: es la única diapositiva de la sesión que se sostiene sola.",
  "¿Esto es un eslogan de marketing?",
  "Es el criterio de aceptación clínico. Está escrito como punto verificable en doce fases del protocolo; el marketing vino después."),
 ("0:45", "Marcar la diferencia entre informe y plan. Insistir en que cada cifra lleva su naturaleza marcada y que no hay ni un dato propio disfrazado.",
  "¿Entonces las cifras no son reales?",
  "Los rangos son del sector y están marcados como modelo. Los datos propios llegan cuando exista la línea base: es la primera tarea de los cien días y está en el apartado 7."),
 ("2:00", "Transición. No detenerse: quince segundos.", "", ""),
 ("2:15", "La apuesta en una frase, y la segunda mitad —«le cuidamos para siempre»— como el compromiso que tiene instrumento contractual, no como una promesa amable.",
  "¿No dicen todos lo mismo?",
  "Todos dicen la primera mitad. Pida a un competidor el documento donde figure por escrito quién responde a los cinco años. Ahí se acaba el parecido."),
 ("3:15", "Tres segmentos, y el matiz que importa: ninguno compra precio. Es el terreno donde la guerra de tarifas no llega.",
  "¿Hay demanda suficiente en Vigo para tres segmentos?",
  "Es exactamente lo que no sabemos y lo reconocemos: el estudio de mercado está en la hoja de ruta del primer trimestre. Hoy es una hipótesis declarada, no un dato."),
 ("4:30", "Insistir en el eje: el mercado no se ordena por precio, sino por quién asume el riesgo del resultado. Recorrer A, B y C rápido, y detenerse en D.",
  "¿Por qué está libre la posición D si es tan buena?",
  "Porque exige casuística alta, sistema documentado y compromiso con coste asumido por adelantado, las tres a la vez. Ninguna se compra por separado y las tres juntas tardan años."),
 ("6:00", "La diapositiva del foso. Señalar físicamente la línea que separa las tres primeras filas de las cuatro últimas.",
  "¿No es más rápido y seguro invertir en tecnología?",
  "Es más rápido y por eso mismo no defiende: cualquiera con financiación nos iguala en tres meses. Lo que compramos en las cuatro filas de abajo es tiempo que el competidor no puede acortar con dinero."),
 ("7:30", "Leerla despacio. Es la frase que debe salir de la sala en la cabeza de todos.",
  "¿Cuánto dinero supone eso al año?",
  "Es la decisión D12: se pide fijar el suelo como porcentaje y concretar la cifra cuando exista línea base, en la revisión del primer trimestre."),
 ("8:15", "Transición.", "", ""),
 ("8:30", "Los cuatro números del sistema construido. No leerlos: señalarlos y decir que están disponibles para auditar hoy mismo.",
  "¿Quién ha verificado que eso existe de verdad?",
  "Está en los tres documentos que acompañan a este plan y los 322 puntos son comprobables en un recorrido físico de una mañana. La invitación está abierta."),
 ("9:30", "Los tres troncales y, sobre todo, la frase final: la diferencia entre un negocio dependiente de personas y uno con activos transferibles.",
  "¿No es demasiada documentación para una clínica?",
  "La cantidad no es el objetivo: la verificabilidad sí. Un estándar que no se puede comprobar en una lista es una intención."),
 ("10:45", "Los tres horizontes y el error que evita la regla: exigir retorno inmediato al horizonte largo lo mata sin que nadie decida matarlo. Pedir D9 aquí.",
  "¿Un 10 % en cosas que no dan dinero?",
  "Un 10 % en mantener abiertas opciones que, si el mercado cambia, no se pueden abrir después a ningún precio. Y con revisión anual del reparto real frente al aprobado."),
 ("12:00", "Transición.", "", ""),
 ("12:15", "Reconocer sin rodeos que no tenemos los cinco números. Es la diapositiva que da credibilidad a todas las demás.",
  "¿Cómo se puede dirigir sin esos datos?",
  "No se puede, y por eso el mes 1 es línea base y no objetivo comercial. La hoja de captura acompaña a este documento y las cinco cifras tienen fecha: días 15, 21 y 30."),
 ("13:45", "Los tres escenarios. Señalar la distancia entre base y objetivo en el mes 36 y decir en voz alta: esto es lo que está en juego hoy.",
  "¿Qué probabilidad tiene el escenario objetivo?",
  "No le asignamos probabilidad porque sería inventarla. Le asignamos condiciones: son las palancas del apartado 14 y las decisiones de esta sesión. Sin ellas, el escenario base."),
 ("15:30", "La matriz. Es la diapositiva más importante de la sesión: las dos palancas se multiplican, no se suman. Si hay tiempo, abrir la comprobación en directo del documento.",
  "¿Y si la conversión se queda en el 35 %?",
  "Se ve en la matriz y podemos moverlo en directo: con 35 % y ticket de 1.800 € son 544 k€. Por eso el protocolo de primera visita es el documento económico central, no un documento de calidad."),
 ("17:15", "El coste real del descuento. La cifra que hay que dejar caer: un 10 % de descuento se lleva el 25 % del beneficio del caso.",
  "¿Nunca vamos a hacer descuentos?",
  "Sí, los reglados. Lo que se pide en D1 es que estén tipificados, topados y autorizados por tramo, y que cada uno se registre con su coste en beneficio, no en facturación."),
 ("18:30", "Cada diez puntos de conversión equivalen a una primera visita diaria que no hay que captar ni pagar.",
  "¿No es más fácil captar más pacientes?",
  "Es más caro. Captar más para convertir igual es pagar por desperdicio: por eso captación es la prioridad 4 y conversión la 3."),
 ("19:30", "El valor del paciente en relación frente al paciente en transacción.",
  "¿La cuota del programa compensa el coste de darlo?",
  "La cuota es casi irrelevante. Lo que compensa es lo que arrastra: revisiones que detectan a tiempo, tratamientos sencillos en lugar de complejos y familiares que entran por la puerta."),
 ("20:30", "El área sombreada. Decir la frase tal cual: no se pierde por competencia, se pierde por no volver a llamar.",
  "¿Cuánto es eso en total?",
  "Con 75 tratamientos terminados por trimestre son del orden de 66 k€ de valor a cinco años por cada trimestre de retraso en D5. Está cuantificado en el coste de no decidir."),
 ("21:45", "La escalera de valor y, acto seguido, la aritmética del múltiplo. Es el momento de decir que una inversión que no mueve el beneficio de este año puede ser la más rentable del presupuesto.",
  "¿De dónde salen esos múltiplos?",
  "De rangos habituales del sector en transacciones de clínicas dentales, marcados como modelo. No es una tasación ni una oferta: es el orden de magnitud de lo que está en juego."),
 ("23:15", "Los cinco pasos del escalado. El orden es lo único innegociable. Pedir D11 aquí, y subrayar que hoy es barata porque no hay ninguna oportunidad concreta sobre la mesa.",
  "¿Y si aparece un local irrepetible el mes que viene?",
  "Esa frase —«no se va a repetir»— es literalmente la señal temprana de la causa 5 del pre-mortem. Por eso la condición se fija hoy y no cuando el local esté delante."),
 ("24:30", "Transición.", "", ""),
 ("24:45", "Los cinco riesgos con dueño, y después el registro puntuado: probabilidad por impacto, residual y fecha de revisión.",
  "¿Por qué la cobertura aseguradora paraliza la clínica y los demás riesgos no?",
  "Porque es el único cuyo coste no tiene techo. Los demás se gestionan; ese se evita."),
 ("26:15", "El pre-mortem. Cambiar el tono: estamos en 2029 y esto ha fracasado. Recorrer las seis causas por su señal temprana, no por su descripción.",
  "¿No es un poco derrotista traer esto a una junta?",
  "Es lo contrario: las seis son decisiones nuestras, no accidentes externos. Un riesgo con señal temprana escrita es un riesgo que se puede parar barato."),
 ("28:00", "Los cinco disparadores. Insistir en «sin valorar la gravedad»: ese es el punto entero.",
  "¿Eso no ata las manos a la Dirección?",
  "Protege a la Junta de la Dirección justo cuando la Dirección estaría tentada de minimizar el problema. Y es la decisión D13."),
 ("29:15", "El cuadro de mando: ocho casillas vacías. Convertirlo en fortaleza —es el diagnóstico honesto— y presentar acto seguido el diccionario de indicadores.",
  "¿Cuándo tendremos datos?",
  "En la revisión trimestral, las diez casillas con valor y tendencia. Y la definición operativa ya está acordada, que era el bloqueo real."),
 ("30:45", "Transición.", "", ""),
 ("31:00", "Las cinco palancas en su orden: sostener, recuperar, fidelizar, captar. La menos eficiente es invertir en captación con la cartera propia desatendida.",
  "¿Cuánto tarda la palanca 1 en dar caja?",
  "Semanas, y no cuesta nada más que gestión: es producto ya cobrado que hay que convertir en producción."),
 ("32:15", "El orden de prelación del capital y la única regla de excepción. Decir que la prioridad 2 es la primera que se recorta en cualquier centro con prisa, y que este orden existe para impedirlo. Pedir D10.",
  "¿Y si un trimestre viene mal?",
  "Es exactamente el escenario para el que se aprueba hoy. Sin el orden escrito, la partida que da ventaja competitiva es siempre la primera candidata al recorte."),
 ("33:45", "Los tres horizontes y las tres puertas. Ninguna fase se adelanta por calendario: se pasa por criterio de salida verificado.",
  "¿Y si vamos por delante de lo previsto?",
  "Mejor, pero la puerta sigue siendo la puerta. Adelantar una fase sin criterio de salida es cómo se abre la segunda unidad demasiado pronto."),
 ("35:00", "Las ocho de la operación. Leer solo las cuatro inmediatas y decir, con la cifra delante, lo que cuesta aplazarlas un trimestre.",
  "¿Se pueden aprobar todas hoy?",
  "Las inmediatas sí: no requieren información que no esté en el documento. D5 queda condicionada al dictamen jurídico, que es un plazo, no una duda."),
 ("38:00", "Las seis de la estrategia. Insistir en que fijan las reglas con las que se decidirá lo que aún no está sobre la mesa. Repartir el cuadernillo de acuerdos aquí.",
  "¿Por qué hay que decidir hoy reglas para problemas que no existen?",
  "Porque cuando existan, decidirlas será caro y estará contaminado por el caso concreto. Una regla se aprueba barata solo antes de necesitarla."),
 ("41:45", "Transición. Esta es la parte que la Junta esperaba desde el principio.", "", ""),
 ("42:00", "El puente. Recorrerlo de izquierda a derecha sin detenerse en cada bloque, y parar en el colchón: se planifican 1.440 para comprometer 1.200.",
  "¿Por qué descontar un 17 % de entrada?",
  "Porque de nueve campañas, dos no arrancan a tiempo y una rinde la mitad. Es la tasa normal. Planificar 1.200 para conseguir 1.200 obliga a que las nueve salgan perfectas, y entonces la primera que falle se lleva el objetivo."),
 ("44:00", "La pregunta previa, y es la importante: ¿cabe la cifra en la agenda? Señalar los 5,9 al día frente a los 4 que da la agenda.",
  "Entonces, ¿hay que hacer más marketing?",
  "No. Hacer más marketing traería demanda que no podemos atender, y eso se paga dos veces: el coste de la campaña y el daño de la espera. Lo que hay que hacer es sacar un 10 % más de las mismas cuatro visitas y construir ingreso fuera del embudo."),
 ("46:00", "La composición. Dejar caer la frase: dos tercios del salto no son implantes.",
  "¿Trescientos mil euros de dónde salen exactamente?",
  "De la base de pacientes que el centro ya tiene y hoy no vuelve: cuotas de seguimiento, mantenimiento y el tratamiento que la revisión detecta a tiempo. No hay que captar a nadie para eso."),
 ("47:30", "Las nueve campañas. No leerlas todas: señalar que GTC es una de nueve, y detenerse en los 274 k€ que dependen de decisiones de hoy.",
  "¿No son demasiadas campañas a la vez?",
  "No van a la vez: el calendario de la diapositiva siguiente lo impide. Nunca más de dos arrancando, y cada una con umbral de parada a los sesenta días."),
 ("49:00", "El hallazgo del modelo, y es el que debería salir de la sala: la mitad del objetivo depende de que el seguimiento se ofrezca siempre. Decirlo despacio.",
  "¿No es arriesgado depender tanto de dos campañas?",
  "Sí, y por eso está escrito. Lo tranquilizador es dónde está la concentración: no en la campaña más cara ni en la más incierta, sino en la más barata y la que más control tenemos sobre ella. Depende de nosotros, no del mercado."),
 ("50:30", "El calendario. Insistir en la regla de los dos arranques y en por qué en julio no se enciende nada caro.",
  "¿Qué pasa si una campaña no funciona?",
  "Se para. Cada ficha del anexo B lleva su umbral: si a los sesenta días no llega a la mitad de su ritmo, se detiene y se revisa. Sin umbral escrito, una campaña que no funciona no se cancela nunca."),
 ("52:00", "La senda a tres años. Es el momento de ser explícito: 1,2 M€ es objetivo de año tres, y si la Junta lo quiere en dieciocho meses eso tiene precio y nombre.",
  "¿Por qué no puede ser en el primer año?",
  "Porque haría falta un rendimiento de 1.190 € por primera visita, un 47 % por encima del actual, y las campañas no maduran en doce meses. Se puede comprimir ampliando capacidad, pero entonces se anticipa la prioridad 5 del apartado 15 y debe constar en el acta."),
 ("53:30", "Las cinco condiciones. Terminar la parte recordando que ninguna es una campaña: son condiciones, y si falla una se cae el bloque entero.",
  "¿Cuál le preocupa más?",
  "La segunda. Tres campañas y 232 k€ se apoyan en una cartera propia que nadie ha contado todavía. Es lo más barato de comprobar y está sin hacer: dos semanas de inventario."),
 ("55:00", "Cerrar con los tres resultados verificables. La última frase debe ser la petición concreta: resolver las catorce y fijar la fecha de la próxima revisión.",
  "¿Qué pasa si no aprobamos alguna?",
  "Se registra como no resuelta con su fecha de reconsideración. Lo que no puede pasar es que salga de aquí sin decisión y sin fecha: eso es la causa 6 del pre-mortem."),
]

assert len(NOTAS) == len(DIAPOSITIVAS), (len(NOTAS), len(DIAPOSITIVAS))


def con_guion(html, i):
    """Añade a la diapositiva su marca de ruta, su minuto y su nota de ponente."""
    minuto, decir, pregunta, respuesta = NOTAS[i]
    marca = ' data-min="%s"%s' % (minuto, ' data-esencial="1"' if i + 1 in ESENCIAL else "")
    html = html.replace('<section class="slide', '<section' + marca + ' class="slide', 1)
    if not decir:
        return html
    dificil = ""
    if pregunta:
        dificil = ('\n    <div class="nota__dura"><b>La pregunta difícil</b>'
                   '<p class="nota__q">%s</p><p>%s</p></div>' % (pregunta, respuesta))
    nota = ('\n  <aside class="nota" hidden>\n'
            '    <div><b>Minuto %s%s</b><p>%s</p></div>%s\n  </aside>\n'
            % (minuto, " · ruta corta" if i + 1 in ESENCIAL else "", decir, dificil))
    return html.replace("</section>", nota + "</section>")


DIAPOSITIVAS = [con_guion(d, i) for i, d in enumerate(DIAPOSITIVAS)]

documento = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Presentación de la Plan de Dirección del Centro de Excelencia Implantológica Giraldo ante la Junta Directiva: posición competitiva, foso, sistema operativo, economía unitaria, valor de empresa, escalado, pre-mortem, asignación de capital, el puente hasta el objetivo de 1,2 M€ y las quince decisiones que se someten a aprobación.">
<title>Plan de Dirección · Junta Giraldo</title>
%s
<style>
%s
%s
</style>
</head>
<body>

<div class="deck-raiz">
<div class="deck">
%s
</div>

<div class="barra" aria-hidden="true"><i data-deck="progreso"></i></div>
<div class="hud">
  <span class="hud__marca">Centro de Excelencia Implantológica Giraldo · Junta Directiva · v@VERSION@</span>
  <span class="hud__modo" data-deck="rotulo-ruta" hidden>Ruta corta</span>
  <span class="hud__modo" data-deck="rotulo-ponente" hidden>Ponente</span>
  <span class="hud__min" data-deck="minuto"></span>
  <button data-deck="prev" type="button" aria-label="Diapositiva anterior">←</button>
  <span class="hud__n" data-deck="n" aria-live="polite">1 / %d</span>
  <button data-deck="next" type="button" aria-label="Diapositiva siguiente">→</button>
  <button data-deck="ruta" type="button" aria-pressed="false" title="Ruta corta: doce diapositivas (tecla E)">E</button>
  <button data-deck="ponente" type="button" aria-pressed="false" title="Guion del ponente (tecla N)">N</button>
</div>
</div>

<script>
%s
</script>
</body>
</html>
""" % (fuentes, tokens, CSS, "\n".join(DIAPOSITIVAS), len(DIAPOSITIVAS), JS)

(RAIZ / "deck.html").write_text(sello(documento), encoding="utf-8")
print("deck.html ·", len(DIAPOSITIVAS), "diapositivas ·", (RAIZ / "deck.html").stat().st_size // 1024, "KB")
