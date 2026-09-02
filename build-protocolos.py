#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""protocolos.html: el protocolo del centro, visto desde cada puesto.

    python3 build-protocolos.py

El sistema tenía todo lo que hace falta para trabajar, repartido en cuatro
documentos: el manual del puesto en el Manual Maestro, la matriz RACI en su
Parte III, las catorce fases en el Protocolo de Primera Visita y los protocolos
operativos en Otros documentos. Quien llega un lunes a trabajar de auxiliar no
tiene que recorrer cuatro documentos para saber qué se espera de él.

Esta página no copia el texto: lo señala. Se elige el puesto y aparece, en un
solo sitio, en qué fases interviene y con qué papel, qué procedimientos tiene
escritos, qué funciones de vanguardia le tocan, con qué se le mide y qué se
espera de él los primeros treinta días. Cada línea lleva al documento donde
está el detalle, que sigue siendo el que manda.
"""
import html as H
import pathlib
import re
import sys
import types

RAIZ = pathlib.Path(__file__).parent
sys.path.insert(0, str(RAIZ))
import perfiles as P  # noqa: E402

_v = {"__name__": "version_prot", "__file__": "version.py"}
exec(compile((RAIZ / "version.py").read_text(encoding="utf-8"), "version.py", "exec"), _v)
VERSION, FECHA = _v["VERSION"], _v["FECHA"]

_menu = types.ModuleType("menu")
exec(compile((RAIZ / "menu.py").read_text(encoding="utf-8"), "menu.py", "exec"), _menu.__dict__)

CLASE = {"R/A": "es-ra", "R": "es-r", "A": "es-a", "C": "es-c", "I": "es-i", "—": "es-no"}

# el ancla de cada fase en el Protocolo de Primera Visita, para poder ir al detalle
ANCLA_FASE = ["f01", "f02", "f03", "f04", "f05", "f06",
              "f07", "f08", "f09", "f10", "f11", "f12", None, None]


def fases(p):
    filas = []
    for i, (nombre, papel) in enumerate(P.raci_de(p)):
        titulo, explica = P.QUE_ES[papel]
        ancla = ANCLA_FASE[i]
        rot = H.escape(nombre)
        enlace = ('<a href="index.html#%s">%s</a>' % (ancla, rot)) if ancla else rot
        filas.append(
            '<tr class="%s"><td class="pf__f">%s</td>'
            '<td><span class="pf__p">%s</span></td>'
            '<td class="pf__q">%s</td></tr>'
            % (CLASE[papel], enlace, H.escape(titulo), H.escape(explica)))
    return "".join(filas)


def lista(titulo, entradas, destino, vacio):
    if not entradas:
        return ('<section class="pf__b"><h3>%s</h3><p class="pf__vacio">%s</p></section>'
                % (H.escape(titulo), H.escape(vacio)))
    filas = "".join('<li><a href="%s#%s">%s</a></li>' % (destino, a, H.escape(r))
                    for r, a in entradas)
    return ('<section class="pf__b"><h3>%s</h3><ul class="pf__l">%s</ul></section>'
            % (H.escape(titulo), filas))


def panel(p):
    activas = sum(1 for _, x in P.raci_de(p) if x not in ("—", "I"))
    return (
        '<section class="pf" id="perfil-%s" data-perfil="%s" hidden>\n'
        '  <header class="pf__cab">\n'
        '    <h2>%s</h2>\n'
        '    <p class="pf__que">%s</p>\n'
        '    <ul class="pf__cifras">\n'
        '      <li><b>%d</b><span>fases en las que interviene</span></li>\n'
        '      <li><b>%d</b><span>bloques de su manual de puesto</span></li>\n'
        '      <li><b>%d</b><span>funciones de vanguardia</span></li>\n'
        '    </ul>\n'
        '  </header>\n'
        '  <div class="pf__rej">\n'
        '    <section class="pf__b pf__b--ancha">\n'
        '      <h3>Su papel en las catorce fases del recorrido</h3>\n'
        '      <p class="pf__ayuda">Sale de la matriz RACI del Manual Maestro. '
        'Las fases 1 a 12 llevan al Protocolo de Primera Visita, donde están '
        'contadas minuto a minuto.</p>\n'
        '      <div class="tablewrap"><table><thead><tr>'
        '<th>Fase</th><th>Su papel</th><th>Qué significa</th>'
        '</tr></thead><tbody>%s</tbody></table></div>\n'
        '    </section>\n'
        '    %s\n    %s\n'
        '    <section class="pf__b">\n'
        '      <h3>Dónde está todo lo suyo</h3>\n'
        '      <ul class="pf__l">\n'
        '        <li><a href="manual.html#%s">Manual del puesto, completo</a></li>\n'
        '        <li><a href="manual.html#p3">La matriz RACI de las catorce fases</a></li>\n'
        '        <li><a href="index.html">El Protocolo de Primera Visita, fase a fase</a></li>\n'
        '        <li><a href="otros.html#otros-perfiles">Protocolos operativos por perfil</a></li>\n'
        '        <li><a href="otros.html#otros-transicion-perfiles">Puesta en marcha por perfil</a></li>\n'
        '      </ul>\n'
        '    </section>\n'
        '  </div>\n'
        '</section>'
        % (p["id"], p["id"], H.escape(p["nombre"]), H.escape(p["que"]),
           activas, len(p["bloques"]), len(p["vanguardia"]),
           fases(p),
           lista("Su manual de puesto", p["bloques"], "manual.html", ""),
           lista("Sus funciones de vanguardia", p["vanguardia"], "manual.html",
                 "Este puesto no tiene funciones de vanguardia propias: las suyas "
                 "son de gobierno del sistema y están en su manual."),
           p["manual"]))


def sello(t):
    return t.replace("@VERSION@", VERSION).replace("@FECHA@", FECHA)


manual = (RAIZ / "manual.html").read_text(encoding="utf-8")
i = manual.index("<body>")
cabecera = manual[:i + len("<body>")]
cabecera = cabecera.replace("<title>Manual Maestro Giraldo</title>",
                            "<title>Protocolos por puesto · Giraldo</title>")
cabecera = re.sub(r'<meta name="description" content="[^"]*">',
                  '<meta name="description" content="El protocolo del Centro de Excelencia '
                  'Implantológica Giraldo visto desde cada puesto: elija Dirección, Doctor, '
                  'Recepción, RAC, Auxiliar o Higienista y vea en qué fases interviene, con qué '
                  'papel, qué procedimientos tiene escritos y con qué se le mide.">',
                  cabecera, count=1)

CSS = """
/* ---------------------------------------------------------------------------
   PROTOCOLOS POR PUESTO
   Un selector de seis y, debajo, todo lo que el sistema dice de ese puesto.
   Sin guiones se ven los seis seguidos, cada uno con su titular.
   --------------------------------------------------------------------------- */
.selector{
  display:flex;flex-wrap:wrap;gap:.5rem;margin:1.8rem 0 2.4rem;
  padding:.5rem;background:var(--surface);border:1px solid var(--line);
  border-radius:999px;width:fit-content;max-width:100%;
}
.selector button{
  font:inherit;font-size:.92rem;font-weight:500;cursor:pointer;
  border:1px solid transparent;background:transparent;color:var(--ink-2);
  border-radius:999px;padding:.5rem 1.05rem;white-space:nowrap;
  transition:background .15s ease,color .15s ease;
}
.selector button:hover{background:var(--surface-2);color:var(--ink)}
.selector button[aria-selected="true"]{background:var(--accent);color:#fff}
.selector button:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.js .selector{display:flex}
.selector{display:none}
.js .selector{display:flex}

.pf[hidden]{display:none}
.js .pf{display:none}
.js .pf.is-on{display:block}
:root:not(.js) .pf{display:block!important}
@media print{.pf{display:block!important}.selector{display:none!important}}

.pf__cab{max-width:64ch;margin-bottom:1.8rem}
.pf__cab h2{font-size:var(--step-3);margin:0 0 .6rem}
.pf__que{font-size:var(--step-1);line-height:1.5;color:var(--ink-2);margin:0}
.pf__cifras{
  list-style:none;display:flex;flex-wrap:wrap;gap:.6rem;margin:1.4rem 0 0;padding:0;
}
.pf__cifras li{
  background:var(--surface);border:1px solid var(--line);border-radius:var(--radio);
  padding:.85rem 1.1rem;min-width:9rem;
}
.pf__cifras b{
  display:block;font-size:1.7rem;font-weight:600;letter-spacing:-.03em;
  line-height:1;color:var(--accent-ink);font-variant-numeric:tabular-nums;
}
.pf__cifras span{display:block;margin-top:.35rem;font-size:.78rem;color:var(--muted)}

.pf__rej{
  display:grid;gap:1rem;
  grid-template-columns:repeat(auto-fill,minmax(min(340px,100%),1fr));
  align-items:start;
}
.pf__b{
  background:var(--surface);border:1px solid var(--line);border-radius:var(--radio);
  padding:1.3rem 1.4rem 1.45rem;min-width:0;
}
.pf__b--ancha{grid-column:1/-1}
.pf__b h3{font-size:1.05rem;margin:0 0 .5rem}
.pf__ayuda{font-size:.86rem;color:var(--muted);line-height:1.5;margin:0 0 1rem;max-width:72ch}
.pf__vacio{font-size:.9rem;color:var(--muted);line-height:1.55;margin:0}
.pf__l{list-style:none;margin:.2rem 0 0;padding:0;display:grid;gap:1px}
.pf__l li + li{border-top:1px solid var(--line-soft)}
.pf__l a{
  display:block;padding:.55rem .1rem;text-decoration:none;color:var(--ink-2);
  font-size:.92rem;line-height:1.35;
}
.pf__l a:hover{color:var(--accent-ink)}
.pf__l a::after{content:" →";color:var(--muted);font-size:.85em}

.pf__b .tablewrap{margin-top:0}
.pf__f a{color:var(--ink);text-decoration:none;font-weight:500}
.pf__f a:hover{color:var(--accent-ink);text-decoration:underline;text-underline-offset:3px}
.pf__p{
  display:inline-block;font-family:var(--f-mono);font-size:.7rem;font-weight:500;
  letter-spacing:.03em;border-radius:999px;padding:.2rem .6rem;white-space:nowrap;
}
.pf__q{color:var(--muted);font-size:.86rem}
tr.es-ra .pf__p{background:var(--accent);color:#fff}
tr.es-r  .pf__p{background:var(--accent-soft);color:var(--accent-ink)}
tr.es-a  .pf__p{background:var(--signal-soft);color:var(--signal)}
tr.es-c  .pf__p{background:var(--surface-2);color:var(--ink-2)}
tr.es-i  .pf__p{background:transparent;color:var(--muted);border:1px solid var(--line)}
tr.es-no .pf__p{background:transparent;color:var(--muted)}
tr.es-no td{opacity:.55}
@media(max-width:640px){
  .selector{border-radius:var(--radio);width:100%}
  .selector button{flex:1 1 auto;text-align:center}
}
"""

k = cabecera.rindex("</style>")
cabecera = cabecera[:k] + CSS + "\n" + cabecera[k:]

BOTONES = "".join(
    '<button type="button" role="tab" data-va="%s" aria-selected="%s" '
    'aria-controls="perfil-%s">%s</button>'
    % (p["id"], "true" if n == 0 else "false", p["id"], H.escape(p["corto"]))
    for n, p in enumerate(P.PERFILES))

CUERPO = """
<header class="topbar">
  <div class="wrap">
    <div class="topbar__in">
      <a class="brand" href="#portada">
        <span class="brand__mark">Protocolos por <b>puesto</b></span>
        <span class="brand__tag">Giraldo · v@VERSION@</span>
      </a>
      <a class="crosslink" href="manual.html">Manual Maestro</a>
      <a class="crosslink" href="index.html">Protocolo de Primera Visita</a>
      <a class="crosslink" href="otros.html">Otros documentos</a>
    </div>
    <nav class="strip" id="strip" aria-label="Secciones"></nav>
  </div>
</header>

<main>

<div class="printhead" aria-hidden="true"><b>Protocolos por puesto · v@VERSION@</b><span>Centro de Excelencia Implantológica Giraldo · Uso interno · Confidencial</span></div>

<section class="hero" id="portada">
  <div class="wrap">
    <p class="eyebrow">Vista operativa · Uso interno</p>
    <h1>Qué se espera de cada puesto</h1>
    <p class="hero__lede">Todo lo que el sistema dice de un puesto vivía repartido en cuatro documentos: su manual en el Manual Maestro, su papel en la matriz RACI, sus fases en el Protocolo de Primera Visita y sus protocolos operativos en Otros documentos. Quien llega un lunes a trabajar no debería recorrer cuatro documentos para saber qué se espera de él.</p>
    <p class="hero__note">Elija el puesto y aparece en un solo sitio: en qué fases interviene y con qué papel, qué procedimientos tiene escritos, qué funciones de vanguardia le tocan, con qué se le mide y qué se espera de él los primeros treinta días. Cada línea lleva al documento donde está el detalle, que sigue siendo el que manda: <strong>esta página señala, no sustituye</strong>.</p>
  </div>
</section>

<section class="section" id="puestos">
  <div class="wrap">
    <div class="section__head">
      <p class="eyebrow">Los seis puestos</p>
      <h2>Elija el suyo</h2>
      <p>La matriz RACI reparte las catorce fases del recorrido entre seis puestos. R ejecuta, A responde del resultado, C se consulta antes de decidir y I se informa después. Una fase sin A es una fase de la que no responde nadie.</p>
    </div>
    <div class="selector" role="tablist" aria-label="Puesto">@@BOTONES@@</div>
@@PANELES@@
  </div>
</section>

<section class="section" id="comun">
  <div class="wrap">
    <div class="section__head">
      <p class="eyebrow">Común a los seis</p>
      <h2>Lo que se cumple en todos los puestos</h2>
    </div>
    <div class="pf__rej">
      <section class="pf__b">
        <h3>Estándares transversales</h3>
        <p class="pf__ayuda">Comunicación y trato, seguridad clínica, protección de datos, entorno físico y agenda. Se cumplen en las catorce fases y en los seis puestos.</p>
        <ul class="pf__l"><li><a href="manual.html#estandares">Ver los estándares transversales</a></li></ul>
      </section>
      <section class="pf__b">
        <h3>Cómo se mide si funciona</h3>
        <p class="pf__ayuda">Cada puesto tiene sus indicadores, y el centro tiene los diez del cuadro de mando. Sin serie propia, cualquier objetivo es una opinión.</p>
        <ul class="pf__l">
          <li><a href="manual.html#p6">Indicadores e interdependencias</a></li>
          <li><a href="instrumentos/captura.html">Los números del centro, mes a mes</a></li>
        </ul>
      </section>
      <section class="pf__b">
        <h3>Qué pasa si un puesto no cumple</h3>
        <p class="pf__ayuda">La matriz de obligaciones dice qué se rompe aguas abajo cuando un puesto se salta lo suyo. No es una amenaza: es la razón por la que el orden importa.</p>
        <ul class="pf__l"><li><a href="manual.html#p4">Ver la matriz de obligaciones</a></li></ul>
      </section>
      <section class="pf__b">
        <h3>Cómo se aprende y se certifica</h3>
        <p class="pf__ayuda">Incorporación en los primeros treinta días, certificación por rol y rúbrica de auditoría de una primera visita real.</p>
        <ul class="pf__l">
          <li><a href="index.html#formacion">Formación y certificación por rol</a></li>
          <li><a href="index.html#indicadores">Rúbrica de auditoría</a></li>
        </ul>
      </section>
    </div>
  </div>
</section>

</main>

<footer class="foot">
  <div class="wrap">
    <div class="ticks" aria-hidden="true" style="margin-bottom:2rem"></div>
    <div class="foot__grid">
      <div><p><strong>Centro de Excelencia Implantológica Giraldo</strong><br>Protocolos por puesto · Uso interno y confidencial</p></div>
      <div><p class="eyebrow">De dónde sale</p><p>Manual Maestro · matriz RACI<br>Protocolo de Primera Visita<br>Otros documentos del sistema</p></div>
      <div><p class="eyebrow">Versión</p><p>Versión única del sistema<br><strong>v@VERSION@ · @FECHA@</strong></p></div>
    </div>
  </div>
</footer>
""".replace("@@BOTONES@@", BOTONES).replace(
    "@@PANELES@@", "\n".join("    " + panel(p) for p in P.PERFILES))

JS = """
<script>
(function(){
  "use strict";
  var sel = document.querySelector(".selector");
  if(!sel) return;
  /* El selector se busca dentro de su propio contenedor y no en toda la página:
     en el archivo único los nueve documentos conviven en el mismo DOM y una
     búsqueda global habría barrido paneles de otro sitio. */
  var raiz = sel.closest("main") || document;
  var paneles = [].slice.call(raiz.querySelectorAll(".pf"));
  var botones = [].slice.call(sel.querySelectorAll("button"));
  /* «perfil-doctor» aquí; «ps-perfil-doctor» en el archivo único, que antepone
     un prefijo a todos los identificadores para que no choquen. */
  var ES_PERFIL = /^#([a-z]+-)?perfil-/;
  function pon(id, mover){
    paneles.forEach(function(p){
      var si = p.dataset.perfil === id;
      p.hidden = !si;
      p.classList.toggle("is-on", si);
    });
    botones.forEach(function(b){
      b.setAttribute("aria-selected", String(b.dataset.va === id));
    });
    /* Solo se toca la dirección si ya hablaba de puestos o si no decía nada:
       en el archivo único la dirección es la que elige documento, y escribirla
       aquí al cargar habría echado al lector del documento que estaba viendo. */
    var actual = location.hash || "";
    if(!actual || ES_PERFIL.test(actual)){
      try { history.replaceState(null, "", "#perfil-" + id); } catch(e){}
    }
    if(mover) sel.scrollIntoView({block:"start", behavior:"smooth"});
  }
  sel.addEventListener("click", function(e){
    var b = e.target.closest("button");
    if(b) pon(b.dataset.va, false);
  });
  sel.addEventListener("keydown", function(e){
    var i = botones.indexOf(document.activeElement);
    if(i < 0) return;
    var j = e.key === "ArrowRight" ? i + 1 : e.key === "ArrowLeft" ? i - 1 : -1;
    if(j < 0 || j >= botones.length) return;
    e.preventDefault(); botones[j].focus(); pon(botones[j].dataset.va, false);
  });
  var h = (location.hash || "").replace(ES_PERFIL, "");
  pon(paneles.some(function(p){ return p.dataset.perfil === h; }) ? h : paneles[0].dataset.perfil, false);
  /* Un enlace a otro puesto desde dentro de la página cambia de pestaña. */
  window.addEventListener("hashchange", function(){
    var d = (location.hash || "").replace(ES_PERFIL, "");
    if(ES_PERFIL.test(location.hash) && paneles.some(function(p){ return p.dataset.perfil === d; })) pon(d, true);
  });
})();
</script>
"""

(RAIZ / "protocolos.html").write_text(
    sello(cabecera + "\n" + CUERPO + "\n" + JS + "\n</body>\n</html>\n"),
    encoding="utf-8")
print("protocolos.html ·", len(P.PERFILES), "puestos ·",
      (RAIZ / "protocolos.html").stat().st_size // 1024, "KB")
