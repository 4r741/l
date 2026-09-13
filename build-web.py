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

# El viaje del paciente: las catorce fases, de la llamada al mantenimiento. Es
# el mapa que se sigue. Las doce primeras suman 123 minutos —la primera visita
# entera—; las dos últimas son el después. Cada parada lleva a su sección.
FASES = [
    ("01", "Preparación", "6 min", "primera-visita"),
    ("02", "Acogida", "5 min", "primera-visita"),
    ("03", "Alta y RGPD", "15 min", "primera-visita"),
    ("04", "Historia clínica", "10 min", "primera-visita"),
    ("05", "Diagnóstico", "15 min", "primera-visita"),
    ("06", "Briefing", "5 min", "primera-visita"),
    ("07", "Expectativas", "15 min", "primera-visita"),
    ("08", "IAC", "10 min", "primera-visita"),
    ("09", "Presentación 3D", "15 min", "primera-visita"),
    ("10", "Propuesta", "20 min", "primera-visita"),
    ("11", "Cierre admin.", "5 min", "primera-visita"),
    ("12", "Seguimiento", "2 min", "primera-visita"),
    ("13", "Circuito de producción", "el después", "operaciones"),
    ("14", "Mantenimiento", "el después", "operaciones"),
]

# El sistema, colgado del lema: cuatro preguntas y, bajo cada una, los
# documentos que la contestan. Es el mapa del conjunto.
SISTEMA = [
    ("Qué se promete", "La posición, la economía y la decisión",
     ["direccion", "presentacion"]),
    ("Cómo se hace", "El recorrido del paciente y quién responde",
     ["primera-visita", "protocolos"]),
    ("Cómo llega el paciente", "Lo que se hace para que entre por la puerta",
     ["marketing"]),
    ("Con qué se mide", "Sin números, cualquier objetivo es una opinión",
     ["numeros", "otros"]),
]


# El logo de Clínica Alma, recreado como SVG a partir del original que envió el
# cliente (el archivo no viajaba como fichero incrustable): el emblema —un
# diente entre hojas, sobre el cuenco de una sonrisa— en azul pizarra. Viaja
# dentro del propio archivo, sin pedir nada a la red. Si hace falta fidelidad
# exacta, se sustituye por el SVG original en un único sitio.
LOGO_EMBLEMA = (
    '<svg class="marca__e" viewBox="0 0 128 118" fill="none" stroke="currentColor" '
    'stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<path d="M52 14 C47 6 39 7 38 17 C37 30 40 44 43 62 C44 72 50 78 53 68 '
    'C56 60 57 50 58 42 C59 50 60 60 63 68 C66 78 72 72 73 62 C76 44 79 30 78 17 '
    'C77 7 69 6 64 14 C61 19 55 19 52 14 Z"/>'
    '<path d="M44 54 C30 50 15 55 9 70 C24 76 40 71 46 58"/>'
    '<path d="M40 74 C28 74 17 69 12 60"/>'
    '<path d="M72 54 C86 50 101 55 107 70 C92 76 76 71 70 58"/>'
    '<path d="M76 74 C88 74 99 69 104 60"/>'
    '<path d="M20 78 C40 106 76 106 96 78"/></svg>')

LOGO_FAVICON = (
    "data:image/svg+xml;utf8,"
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 128 118' fill='none' "
    "stroke='%2322405C' stroke-width='4' stroke-linecap='round' stroke-linejoin='round'>"
    "<path d='M52 14 C47 6 39 7 38 17 C37 30 40 44 43 62 C44 72 50 78 53 68 "
    "C56 60 57 50 58 42 C59 50 60 60 63 68 C66 78 72 72 73 62 C76 44 79 30 78 17 "
    "C77 7 69 6 64 14 C61 19 55 19 52 14 Z'/>"
    "<path d='M44 54 C30 50 15 55 9 70 C24 76 40 71 46 58'/>"
    "<path d='M72 54 C86 50 101 55 107 70 C92 76 76 71 70 58'/>"
    "<path d='M20 78 C40 106 76 106 96 78'/></svg>")


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
  D.documentElement.classList.add('js');
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
  // barra de progreso de lectura
  var prog=D.getElementById('prog');
  function pintaProg(){
    var e=D.documentElement, max=e.scrollHeight-e.clientHeight;
    if(prog) prog.style.width=(max>0?(e.scrollTop/max*100):0)+'%';
  }
  window.addEventListener('scroll', pintaProg, {passive:true});
  window.addEventListener('resize', pintaProg);
  // revelado al bajar: cada bloque entra una vez
  var rev=null;
  if('IntersectionObserver' in window){
    rev=new IntersectionObserver(function(es){
      es.forEach(function(e){ if(e.isIntersecting){ e.target.classList.add('visto'); rev.unobserve(e.target); } });
    }, {rootMargin:'0px 0px -8% 0px'});
    [].slice.call(D.querySelectorAll('.reveal')).forEach(function(x){ rev.observe(x); });
  } else {
    [].slice.call(D.querySelectorAll('.reveal')).forEach(function(x){ x.classList.add('visto'); });
  }
  // vista inicial: por el hash, o Inicio
  var h=(location.hash||'').slice(1);
  var v0=h?vistaDe(h):null;
  ve(v0||(vistas.some(function(v){return idDeVista(v)===h;})?h:'inicio'));
  if(h){ var d=D.getElementById(h); if(d) requestAnimationFrame(function(){ d.scrollIntoView(); }); }
  pintaProg();
})();
"""


def _meta(indice):
    """sid → (rótulo, nombre del documento, nº de apartados, orden)."""
    cuenta = {i: (rot, nombre, n) for i, rot, nombre, n in indice}
    m = {}
    for k, (sid, rot, doc, nombre) in enumerate(SECCIONES, 1):
        rr, nn, n = cuenta.get(sid, (rot, nombre, 0))
        m[sid] = (rot, nombre, n, k)
    return m


def fase_ancla(num):
    """El ancla de una fase dentro de la página: las doce primeras viven en
    Primera Visita (d-f01…d-f12); las dos últimas, en Operaciones."""
    return ("d-f%s" % num) if int(num) <= 12 else ("e-m%s" % int(num))


def banda_lema():
    """Una franja a sangre, en pizarra pleno y con la tipografía gigante: la
    línea que ordena todo el sistema. El golpe de contraste del inicio."""
    return (
        '<section class="banda">'
        '<div class="env">'
        '<p class="banda__k reveal">El criterio</p>'
        '<p class="banda__t reveal">Media sonrisa es la que se hace '
        '<em>a medias</em>: el corte que nadie ve y el paciente sí nota.</p>'
        '</div></section>')


def camino_seccion():
    """El mapa del viaje, compacto y dentro de Primera Visita: las doce fases de
    la primera visita como pasos que se pulsan para bajar a cada una, más las
    dos del después. Es «el camino que seguir» en su propia casa."""
    pasos = []
    for num, nombre, minu, sid in FASES:
        anc = fase_ancla(num)
        fuera = ' data-ve="operaciones"' if int(num) > 12 else ""
        pasos.append(
            '<a class="hito reveal" href="#%s"%s>'
            '<span class="hito__n">%s</span>'
            '<span class="hito__t">%s</span>'
            '<span class="hito__m">%s</span></a>'
            % (anc, fuera, num, H.escape(nombre), H.escape(minu)))
    return (
        '<section class="franja franja--oscura" id="camino-visita">'
        '<div class="env">'
        '<header class="titmapa titmapa--claro reveal">'
        '<p class="titmapa__k">El camino · 123 minutos</p>'
        '<h2>Siga la primera visita, fase a fase</h2>'
        '<p class="titmapa__p">Doce fases hasta la propuesta, y dos más para el '
        'después. Pulse una para bajar a su detalle.</p></header>'
        '<div class="hitos">%s</div>'
        '</div></section>' % "".join(pasos))


def cuenta_txt(sid, n, nombre):
    """El pie de cada documento: apartados, o su unidad propia."""
    if sid == "presentacion":
        return "43 diapositivas"
    if n == 1:
        return "1 apartado"
    if n:
        return "%d apartados" % n
    return nombre


def mapa_sistema(meta):
    """Mapa 1 · El sistema, colgado del lema: cuatro preguntas y sus documentos."""
    ramas = []
    for qi, (preg, sub, sids) in enumerate(SISTEMA, 1):
        nodos = []
        for sid in sids:
            rot, nombre, n, k = meta[sid]
            pie = cuenta_txt(sid, n, nombre)
            nodos.append(
                '<a class="ram__d" href="#%s" data-ve="%s">'
                '<span class="ram__n">%02d</span>'
                '<b>%s</b><span class="ram__c">%s</span></a>'
                % (sid, sid, k, H.escape(rot), H.escape(pie)))
        ramas.append(
            '<div class="rama reveal">'
            '<p class="rama__q"><i>%02d</i>%s</p>'
            '<p class="rama__s">%s</p>'
            '<div class="rama__docs">%s</div></div>'
            % (qi, H.escape(preg), H.escape(sub), "".join(nodos)))
    return (
        '<section class="franja" id="mapa-sistema">'
        '<div class="env">'
        '<header class="titmapa reveal">'
        '<p class="titmapa__k">Mapa 01 · El sistema</p>'
        '<h2>Todo cuelga de una frase</h2>'
        '<p class="titmapa__p">«No medias sonrisas» no es un eslogan: es el '
        'criterio. De él salen cuatro preguntas, y cada documento contesta una.</p>'
        '</header>'
        '<div class="lema reveal"><span>No medias</span> <em>sonrisas</em></div>'
        '<div class="ramas">%s</div>'
        '</div></section>' % "".join(ramas))


def mapa_viaje(meta):
    """Mapa 2 · El viaje del paciente: las catorce fases, en franja oscura, como
    un camino que se sigue paso a paso. Cada parada lleva a su sección."""
    pasos = []
    for num, nombre, minu, sid in FASES:
        rot = meta[sid][0]
        pasos.append(
            '<a class="paso reveal" href="#%s" data-ve="%s">'
            '<span class="paso__n">%s</span>'
            '<span class="paso__cuerpo"><b>%s</b>'
            '<span class="paso__min">%s</span></span>'
            '<span class="paso__sec">%s →</span></a>'
            % (sid, sid, num, H.escape(nombre), H.escape(minu), H.escape(rot)))
    return (
        '<section class="franja franja--oscura" id="mapa-viaje">'
        '<div class="env">'
        '<header class="titmapa titmapa--claro reveal">'
        '<p class="titmapa__k">Mapa 02 · El viaje del paciente</p>'
        '<h2>De la primera llamada<br>al mantenimiento</h2>'
        '<p class="titmapa__p">Catorce fases. Las doce primeras —la primera '
        'visita entera— caben en <b>123 minutos</b>. Siga el camino: cada '
        'parada dice qué pasa y le lleva a donde se detalla.</p>'
        '</header>'
        '<div class="camino">%s</div>'
        '</div></section>' % "".join(pasos))


def mapa_ruta(meta, total):
    """Mapa 3 · La ruta de lectura: las ocho secciones en orden, para seguirlas
    una tras otra. Es también el índice grande del inicio."""
    filas = []
    for sid, rot, doc, nombre in SECCIONES:
        _rr, _nn, n, k = meta[sid]
        pie = cuenta_txt(sid, n, nombre)
        filas.append(
            '<a class="ruta__i reveal" href="#%s" data-ve="%s">'
            '<span class="ruta__n">%02d</span>'
            '<span class="ruta__t"><b>%s</b><span>%s</span></span>'
            '<span class="ruta__c">%s</span>'
            '<span class="ruta__f">→</span></a>'
            % (sid, sid, k, H.escape(rot), H.escape(nombre), H.escape(pie)))
    return (
        '<section class="franja" id="mapa-ruta">'
        '<div class="env">'
        '<header class="titmapa reveal">'
        '<p class="titmapa__k">Mapa 03 · La ruta de lectura</p>'
        '<h2>Ocho paradas, en orden</h2>'
        '<p class="titmapa__p">Si prefiere leerlo entero, este es el orden. '
        'De la posición del centro a los números que lo miden.</p>'
        '</header>'
        '<div class="ruta">%s</div>'
        '<p class="pie">El sistema documental del centro · %d apartados en 8 documentos · '
        'Calle Progreso 2 · Ourense</p>'
        '</div></section>' % ("".join(filas), total))


def bloque_inicio(indice, total):
    meta = _meta(indice)
    cifras = [
        ("8", "Documentos"), ("135", "Apartados"), ("14", "Fases"),
        ("6", "Puestos"), ("76", "Acciones"), ("123′", "La primera visita"),
    ]
    cajas = "".join('<div class="cifra"><b>%s</b><span>%s</span></div>' % c for c in cifras)
    hero = (
        '<section class="hero2">'
        '<div class="env">'
        '<p class="hero2__k">Centro de Excelencia Implantológica Alma · Ourense</p>'
        '<h1 class="hero2__t">No medias<br><em>sonrisas</em></h1>'
        '<p class="hero2__p">Le devolvemos su sonrisa completa, en el menor tiempo '
        'posible, y le cuidamos para siempre. Todo el sistema del centro, en un mapa '
        'que se sigue.</p>'
        '<div class="cifras cifras--hero">%s</div>'
        '<a class="hero2__baja" href="#mapa-sistema">Seguir el mapa <i>↓</i></a>'
        '</div></section>' % cajas)
    return (
        '<section class="vista" id="v-inicio">\n'
        + hero + banda_lema() + mapa_sistema(meta) + mapa_viaje(meta)
        + mapa_ruta(meta, total) + '\n</section>')


def bloque_experiencia():
    """La capa que faltaba: la literatura de la EXPERIENCIA, en la voz de Alma.

    El resto del sistema dice cómo se hace; esto dice por qué se siente distinto.
    Todo se apoya en lo que ya es cierto en el sistema —los 123 minutos medidos,
    las catorce fases, los seis puestos, el manifiesto, Alma Te Cuida— y lo eleva.
    Nada de datos inventados: la promesa es la que el propio sistema sostiene. """
    principios = [
        ("01", "El tiempo", "123 minutos", "primera-visita",
         "La prisa es la primera causa de una media sonrisa. Por eso su primera "
         "visita dura lo que tiene que durar: ciento veintitrés minutos medidos, "
         "fase a fase, no estimados. Sale usted con un diagnóstico en la mano, su "
         "caso en tres dimensiones y una decisión que puede tomar con calma."),
        ("02", "La claridad", "Todo por escrito", "direccion",
         "Lo que no está escrito no existe. Cada estándar de Alma puede "
         "comprobarse en una lista; cada decisión lleva fecha y responsable. No "
         "prometemos: dejamos constancia. Es la diferencia entre una intención y "
         "un compromiso —y lo que no se explica, no se firma—."),
        ("03", "La precisión", "El plan es lo que se coloca", "primera-visita",
         "Imagen de alta resolución, planificación digital y presentación en tres "
         "dimensiones: la tecnología no está para impresionar, sino para que usted "
         "vea su propio caso antes de decidir, y para que lo que se planifica sea "
         "exactamente lo que se coloca."),
        ("04", "La continuidad", "Seis puestos, un criterio", "protocolos",
         "De la primera llamada al mantenimiento, cada persona que le atiende sabe "
         "qué le toca y de qué responde. Usted no repite su historia en cada "
         "visita: el sistema la lleva por usted, y el testigo pasa de mano en mano "
         "sin que se caiga nada por el camino."),
        ("05", "El cuidado", "Alma Te Cuida", "otros",
         "El tratamiento no termina cuando se coloca el implante: termina —y no "
         "termina nunca— cuando usted deja de pensar en él. Alma Te Cuida es el "
         "programa que sostiene lo tratado, detecta pronto lo que se tuerce y "
         "mantiene la relación año tras año."),
    ]
    tarjetas = []
    for num, tit, cifra, sid, texto in principios:
        tarjetas.append(
            '<a class="prin reveal" href="#%s" data-ve="%s">'
            '<span class="prin__n">%s</span>'
            '<div class="prin__c"><p class="prin__k">%s</p>'
            '<p class="prin__cifra">%s</p>'
            '<p class="prin__t">%s</p>'
            '<span class="prin__ir">Ver en el sistema →</span></div></a>'
            % (sid, sid, num, H.escape(tit), H.escape(cifra), H.escape(texto)))
    return (
        '<section class="vista" id="v-experiencia">\n'
        # apertura: la filosofía, a sangre y en grande
        '<section class="hero2 hero2--exp"><div class="env">'
        '<p class="hero2__k reveal">La experiencia · Lo que se siente, no solo lo que se hace</p>'
        '<h1 class="hero2__t reveal">Una sonrisa no es<br>un trabajo terminado:<br>'
        '<em>es una persona.</em></h1>'
        '<p class="hero2__p reveal">Es alguien que vuelve a reír sin taparse la boca. '
        'En Alma no entendemos la excelencia como una máquina más cara ni un '
        'material más nuevo, sino como la mitad del trabajo que nadie ve —y que '
        'el paciente sí nota—. Esa mitad invisible es la única que ningún '
        'competidor puede comprar.</p>'
        '</div></section>'
        # los cinco principios de la experiencia
        '<section class="franja"><div class="env">'
        '<header class="titmapa reveal">'
        '<p class="titmapa__k">Cinco maneras de notarlo</p>'
        '<h2>Lo que cambia, para usted</h2>'
        '<p class="titmapa__p">Cinco promesas que el sistema entero está montado '
        'para cumplir. Cada una lleva a donde se detalla, por escrito.</p></header>'
        '<div class="prins">%s</div>'
        '</div></section>'
        # el cierre, en pizarra pleno
        '<section class="banda"><div class="env">'
        '<p class="banda__k reveal">La promesa</p>'
        '<p class="banda__t reveal">No medias sonrisas.<br><em>Ni medias '
        'decisiones.</em></p>'
        '<p class="banda__p reveal">Le devolvemos su sonrisa completa, en el menor '
        'tiempo posible, y le cuidamos para siempre.</p>'
        '</div></section>'
        '\n</section>' % "".join(tarjetas))


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

    # La ruta de lectura: la parada anterior y la siguiente, para seguir el mapa
    # sin volver al inicio. (k va de 1 a 8 sobre SECCIONES.)
    n_sec = len(SECCIONES)
    prev_l = next_l = ""
    if k > 1:
        p_sid, p_rot, _d, _n = SECCIONES[k - 2]
        prev_l = ('<a class="salta salta--ant" href="#%s" data-ve="%s">'
                  '<span class="salta__d">← Anterior</span>'
                  '<b>%02d · %s</b></a>' % (p_sid, p_sid, k - 1, H.escape(p_rot)))
    if k < n_sec:
        x_sid, x_rot, _d, _n = SECCIONES[k]
        next_l = ('<a class="salta salta--sig" href="#%s" data-ve="%s">'
                  '<span class="salta__d">Siguiente →</span>'
                  '<b>%02d · %s</b></a>' % (x_sid, x_sid, k + 1, H.escape(x_rot)))
    ruta = ('<nav class="salta-nav" aria-label="Ruta de lectura">%s%s</nav>'
            % (prev_l, next_l))

    camino = camino_seccion() if sid == "primera-visita" else ""

    return (
        '<section class="vista" id="v-%s">\n'
        '  <header class="sh reveal">\n<div class="env">\n'
        '    <p class="sh__n">Sección %02d <i>de %02d</i> · %s</p>\n'
        '    <h1>%s</h1>\n'
        '    <p class="sh__p">%s</p>\n'
        '  </div></header>\n'
        '  %s\n'
        '  <div class="env">\n'
        '  %s\n'
        '  <div class="cuerpo">\n'
        '    <nav class="toc" aria-label="Apartados de la sección">'
        '<p class="toc__t">En esta sección</p>%s</nav>\n'
        '    <div class="wlista">%s</div>\n'
        '  </div>\n'
        '  %s\n'
        '  </div>\n</section>'
        % (sid, k, n_sec, H.escape(nombre), H.escape(rot), H.escape(texto),
           camino, docif, toc, "\n".join(aps), ruta))


BOLD = """
/* ==================== La piel atrevida ====================
   Sobre la base blanca y azul pizarra: hero a pantalla, franjas a sangre —una
   oscura de pizarra pleno—, tipografía a gran escala, un mapa que se sigue y
   revelado al desplazar. La disrupción, sin perder la calma profesional. */

.cab__prog{position:absolute;left:0;bottom:-1px;height:2px;width:0;
  background:var(--pizarra);transition:width .12s linear}

/* Revelado: visible por defecto (sin JS no se esconde nada); con JS entra al bajar */
html.js .reveal{opacity:0;transform:translateY(1.4rem);
  transition:opacity .7s cubic-bezier(.22,.61,.36,1),transform .7s cubic-bezier(.22,.61,.36,1)}
html.js .reveal.visto{opacity:1;transform:none}
@media(prefers-reduced-motion:reduce){html.js .reveal{opacity:1;transform:none;transition:none}}

/* Hero a pantalla */
.hero2{min-height:calc(100svh - var(--nav));display:flex;align-items:center;
  border-bottom:1px solid var(--linea)}
.hero2 .env{width:100%;padding-top:clamp(2rem,6vh,4rem);padding-bottom:clamp(2rem,6vh,4rem)}
.hero2__k{font-family:var(--mono);font-size:.7rem;letter-spacing:.2em;
  text-transform:uppercase;color:var(--muted);margin:0 0 1.6rem}
.hero2__t{font-family:var(--serif);font-weight:400;
  font-size:clamp(3.2rem,13vw,9rem);line-height:.88;letter-spacing:-.01em;margin:0;color:var(--tinta)}
.hero2__t em{font-style:italic;color:var(--pizarra);display:block}
.hero2__p{font-size:clamp(1.1rem,2.2vw,1.45rem);max-width:42ch;line-height:1.5;
  color:var(--ink-2);margin:2rem 0 0}
.hero2__baja{display:inline-flex;align-items:center;gap:.6rem;margin-top:2.4rem;
  font-family:var(--mono);font-size:.7rem;letter-spacing:.14em;text-transform:uppercase;
  color:var(--pizarra);text-decoration:none;border:1px solid var(--pizarra-linea);
  border-radius:100px;padding:.7rem 1.3rem;transition:background .2s,color .2s}
.hero2__baja:hover{background:var(--pizarra);color:#fff}
.hero2__baja i{font-style:normal;animation:baja 1.6s infinite}
@keyframes baja{0%,100%{transform:translateY(0)}50%{transform:translateY(4px)}}
.cifras--hero{margin-top:3rem}

/* Franjas a sangre */
.franja{padding:clamp(3.4rem,10vh,7rem) 0;border-bottom:1px solid var(--linea)}
.franja--oscura{background:var(--pizarra-fuerte);color:#EAF0F6;border-bottom:0}
.titmapa{max-width:46ch;margin-bottom:clamp(2.4rem,6vh,4rem)}
.titmapa__k{font-family:var(--mono);font-size:.68rem;letter-spacing:.18em;
  text-transform:uppercase;color:var(--pizarra);margin:0 0 1rem}
.titmapa--claro .titmapa__k{color:#9DBBD8}
.titmapa h2{font-family:var(--serif);font-weight:400;
  font-size:clamp(2.2rem,6vw,4.2rem);line-height:1.02;letter-spacing:-.01em;margin:0;color:var(--tinta)}
.titmapa--claro h2{color:#fff}
.titmapa__p{font-size:1.1rem;line-height:1.55;margin:1.4rem 0 0;color:var(--ink-2)}
.titmapa--claro .titmapa__p{color:#B9C7D6}
.titmapa__p b{font-weight:700;color:inherit}

/* Mapa 1 · el sistema */
.lema{font-family:var(--serif);font-size:clamp(2rem,6vw,3.6rem);text-align:center;
  margin:0 0 3rem;line-height:1}
.lema span{color:var(--tinta)}.lema em{font-style:italic;color:var(--pizarra)}
.ramas{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:1px;
  background:var(--linea);border:1px solid var(--linea)}
.rama{background:var(--panel);padding:1.8rem 1.6rem;display:flex;flex-direction:column;gap:.4rem}
.rama__q{font-family:var(--serif);font-size:1.45rem;color:var(--tinta);margin:0;
  display:flex;gap:.7rem;align-items:baseline;line-height:1.1}
.rama__q i{font-family:var(--mono);font-size:.78rem;font-style:normal;color:var(--pizarra)}
.rama__s{font-size:.88rem;color:var(--muted);margin:0 0 .9rem}
.rama__docs{display:flex;flex-direction:column;gap:.5rem;margin-top:auto}
.ram__d{display:flex;align-items:baseline;gap:.7rem;text-decoration:none;color:var(--tinta);
  padding:.7rem .9rem;border:1px solid var(--linea);border-radius:8px;
  transition:border-color .18s,background .18s,transform .18s}
.ram__d:hover{border-color:var(--pizarra);background:var(--pizarra-soft);transform:translateX(3px)}
.ram__n{font-family:var(--mono);font-size:.64rem;color:var(--pizarra)}
.ram__d b{font-weight:600;flex:1}
.ram__c{font-family:var(--mono);font-size:.58rem;color:var(--muted);text-transform:uppercase}

/* Mapa 2 · el camino del paciente */
.camino{position:relative;display:flex;flex-direction:column}
.camino::before{content:"";position:absolute;
  left:calc(clamp(2.4rem,6vw,3.6rem) / 2 + 1.4rem);top:2rem;bottom:2rem;width:2px;
  background:rgba(157,187,216,.25)}
.paso{position:relative;display:grid;
  grid-template-columns:clamp(2.4rem,6vw,3.6rem) 1fr auto;gap:clamp(1rem,3vw,2rem);
  align-items:center;padding:.95rem 1.4rem;text-decoration:none;border-radius:12px;
  transition:background .18s}
.paso:hover{background:rgba(255,255,255,.05)}
.paso__n{font-family:var(--serif);font-size:clamp(1.4rem,3.4vw,2.2rem);color:#fff;
  width:clamp(2.4rem,6vw,3.6rem);height:clamp(2.4rem,6vw,3.6rem);flex:none;
  display:grid;place-items:center;border-radius:50%;position:relative;z-index:1;
  background:var(--pizarra);box-shadow:0 0 0 6px var(--pizarra-fuerte)}
.paso__cuerpo{display:flex;flex-direction:column;gap:.15rem;min-width:0}
.paso__cuerpo b{font-family:var(--serif);font-weight:400;font-size:clamp(1.1rem,2.4vw,1.6rem);
  color:#fff;line-height:1.1}
.paso__min{font-family:var(--mono);font-size:.6rem;letter-spacing:.1em;text-transform:uppercase;color:#9DBBD8}
.paso__sec{font-family:var(--mono);font-size:.58rem;letter-spacing:.08em;text-transform:uppercase;
  color:#7E9AB8;white-space:nowrap}
.paso:hover .paso__sec{color:#EAF0F6}

/* Mapa 3 · la ruta de lectura */
.ruta{border:1px solid var(--linea);border-radius:14px;overflow:hidden;background:var(--panel)}
.ruta__i{display:grid;grid-template-columns:auto 1fr auto auto;gap:1.2rem;align-items:center;
  padding:1.3rem 1.6rem;text-decoration:none;color:var(--tinta);
  border-bottom:1px solid var(--linea);transition:background .18s}
.ruta__i:last-child{border-bottom:0}
.ruta__i:hover{background:var(--pizarra-soft)}
.ruta__n{font-family:var(--serif);font-size:1.7rem;color:var(--pizarra);width:2.4rem;text-align:center}
.ruta__t{display:flex;flex-direction:column}
.ruta__t b{font-family:var(--serif);font-weight:400;font-size:1.35rem;color:var(--tinta)}
.ruta__t span{font-size:.84rem;color:var(--muted)}
.ruta__c{font-family:var(--mono);font-size:.58rem;color:var(--muted);text-transform:uppercase;letter-spacing:.06em}
.ruta__f{font-size:1.2rem;color:var(--pizarra);transition:transform .18s}
.ruta__i:hover .ruta__f{transform:translateX(4px)}

/* Cabecera de sección, a sangre en pizarra suave */
.sh{background:var(--pizarra-soft);border-bottom:1px solid var(--pizarra-linea);border-top:0;
  margin-bottom:0;padding:clamp(2.4rem,7vh,4.5rem) 0 clamp(2rem,5vh,3.2rem)}
.sh .env{padding-top:0;padding-bottom:0}
.sh__n i{font-style:normal;color:var(--muted)}
.sh h1{font-size:clamp(2.4rem,6vw,4rem)}

/* Ruta de lectura al pie de sección */
.salta-nav{display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-top:3.5rem;
  border-top:1px solid var(--linea);padding-top:2rem}
.salta{display:flex;flex-direction:column;gap:.4rem;text-decoration:none;
  border:1px solid var(--linea);border-radius:12px;padding:1.2rem 1.4rem;
  transition:border-color .18s,background .18s}
.salta--ant{grid-column:1}
.salta--sig{grid-column:2;text-align:right}
.salta:hover{border-color:var(--pizarra);background:var(--pizarra-soft)}
.salta__d{font-family:var(--mono);font-size:.6rem;letter-spacing:.12em;text-transform:uppercase;color:var(--pizarra)}
.salta b{font-family:var(--serif);font-weight:400;font-size:1.25rem;color:var(--tinta)}

/* Banda a sangre con el criterio, en pizarra pleno y tipografía gigante */
.banda{background:var(--pizarra-fuerte);color:#EAF0F6;
  padding:clamp(3.5rem,12vh,8rem) 0}
.banda__k{font-family:var(--mono);font-size:.7rem;letter-spacing:.2em;
  text-transform:uppercase;color:#9DBBD8;margin:0 0 1.6rem}
.banda__t{font-family:var(--serif);font-weight:400;
  font-size:clamp(2rem,6.5vw,4.6rem);line-height:1.05;letter-spacing:-.01em;
  color:#fff;margin:0;max-width:22ch}
.banda__t em{font-style:italic;color:#B9D0E6}

/* El camino compacto dentro de Primera Visita */
.hitos{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:1px;
  background:rgba(157,187,216,.18);border:1px solid rgba(157,187,216,.18)}
.hito{display:flex;flex-direction:column;gap:.25rem;padding:1.1rem 1.1rem;
  text-decoration:none;background:var(--pizarra-fuerte);transition:background .18s}
.hito:hover{background:rgba(255,255,255,.06)}
.hito__n{font-family:var(--serif);font-size:1.6rem;color:#fff;line-height:1}
.hito__t{font-size:.9rem;color:#EAF0F6;font-weight:600;line-height:1.2}
.hito__m{font-family:var(--mono);font-size:.56rem;letter-spacing:.08em;
  text-transform:uppercase;color:#9DBBD8}

/* El logo en la cabecera */
.marca{display:inline-flex;align-items:center;gap:.6rem;color:var(--pizarra);text-decoration:none}
.marca__e{width:1.9rem;height:1.75rem;flex:none;color:var(--pizarra)}
.marca__t{font-family:var(--serif);font-size:1.25rem;letter-spacing:.02em;
  color:var(--tinta);white-space:nowrap;line-height:1}

/* La experiencia · la capa premium */
.hero2--exp{border-bottom:0}
.hero2--exp .hero2__t{font-size:clamp(2.4rem,7vw,5.2rem)}
.banda__p{font-size:1.15rem;line-height:1.5;color:#B9C7D6;margin:1.6rem 0 0;max-width:44ch}
.prins{display:grid;gap:1px;background:var(--linea);border:1px solid var(--linea);border-radius:14px;overflow:hidden}
.prin{display:grid;grid-template-columns:auto 1fr;gap:clamp(1rem,3vw,2.4rem);
  background:var(--panel);padding:clamp(1.6rem,3.5vw,2.6rem);text-decoration:none;
  color:var(--tinta);transition:background .18s}
.prin:hover{background:var(--pizarra-soft)}
.prin__n{font-family:var(--serif);font-size:clamp(1.6rem,4vw,2.6rem);color:var(--pizarra);line-height:1}
.prin__k{font-family:var(--mono);font-size:.62rem;letter-spacing:.14em;text-transform:uppercase;
  color:var(--muted);margin:0 0 .5rem}
.prin__cifra{font-family:var(--serif);font-weight:400;font-size:clamp(1.5rem,3.5vw,2.2rem);
  color:var(--tinta);margin:0 0 .8rem;line-height:1.05}
.prin__t{font-size:1.02rem;line-height:1.6;color:var(--ink-2);margin:0;max-width:62ch}
.prin__ir{display:inline-block;margin-top:1rem;font-family:var(--mono);font-size:.6rem;
  letter-spacing:.1em;text-transform:uppercase;color:var(--pizarra)}

@media(max-width:640px){
  .ruta__i{grid-template-columns:auto 1fr auto}
  .ruta__c{display:none}
  .salta-nav{grid-template-columns:1fr}
  .salta--ant,.salta--sig{grid-column:1;text-align:left}
  .marca__t{display:none}
}
@media(max-width:560px){.prin{grid-template-columns:1fr}}
"""


def main():
    secciones, menus, indice, orden, voces, mapa = bs.monta()
    total = len(orden)

    nav = ('<a class="cab__l" href="#inicio" data-ve="inicio">Inicio</a>'
           '<a class="cab__l" href="#experiencia" data-ve="experiencia">La experiencia</a>'
           + "".join(
               '<a class="cab__l" href="#%s" data-ve="%s">%s</a>' % (sid, sid, H.escape(rot))
               for sid, rot, _d, _n in SECCIONES))

    vistas = [bloque_inicio(indice, total), bloque_experiencia()]
    for k, (sid, rot, doc, nombre) in enumerate(SECCIONES, 1):
        # monta() devuelve las secciones en el orden de SECCIONES
        vistas.append(bloque_seccion(k, sid, rot, nombre, secciones[k - 1]))

    estilo = ("<style>%s</style>\n<style>%s\n%s\n%s\n%s</style>"
              % (css_documentos(), fuentes_incrustadas(), TEMA, SHELL, BOLD))

    # Se arma por trozos (sin %-format) para no chocar con el «%» del favicon
    # ni con las llaves del SVG del logo.
    cabecera = (
        '<a class="cab__m marca" href="#inicio" data-ve="inicio" '
        'aria-label="Clínica Alma · inicio">' + LOGO_EMBLEMA
        + '<span class="marca__t">Clínica Alma</span></a>')

    doc = (
        '<!doctype html>\n<html lang="es">\n<head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<title>Clínica Alma · Centro de Excelencia Implantológica</title>\n'
        '<link rel="icon" href="' + LOGO_FAVICON + '">\n'
        + fuentes_archivo() + '\n' + estilo + '\n</head>\n<body>\n'
        '<header class="cab">\n  ' + cabecera + '\n'
        '  <nav class="cab__nav" aria-label="Secciones">' + nav + '</nav>\n'
        '  <div class="cab__prog" id="prog" aria-hidden="true"></div>\n'
        '</header>\n'
        '<main>\n' + "\n".join(vistas) + '\n</main>\n'
        '<script>' + JS + '</script>\n'
        '</body>\n</html>\n')

    salida = RAIZ / "web.html"
    salida.write_text(doc, encoding="utf-8")
    print("web.html · %d secciones · %d apartados · %d KB"
          % (len(SECCIONES), total, len(doc.encode("utf-8")) // 1024))


if __name__ == "__main__":
    main()
