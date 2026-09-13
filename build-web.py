#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build-web.py — la web, empezada de cero.

Una web-documento LIMPIA: blanca, con un azul pizarra sobrio, apartados bien
diferenciados, cuadros para destacar conceptos y cifras, y nada de artificios
—ni recorridos guiados, ni mapa pulsable, ni lector emergente, ni tablero de
mando animado—. Solo el contenido, ordenado y fácil de navegar.

El contenido no se toca ni se pierde: se reutiliza `monta()` del sistema de
siempre, que cosecha los ocho documentos en 135 apartados ya verificados. Aquí
solo cambia la PIEL y la disposición: se envuelve ese mismo contenido en una
cáscara nueva, mínima y profesional.

    python3 build-web.py        → web.html
"""
import importlib.util
import re
import html as H
import pathlib
import base64

RAIZ = pathlib.Path(__file__).parent

# ---------------------------------------------------------------- el contenido
# Se carga el generador de siempre como módulo (el guion lleva guion en el
# nombre y no se puede importar a secas) y se le pide lo único que interesa: el
# contenido cosechado de los ocho documentos.
_spec = importlib.util.spec_from_file_location("bs", str(RAIZ / "build-sitio.py"))
bs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bs)

SECCIONES = [
    ("direccion", "Dirección", "memoria.html", "Plan de Dirección"),
    ("presentacion", "Presentación", "deck.html", "Presentación de Junta"),
    ("protocolos", "Protocolos", "protocolos.html", "Protocolos por puesto"),
    ("primera-visita", "Primera Visita", "index.html", "Protocolo de Primera Visita"),
    ("operaciones", "Operaciones", "manual.html", "Manual Maestro de Operaciones"),
    ("marketing", "Marketing", "marketing.html", "Plan Maestro de Marketing"),
    ("otros", "Otros", "otros.html", "Otros documentos del sistema"),
    ("numeros", "Los números", "instrumentos/captura.html", "Los números del centro"),
]

# Frases de entrada de cada sección: las mismas que ya escribía el sistema.
INTRO = bs.INTROS


def fuentes_incrustadas():
    """Instrument Serif —la serif de los titulares— empotrada en el archivo."""
    fmt = ('@font-face{font-family:"Instrument Serif";font-style:%s;font-weight:400;'
           'font-display:swap;src:url(data:font/ttf;base64,%s) format("truetype")}')
    out = []
    for estilo, arch in (("normal", "InstrumentSerif-Regular.ttf"),
                         ("italic", "InstrumentSerif-Italic.ttf")):
        ruta = RAIZ / "fuentes" / "tipos" / arch
        if ruta.exists():
            b64 = base64.b64encode(ruta.read_bytes()).decode()
            out.append(fmt % (estilo, b64))
    return "".join(out)


def fuentes_archivo():
    """Archivo e IBM Plex Mono, ya incrustadas en base64 y sin conexión.

    Se reutiliza la caché que el sistema deja en export/_fuentes.html (la misma
    que empotra el resto de la entrega). Así la web se abre de doble clic sin
    pedir una letra a la red. Si la caché no está, se cae al enlace de Google
    —solo pasa en una máquina que nunca haya construido la entrega—. """
    cache = RAIZ / "export" / "_fuentes.html"
    if cache.exists():
        return cache.read_text(encoding="utf-8")
    return ('<link rel="preconnect" href="https://fonts.googleapis.com">'
            '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
            'family=Archivo:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap">')


def css_documentos():
    """Todo el CSS que usan los apartados cosechados, junto y una sola vez.

    Los ocho documentos comparten un marco de estilos (las clases t-…, wrap,
    eyebrow, las tablas, las figuras) repartido en varios <style>. Se recogen
    todos, se quitan los duplicados exactos y se devuelven en bloque, para que
    el contenido se vea tal como se escribió. La PALETA la manda luego el tema:
    estos estilos usan tokens (--ink, --paper, --accent…) que se redefinen. """
    vistos, trozos = set(), []
    for _id, _rot, doc, _n in SECCIONES:
        texto = bs.fuente(doc)
        for m in re.finditer(r"<style>(.*?)</style>", texto, re.S):
            css = m.group(1)
            firma = css[:120]
            if firma in vistos:
                continue
            vistos.add(firma)
            trozos.append(css)
    return "\n".join(trozos)


# --------------------------------------------------------------------- el tema
# Blanco y azul pizarra. Se redefinen los tokens de los documentos a esta
# paleta y se apoya el marco propio. Va DESPUÉS del CSS de los documentos y con
# «html:root» para ganar la especificidad, de modo que manda esta paleta.
TEMA = """
:root, html:root{
  --fondo:#FBFBFA; --panel:#FFFFFF; --panel-2:#F4F6F8;
  --tinta:#1A2A34; --ink:#1A2A34; --ink-2:#465A66; --muted:#748690;
  --pizarra:#33587C; --pizarra-o:#2C4A6A; --pizarra-fuerte:#22405C;
  --pizarra-soft:rgba(51,88,124,.07); --pizarra-linea:rgba(51,88,124,.22);
  --linea:rgba(26,42,52,.12); --linea-2:rgba(26,42,52,.07);
  --serif:"Instrument Serif",Georgia,"Times New Roman",serif;
  --sans:"Archivo","Helvetica Neue",Arial,sans-serif;
  --mono:"IBM Plex Mono",ui-monospace,Menlo,monospace;
  --nav:64px; --ancho:74rem;
  /* los tokens de los documentos, remapeados a esta paleta */
  --paper:var(--fondo); --surface:var(--panel); --surface-2:var(--panel-2);
  --accent:var(--pizarra); --accent-ink:var(--pizarra-fuerte);
  --accent-fuerte:var(--pizarra-fuerte); --accent-soft:var(--pizarra-soft);
  --acido:var(--pizarra-soft); --acido-ink:var(--pizarra-fuerte);
  --line:var(--linea); --line-soft:var(--linea-2); --rule:var(--linea);
  --f-body:var(--sans); --f-display:var(--serif); --f-mono:var(--mono);
  --tinta-doc:var(--tinta); --barra:var(--nav);
  --sombra-2:0 1px 2px rgba(26,42,52,.05),0 12px 28px -20px rgba(26,42,52,.30);
}
"""


# ------------------------------------------------------------------ el marco
# La cáscara propia: cabecera, inicio, secciones, índice y apartados. Va al
# final de la cascada para mandar sobre el CSS de los documentos donde importa.
SHELL = """
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
html body{margin:0;background:var(--fondo);color:var(--tinta);
  font-family:var(--sans);font-size:16px;line-height:1.65;
  -webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility}
img{max-width:100%}
::selection{background:var(--pizarra);color:#fff}

/* Cabecera fija */
.cab{position:sticky;top:0;z-index:50;background:rgba(251,251,250,.92);
  backdrop-filter:saturate(1.2) blur(10px);border-bottom:1px solid var(--linea);
  min-height:var(--nav);display:flex;align-items:center;gap:clamp(1rem,3vw,2.4rem);
  padding:0 clamp(1rem,4vw,3rem)}
.cab__m{font-family:var(--serif);font-size:1.4rem;letter-spacing:.01em;
  color:var(--tinta);text-decoration:none;flex:none;line-height:1}
.cab__nav{display:flex;gap:.1rem;flex:1 1 auto;min-width:0;overflow-x:auto;
  scrollbar-width:none}
.cab__nav::-webkit-scrollbar{display:none}
.cab__l{font-family:var(--mono);font-size:.68rem;letter-spacing:.03em;
  text-transform:uppercase;color:var(--ink-2);text-decoration:none;
  padding:.5rem .7rem;border-radius:5px;white-space:nowrap;cursor:pointer;
  border:0;background:none;transition:color .15s,background .15s}
.cab__l:hover{color:var(--pizarra);background:var(--pizarra-soft)}
.cab__l.on{color:var(--pizarra-fuerte);background:var(--pizarra-soft);font-weight:600}

/* Una vista a la vez */
.vista{display:none}
.vista.on{display:block}
.env{max-width:var(--ancho);margin:0 auto;
  padding:clamp(1.6rem,4vw,3.4rem) clamp(1.2rem,4vw,3rem) 6rem}

/* Inicio */
.whero{padding:clamp(1.6rem,6vh,4rem) 0 clamp(1.6rem,4vh,3rem)}
.whero__k{font-family:var(--mono);font-size:.72rem;letter-spacing:.18em;
  text-transform:uppercase;color:var(--muted);margin:0 0 1.4rem}
.whero h1{font-family:var(--serif);font-weight:400;
  font-size:clamp(2.6rem,8vw,5.4rem);line-height:.98;letter-spacing:-.005em;
  margin:0;color:var(--tinta)}
.whero h1 em{font-style:italic;color:var(--pizarra)}
.whero__p{font-size:clamp(1.05rem,2.2vw,1.3rem);max-width:36ch;
  color:var(--ink-2);margin:1.6rem 0 0;line-height:1.5}
.whero__d{font-family:var(--mono);font-size:.66rem;letter-spacing:.12em;
  text-transform:uppercase;color:var(--muted);margin:1.6rem 0 0}

/* Cuadros de cifras */
.cifras{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));
  gap:1px;background:var(--linea);border:1px solid var(--linea);
  margin:clamp(2rem,5vh,3.4rem) 0}
.cifra{background:var(--panel);padding:1.4rem 1.3rem}
.cifra b{font-family:var(--serif);font-size:2.5rem;font-weight:400;
  display:block;color:var(--pizarra);line-height:1}
.cifra span{font-family:var(--mono);font-size:.6rem;letter-spacing:.09em;
  text-transform:uppercase;color:var(--muted);display:block;margin-top:.5rem}

/* Tarjetas de secciones */
.wsecs{display:grid;grid-template-columns:repeat(auto-fill,minmax(255px,1fr));
  gap:1rem;margin-top:1rem}
.tarjeta{display:flex;flex-direction:column;text-decoration:none;color:inherit;
  background:var(--panel);border:1px solid var(--linea);border-radius:10px;
  padding:1.5rem;transition:border-color .18s,box-shadow .18s,transform .18s;cursor:pointer}
.tarjeta:hover{border-color:var(--pizarra-linea);box-shadow:var(--sombra-2);transform:translateY(-2px)}
.tarjeta__n{font-family:var(--mono);font-size:.64rem;color:var(--pizarra);letter-spacing:.1em}
.tarjeta h3{font-family:var(--serif);font-weight:400;font-size:1.5rem;
  margin:.6rem 0 .35rem;color:var(--tinta);line-height:1.1}
.tarjeta p{font-size:.86rem;color:var(--ink-2);margin:0;flex:1}
.tarjeta__c{font-family:var(--mono);font-size:.58rem;color:var(--muted);
  text-transform:uppercase;letter-spacing:.08em;margin-top:1.1rem}

/* Cabecera de sección */
.sh{padding-bottom:1.8rem;margin-bottom:2.4rem;border-bottom:2px solid var(--pizarra)}
.sh__n{font-family:var(--mono);font-size:.7rem;letter-spacing:.16em;
  text-transform:uppercase;color:var(--pizarra);margin:0 0 1rem}
.sh h1{font-family:var(--serif);font-weight:400;font-size:clamp(2rem,5vw,3.3rem);
  margin:0;color:var(--tinta);line-height:1.05}
.sh__p{font-size:1.05rem;color:var(--ink-2);max-width:62ch;margin:1.1rem 0 0;line-height:1.55}

/* Cifras del documento (del tablero), como cuadros */
.docif{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));
  gap:1px;background:var(--linea);border:1px solid var(--linea);margin:0 0 3rem}
.docif__i{background:var(--panel);padding:1.2rem 1.2rem}
.docif__i b{font-family:var(--serif);font-size:1.9rem;font-weight:400;color:var(--pizarra);
  display:block;line-height:1}
.docif__i span{font-size:.78rem;color:var(--tinta);display:block;margin-top:.4rem;font-weight:600}
.docif__i small{font-size:.72rem;color:var(--muted);display:block;margin-top:.2rem;line-height:1.35}

/* Índice + contenido */
.cuerpo{display:grid;grid-template-columns:15rem minmax(0,1fr);
  gap:clamp(1.5rem,4vw,3.4rem);align-items:start}
.toc{position:sticky;top:calc(var(--nav) + 1.4rem);font-size:.84rem;
  max-height:calc(100vh - var(--nav) - 2.6rem);overflow:auto;padding-right:.4rem}
.toc__t{font-family:var(--mono);font-size:.6rem;letter-spacing:.14em;
  text-transform:uppercase;color:var(--muted);margin:0 0 .9rem}
.toc a{display:block;text-decoration:none;color:var(--ink-2);
  padding:.3rem 0 .3rem .85rem;border-left:2px solid var(--linea);line-height:1.35;
  transition:color .15s,border-color .15s}
.toc a:hover{color:var(--pizarra);border-color:var(--pizarra-linea)}
.toc a.on{color:var(--pizarra-fuerte);border-color:var(--pizarra);font-weight:600}
.toc__parte{font-family:var(--mono);font-size:.57rem;letter-spacing:.1em;
  text-transform:uppercase;color:var(--pizarra);margin:1.3rem 0 .4rem;padding-left:.85rem}
.toc__parte:first-child{margin-top:0}

/* Apartados */
.wlista{min-width:0}
.wart{padding:2.6rem 0;border-bottom:1px solid var(--linea);scroll-margin-top:calc(var(--nav) + 1rem)}
.wart:first-child{padding-top:.5rem}
.wart:last-child{border-bottom:0}
.wart__k{font-family:var(--mono);font-size:.62rem;letter-spacing:.12em;
  text-transform:uppercase;color:var(--muted);margin:0 0 1rem}
.wart .wrap{max-width:none;margin:0;padding:0;width:auto}
.wart h2{font-family:var(--serif);font-weight:400;font-size:clamp(1.5rem,3.4vw,2.15rem);
  line-height:1.12;color:var(--tinta);letter-spacing:-.008em;margin:0 0 1rem}
.wart h2 em,.wart h2 br{font-style:italic}
.wart h3{font-family:var(--serif);font-weight:400;font-size:1.3rem;color:var(--tinta);
  margin:2rem 0 .8rem}
.wart p{font-size:1.02rem;line-height:1.7;color:var(--tinta)}
.wart .eyebrow{font-family:var(--mono);font-size:.62rem;letter-spacing:.12em;
  text-transform:uppercase;color:var(--pizarra);font-weight:600}

/* Tablas, limpias y en cuadro */
.wart table{border-collapse:collapse;width:100%;font-size:.9rem;margin:1.4rem 0;
  border:1px solid var(--linea)}
.wart th,.wart td{border:1px solid var(--linea);padding:.6rem .8rem;text-align:left;
  vertical-align:top;background:var(--panel)}
.wart th{background:var(--panel-2);font-family:var(--mono);font-size:.68rem;
  letter-spacing:.04em;text-transform:uppercase;color:var(--ink-2);font-weight:600}
.wart figure{margin:1.6rem 0;padding:1.2rem;border:1px solid var(--linea);
  border-radius:8px;background:var(--panel);overflow-x:auto}
.wart figure svg{max-width:100%;height:auto}
.wart figcaption{font-size:.78rem;color:var(--muted);margin-top:.8rem;text-align:center}

/* Cuadro para destacar (lo que en los documentos era una lista numerada de
   principios, una cita de cierre, etc.) */
.wart ol,.wart ul{padding-left:1.3rem}
.wart li{margin:.5rem 0;line-height:1.6}
.wart blockquote{margin:1.4rem 0;padding:1.2rem 1.4rem;border-left:3px solid var(--pizarra);
  background:var(--pizarra-soft);border-radius:0 8px 8px 0;font-size:1.05rem;color:var(--tinta)}

/* Pie */
.pie{border-top:1px solid var(--linea);margin-top:3rem;padding:2rem 0;
  font-family:var(--mono);font-size:.64rem;letter-spacing:.1em;text-transform:uppercase;
  color:var(--muted);text-align:center}

/* Componentes que en los documentos venían en panel OSCURO (el manifiesto, las
   diapositivas de la Junta, la portada del tablero…). Aquí, en una web clara y
   sobria, se pasan a claro: recuadro sutil, tinta oscura y el azul pizarra como
   único acento. Así nada rompe la calma de la página. */
.t-manifiesto,.slide,.slide--stmt,.tb__hero,.t-cover,.acta__cod,.deck__stage{
  background:var(--panel)!important;color:var(--tinta)!important}
.t-manifiesto{border:1px solid var(--pizarra-linea);border-radius:10px;
  padding:clamp(1.6rem,4vw,2.6rem)!important;margin:.5rem 0}
.t-manifiesto h2,.t-manifiesto p,.t-manifiesto__cierre,
.t-manifiesto__list span,.t-manifiesto__list span b,
.slide *,.tb__hero *{color:var(--tinta)!important}
.t-manifiesto h2 em,.t-manifiesto__cierre,.t-manifiesto .eyebrow,
.t-manifiesto__list>li>b{color:var(--pizarra)!important}
.t-manifiesto__list li{border-color:var(--linea)!important}
/* La Presentación es un pase de diapositivas: una sola visible cada vez con
   posición absoluta. Aquí, en una web-documento, se sueltan todas en columna,
   una debajo de otra, cada una en su recuadro. Se lee como un documento. */
.deck,.deck--sitio{height:auto!important;overflow:visible!important;position:static!important;
  display:block!important}
.slide,.slide--stmt{position:static!important;display:block!important;inset:auto!important;
  height:auto!important;min-height:0!important;
  border:1px solid var(--linea);border-radius:10px;
  padding:clamp(1.4rem,4vw,2.4rem)!important;margin:1.2rem 0!important;animation:none!important}
.slide h2{font-family:var(--serif);font-weight:400;font-size:clamp(1.5rem,3.4vw,2.2rem);
  color:var(--tinta)!important;line-height:1.12;margin:0 0 .8rem}
.slide h2 em{font-style:italic;color:var(--pizarra)!important}
thead th,.tb__e:hover{background:var(--panel-2)!important;color:var(--ink-2)!important}

@media(max-width:820px){
  .cuerpo{grid-template-columns:1fr}
  .toc{position:static;max-height:none;margin-bottom:2rem;
    border:1px solid var(--linea);border-radius:8px;padding:1.2rem;background:var(--panel)}
}
"""


def limpia(t):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", t)).strip()


def titulos_de(seccion):
    """id → título limpio, del propio índice de la sección (title="Va a: …")."""
    tit = {}
    for m in re.finditer(r'href="#([a-z0-9\-]+)"[^>]*title="Va a: ([^"]+)"', seccion):
        tit[m.group(1)] = H.unescape(m.group(2)).strip()
    return tit


def articulos(seccion):
    """(id, contenido) de cada apartado, con emparejado EQUILIBRADO de <article>.

    Los apartados llevan dentro más <article> (30 por sección): un `(.*?)</article>`
    corta en el primer cierre interno, trunca el apartado y desbarata el resto de
    la página. Aquí se cuenta la profundidad de <article> desde cada apertura de
    apartado hasta encontrar SU cierre, el que deja la profundidad a cero. """
    out = []
    for ap in re.finditer(r'<article class="hoja" id="([^"]+)"[^>]*>', seccion):
        hid, ini = ap.group(1), ap.end()
        prof = 1
        for tag in re.finditer(r'<(/?)article\b', seccion[ini:]):
            prof += -1 if tag.group(1) else 1
            if prof == 0:
                out.append((hid, seccion[ini:ini + tag.start()]))
                break
    return out


def hojas_de(seccion):
    """Los apartados de una sección: (id, contenido). Se salta la portada-doc."""
    out = []
    for hid, cont in articulos(seccion):
        if hid.endswith("portada-doc"):
            continue
        cont = re.sub(r'<p class="hoja__k">.*?</p>', "", cont, count=1, flags=re.S)
        out.append((hid, cont.strip()))
    return out


def cifras_doc(seccion):
    """Las cifras del tablero del documento, para los cuadros de cabecera."""
    port = ""
    for hid, cont in articulos(seccion):
        if hid.endswith("portada-doc"):
            port = cont
            break
    cajas = []
    for m in re.finditer(r'<div class="tb__d[^"]*">\s*<b>(.*?)</b>\s*<span>(.*?)</span>'
                         r'\s*<small>(.*?)</small>', port, re.S):
        cajas.append('<div class="docif__i"><b>%s</b><span>%s</span><small>%s</small></div>'
                     % (limpia(m.group(1)), limpia(m.group(2)), limpia(m.group(3))))
    return '<div class="docif">%s</div>' % "".join(cajas) if cajas else ""


def toc_de(seccion, hojas, titulos):
    """El índice lateral de la sección, con sus partes como subtítulos."""
    # las «partes» son enlaces del índice cuyo id empieza por «…parte»
    partes = {}
    for m in re.finditer(r'href="#([a-z0-9\-]+)"[^>]*>(?:<[^>]+>)*([^<]*Parte [^<]*)<',
                         seccion):
        partes[m.group(1)] = limpia(m.group(2))
    filas = []
    for hid, _ in hojas:
        if hid in partes:
            filas.append('<p class="toc__parte">%s</p>' % H.escape(partes[hid]))
        t = titulos.get(hid) or limpia(_)[:60] or hid
        filas.append('<a href="#%s" data-toc="%s">%s</a>' % (hid, hid, H.escape(t)))
    return "\n".join(filas)


JS = """
(function(){
  var D=document;
  var links=[].slice.call(D.querySelectorAll('.cab__l'));
  var vistas=[].slice.call(D.querySelectorAll('.vista'));
  function idDeVista(v){ return v.id.replace(/^v-/,''); }
  function ve(id, arriba){
    var hay=vistas.some(function(v){ return idDeVista(v)===id; });
    if(!hay) id='inicio';
    vistas.forEach(function(v){ v.classList.toggle('on', idDeVista(v)===id); });
    links.forEach(function(l){ l.classList.toggle('on', l.dataset.ve===id); });
    if(arriba!==false) window.scrollTo(0,0);
    try{ history.replaceState(null,'','#'+id); }catch(e){}
  }
  // ¿en qué vista vive un ancla?
  function vistaDe(id){
    var el=D.getElementById(id); if(!el) return null;
    var v=el.closest('.vista'); return v?idDeVista(v):null;
  }
  D.addEventListener('click', function(e){
    var l=e.target.closest('[data-ve]');
    if(l){ e.preventDefault(); ve(l.dataset.ve); return; }
    var a=e.target.closest('a[href^="#"]');
    if(a){
      var id=a.getAttribute('href').slice(1);
      if(!id) return;
      var dest=D.getElementById(id);
      if(!dest) return;
      var v=vistaDe(id);
      var actual=(D.querySelector('.vista.on')||{}).id;
      e.preventDefault();
      if(v && 'v-'+v!==actual){ ve(v, false); }
      requestAnimationFrame(function(){
        var d=D.getElementById(id);
        if(d) d.scrollIntoView({behavior:'smooth', block:'start'});
        try{ history.replaceState(null,'','#'+id); }catch(_){}
      });
    }
  });
  // resalta el apartado activo en el índice
  var obs;
  if('IntersectionObserver' in window){
    obs=new IntersectionObserver(function(ents){
      ents.forEach(function(en){
        if(!en.isIntersecting) return;
        var id=en.target.id;
        [].slice.call(D.querySelectorAll('.toc a')).forEach(function(x){
          x.classList.toggle('on', x.getAttribute('href')==='#'+id);
        });
      });
    }, {rootMargin:'-20% 0px -70% 0px'});
    [].slice.call(D.querySelectorAll('.wart')).forEach(function(a){ if(a.id) obs.observe(a); });
  }
  // vista inicial: por el hash, o Inicio
  var h=(location.hash||'').slice(1);
  var v0=h?vistaDe(h):null;
  ve(v0||(vistas.some(function(v){return idDeVista(v)===h;})?h:'inicio'));
  if(h){ var d=D.getElementById(h); if(d) requestAnimationFrame(function(){ d.scrollIntoView(); }); }
})();
"""


def bloque_inicio(indice, total):
    cifras = [
        ("8", "Documentos"), ("135", "Apartados"), ("14", "Fases del recorrido"),
        ("6", "Puestos con protocolo"), ("76", "Acciones de marketing"),
        ("10", "Recorridos guiados"),
    ]
    cajas = "".join('<div class="cifra"><b>%s</b><span>%s</span></div>' % c for c in cifras)
    doc_c = {i: (nombre, n) for i, _rot, nombre, n in indice}
    tarjetas = []
    for k, (sid, rot, doc, nombre) in enumerate(SECCIONES, 1):
        n = doc_c.get(sid, (nombre, 0))[1]
        _t, texto = INTRO.get(sid, ("", ""))
        pie = "%d apartados" % n if n else nombre
        tarjetas.append(
            '<a class="tarjeta" href="#%s" data-ve="%s">'
            '<span class="tarjeta__n">%02d</span>'
            '<h3>%s</h3><p>%s</p><span class="tarjeta__c">%s</span></a>'
            % (sid, sid, k, H.escape(rot), H.escape(nombre), H.escape(pie)))
    return (
        '<section class="vista" id="v-inicio">\n<div class="env">\n'
        '  <div class="whero">\n'
        '    <p class="whero__k">Centro de Excelencia Implantológica Alma</p>\n'
        '    <h1>No medias<br><em>sonrisas</em></h1>\n'
        '    <p class="whero__p">Le devolvemos su sonrisa completa, en el menor '
        'tiempo posible, y le cuidamos para siempre.</p>\n'
        '    <p class="whero__d">Calle Progreso 2 · Ourense · Uso interno y confidencial</p>\n'
        '  </div>\n'
        '  <div class="cifras">%s</div>\n'
        '  <div class="wsecs">%s</div>\n'
        '  <p class="pie">El sistema documental del centro · %d apartados en 8 documentos</p>\n'
        '</div>\n</section>' % (cajas, "".join(tarjetas), total))


def bloque_seccion(k, sid, rot, nombre, seccion):
    titulos = titulos_de(seccion)
    hojas = hojas_de(seccion)
    _t, texto = INTRO.get(sid, ("", ""))
    docif = cifras_doc(seccion)
    toc = toc_de(seccion, hojas, titulos)
    aps = []
    for hid, cont in hojas:
        t = titulos.get(hid, "")
        kic = '<p class="wart__k">%s</p>' % H.escape(t) if t else ""
        aps.append('<article class="wart" id="%s">%s\n%s</article>' % (hid, kic, cont))
    return (
        '<section class="vista" id="v-%s">\n<div class="env">\n'
        '  <header class="sh">\n'
        '    <p class="sh__n">%02d · %s</p>\n'
        '    <h1>%s</h1>\n'
        '    <p class="sh__p">%s</p>\n'
        '  </header>\n'
        '  %s\n'
        '  <div class="cuerpo">\n'
        '    <nav class="toc" aria-label="Apartados de la sección">'
        '<p class="toc__t">En esta sección</p>%s</nav>\n'
        '    <div class="wlista">%s</div>\n'
        '  </div>\n'
        '</div>\n</section>'
        % (sid, k, H.escape(nombre), H.escape(rot), H.escape(texto),
           docif, toc, "\n".join(aps)))


def main():
    secciones, menus, indice, orden, voces, mapa = bs.monta()
    total = len(orden)

    nav = '<a class="cab__l" href="#inicio" data-ve="inicio">Inicio</a>' + "".join(
        '<a class="cab__l" href="#%s" data-ve="%s">%s</a>' % (sid, sid, H.escape(rot))
        for sid, rot, _d, _n in SECCIONES)

    vistas = [bloque_inicio(indice, total)]
    for k, (sid, rot, doc, nombre) in enumerate(SECCIONES, 1):
        # monta() devuelve las secciones en el orden de SECCIONES
        vistas.append(bloque_seccion(k, sid, rot, nombre, secciones[k - 1]))

    estilo = ("<style>%s</style>\n<style>%s\n%s\n%s</style>"
              % (css_documentos(), fuentes_incrustadas(), TEMA, SHELL))

    doc = (
        '<!doctype html>\n<html lang="es">\n<head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<title>Alma · Centro de Excelencia Implantológica</title>\n'
        '%s\n%s\n</head>\n<body>\n'
        '<header class="cab">\n'
        '  <a class="cab__m" href="#inicio" data-ve="inicio">Alma</a>\n'
        '  <nav class="cab__nav" aria-label="Secciones">%s</nav>\n'
        '</header>\n'
        '<main>\n%s\n</main>\n'
        '<script>%s</script>\n'
        '</body>\n</html>\n'
        % (fuentes_archivo(), estilo, nav, "\n".join(vistas), JS))

    salida = RAIZ / "web.html"
    salida.write_text(doc, encoding="utf-8")
    print("web.html · %d secciones · %d apartados · %d KB"
          % (len(SECCIONES), total, len(doc.encode("utf-8")) // 1024))


if __name__ == "__main__":
    main()
