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
import json

RAIZ = pathlib.Path(__file__).parent

# ---------------------------------------------------------------- el contenido
# Se carga el generador de siempre como módulo (el guion lleva guion en el
# nombre y no se puede importar a secas) y se le pide lo único que interesa: el
# contenido cosechado de los ocho documentos.
_spec = importlib.util.spec_from_file_location("bs", str(RAIZ / "build-sitio.py"))
bs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bs)

# El orden de MENÚ. Primera Visita va primera —es el corazón del sistema— y el
# resto sigue el orden documental. Su posición aquí manda la numeración
# («Sección 01 de 08»), la ruta de lectura y el orden de las vistas.
SECCIONES = [
    ("primera-visita", "Primera Visita", "index.html", "Protocolo de Primera Visita"),
    ("direccion", "Dirección", "memoria.html", "Plan de Dirección"),
    ("presentacion", "Presentación", "deck.html", "Presentación de Junta"),
    ("protocolos", "Protocolos", "protocolos.html", "Protocolos por puesto"),
    ("operaciones", "Operaciones", "manual.html", "Manual Maestro de Operaciones"),
    ("marketing", "Marketing", "marketing.html", "Plan Maestro de Marketing"),
    ("otros", "Otros", "otros.html", "Otros documentos del sistema"),
    ("numeros", "Los números", "instrumentos/captura.html", "Los números del centro"),
]

# El orden en que monta() DEVUELVE el contenido cosechado (el de siempre: por
# documento). Se usa para casar cada sección con su contenido por su sid, con
# independencia del orden de MENÚ de arriba.
ORDEN_MONTA = ["direccion", "presentacion", "protocolos", "primera-visita",
               "operaciones", "marketing", "otros", "numeros"]

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
    "stroke='%23B99653' stroke-width='4' stroke-linecap='round' stroke-linejoin='round'>"
    "<path d='M52 14 C47 6 39 7 38 17 C37 30 40 44 43 62 C44 72 50 78 53 68 "
    "C56 60 57 50 58 42 C59 50 60 60 63 68 C66 78 72 72 73 62 C76 44 79 30 78 17 "
    "C77 7 69 6 64 14 C61 19 55 19 52 14 Z'/>"
    "<path d='M44 54 C30 50 15 55 9 70 C24 76 40 71 46 58'/>"
    "<path d='M72 54 C86 50 101 55 107 70 C92 76 76 71 70 58'/>"
    "<path d='M20 78 C40 106 76 106 96 78'/></svg>")


# Un icono de línea por sección, dibujado a mano (SVG, no fotos): la red de
# este entorno no deja bajar imágenes y no se inventan fotos de la clínica, así
# que cada sección lleva una ilustración propia relacionada con su tema.
def _ico(inner):
    return ('<svg class="sh__ico" viewBox="0 0 48 48" fill="none" '
            'stroke="currentColor" stroke-width="2.2" stroke-linecap="round" '
            'stroke-linejoin="round" aria-hidden="true">' + inner + '</svg>')


SECC_ICONO = {
    "direccion": _ico('<circle cx="24" cy="24" r="17"/>'
                      '<path d="M31 17 L26 26 L17 31 L22 22 Z"/>'
                      '<circle cx="24" cy="24" r="1.6" fill="currentColor" stroke="none"/>'),
    "presentacion": _ico('<rect x="7" y="10" width="34" height="24" rx="2"/>'
                         '<path d="M14 28 L20 22 L25 26 L34 16"/>'
                         '<path d="M18 41 h12 M24 34 v7"/>'),
    "protocolos": _ico('<rect x="11" y="7" width="26" height="34" rx="2.5"/>'
                       '<path d="M17 17 l3 3 l5 -6"/><path d="M17 29 l3 3 l5 -6"/>'
                       '<path d="M28 18 h5 M28 30 h5"/>'),
    "primera-visita": _ico('<path d="M17 9 C13 6 9 8 9 15 C9 24 11 32 13 38 C14 41 17 41 '
                           '18 37 C19 32 19 26 20 24 C21 26 21 32 22 37 C23 41 26 41 27 38 '
                           'C31 30 33 20 32 14 C31 7 26 6 23 9 C21 11 19 11 17 9 Z"/>'),
    "operaciones": _ico('<circle cx="19" cy="19" r="7"/><circle cx="32" cy="32" r="5"/>'
                        '<path d="M19 12 v-3 M19 26 v3 M12 19 h-3 M26 19 h3 '
                        'M14 14 l-2 -2 M24 24 l2 2"/>'),
    "marketing": _ico('<path d="M9 33 L19 23 L26 29 L39 15"/><path d="M31 15 h8 v8"/>'
                      '<circle cx="19" cy="23" r="1.8" fill="currentColor" stroke="none"/>'
                      '<circle cx="26" cy="29" r="1.8" fill="currentColor" stroke="none"/>'),
    "otros": _ico('<rect x="10" y="14" width="24" height="28" rx="2"/>'
                  '<path d="M16 9 h20 a2 2 0 0 1 2 2 v24"/>'
                  '<path d="M16 23 h12 M16 30 h12 M16 37 h8"/>'),
    "numeros": _ico('<path d="M9 39 h30"/><rect x="13" y="27" width="6" height="12"/>'
                    '<rect x="22" y="19" width="6" height="20"/>'
                    '<rect x="31" y="11" width="6" height="28"/>'),
}


def fuentes_incrustadas():
    """Las dos tipografías de la web, empotradas en el archivo.

    Fraunces —una serif cálida, de revista— para los titulares, y Roboto
    —limpia y muy legible— para el cuerpo y las etiquetas. Fraunces viaja como
    fuente variable (un solo archivo cubre todos los pesos). Todo va en base64
    dentro del propio HTML: la web se abre de doble clic y se ve igual sin
    conexión.
    """
    # (familia, rango de peso, estilo, archivo)
    caras = (
        ("Roboto", "400", "normal", "Roboto-Regular.ttf"),
        ("Roboto", "500", "normal", "Roboto-Medium.ttf"),
        ("Roboto", "700", "normal", "Roboto-Bold.ttf"),
        ("Roboto", "900", "normal", "Roboto-Black.ttf"),
        ("Fraunces", "100 900", "normal", "Fraunces-Variable.ttf"),
    )
    fmt = ('@font-face{font-family:"%s";font-style:%s;font-weight:%s;'
           'font-display:swap;src:url(data:font/ttf;base64,%s) format("truetype")}')
    out = []
    for familia, peso, estilo, arch in caras:
        ruta = RAIZ / "fuentes" / "tipos" / arch
        if ruta.exists():
            b64 = base64.b64encode(ruta.read_bytes()).decode()
            out.append(fmt % (familia, estilo, peso, b64))
    return "".join(out)


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
  /* Oscuro premium: fondo tinta, texto crema y un oro cálido como único
     acento. Serif de revista en los titulares. Lujo y calma. */
  --fondo:#14181C; --panel:#191E23; --panel-2:#20262D;
  --tinta:#F1ECE1; --ink:#F1ECE1; --ink-2:#B9B3A6; --muted:#8B8579;
  /* banda profunda para las franjas oscuras, más honda que el fondo */
  --honda:#0E1216;
  /* acento principal (conserva el nombre --pizarra por compatibilidad):
     un oro cálido. La variante «fuerte» es MÁS CLARA, para que sirva como
     texto legible sobre el fondo oscuro. */
  --pizarra:#B99653; --pizarra-o:#A9863F; --pizarra-fuerte:#CFA862;
  --pizarra-soft:rgba(185,150,83,.10); --pizarra-linea:rgba(185,150,83,.32);
  /* segundo acento, oro más claro: la cursiva del lema y las cifras */
  --calido:#DABB7C; --calido-fuerte:#CFA862;
  --calido-soft:rgba(218,187,124,.12); --calido-linea:rgba(200,162,95,.34);
  --linea:rgba(241,236,225,.13); --linea-2:rgba(241,236,225,.055);
  /* Dos tipografías: Fraunces (serif cálida, de revista) en los titulares,
     Roboto (limpia y legible) en el cuerpo y las etiquetas. */
  --serif:"Fraunces","Georgia","Times New Roman",serif;
  --display:"Fraunces","Georgia","Times New Roman",serif;
  --sans:"Roboto","Helvetica Neue",Arial,sans-serif;
  --mono:"Roboto","Helvetica Neue",Arial,sans-serif;
  --nav:76px; --ancho:74rem;
  /* los tokens de los documentos, remapeados a esta paleta */
  --paper:var(--fondo); --surface:var(--panel); --surface-2:var(--panel-2);
  --accent:var(--pizarra); --accent-ink:var(--pizarra-fuerte);
  --accent-fuerte:var(--pizarra-fuerte); --accent-soft:var(--pizarra-soft);
  --acido:var(--pizarra-soft); --acido-ink:var(--pizarra-fuerte);
  --line:var(--linea); --line-soft:var(--linea-2); --rule:var(--linea);
  --f-body:var(--sans); --f-display:var(--serif); --f-mono:var(--mono);
  --tinta-doc:var(--tinta); --barra:var(--nav);
  --sombra-2:0 2px 6px rgba(0,0,0,.5),0 34px 70px -34px rgba(0,0,0,.85);
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

  // ---- Pop-up de entrada: el manifiesto, una vez por sesión ----
  var portal=D.getElementById('portal');
  function cierraPortal(){
    if(!portal) return;
    portal.classList.remove('on');
    try{ sessionStorage.setItem('alma-portal','1'); }catch(e){}
    setTimeout(function(){ if(portal) portal.hidden=true; }, 420);
  }
  if(portal){
    var visto=false;
    try{ visto=sessionStorage.getItem('alma-portal')==='1'; }catch(e){}
    if(visto || h){ portal.hidden=true; }
    else { portal.hidden=false; requestAnimationFrame(function(){ portal.classList.add('on'); }); }
    portal.addEventListener('click', function(e){
      if(e.target.closest('[data-cerrar]') || e.target===portal) cierraPortal();
    });
  }

  // ---- Pop-up de concepto: las voces técnicas, al pulsarlas ----
  var VOCES=window.__VOCES__||{};
  var modal=D.getElementById('voz-modal');
  var mSigla=modal&&modal.querySelector('[data-voz-sigla]');
  var mDef=modal&&modal.querySelector('[data-voz-def]');
  function abreVoz(sigla){
    if(!modal) return;
    var d=VOCES[sigla];
    if(!d) return;
    mSigla.textContent=sigla;
    mDef.textContent=d;
    modal.hidden=false;
    requestAnimationFrame(function(){ modal.classList.add('on'); });
  }
  function cierraVoz(){
    if(!modal) return;
    modal.classList.remove('on');
    setTimeout(function(){ if(modal) modal.hidden=true; }, 320);
  }
  D.addEventListener('click', function(e){
    var g=e.target.closest('.gl[data-gl]');
    if(g){ e.preventDefault(); abreVoz(g.dataset.gl); return; }
    if(modal && (e.target.closest('[data-cerrar-voz]') || e.target===modal)) cierraVoz();
  });

  // ---- Índice global: botón de la cabecera, disponible en toda la página ----
  var idx=D.getElementById('indice');
  function abreIdx(){ if(!idx) return; idx.hidden=false; requestAnimationFrame(function(){ idx.classList.add('on'); }); }
  function cierraIdx(){ if(!idx) return; idx.classList.remove('on'); setTimeout(function(){ if(idx) idx.hidden=true; }, 320); }
  D.addEventListener('click', function(e){
    if(e.target.closest('[data-indice]')){ e.preventDefault(); abreIdx(); return; }
    if(!idx) return;
    if(e.target.closest('[data-cerrar-indice]') || e.target===idx){ cierraIdx(); return; }
    // al pulsar un enlace del índice, el manejador de navegación actúa y aquí se cierra
    if(e.target.closest('.indice a')){ cierraIdx(); }
  });

  D.addEventListener('keydown', function(e){
    if(e.key==='Escape'){ cierraVoz(); cierraPortal(); cierraIdx(); }
  });
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
            '<span class="hito__m">Fase %d de 14 · %s</span></a>'
            % (anc, fuera, num, H.escape(nombre), int(num), H.escape(minu)))
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
        '<p class="titmapa__k">Mapa 02 · El sistema</p>'
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
            '<span class="paso__min">Fase %d de 14 · %s</span></span>'
            '<span class="paso__sec">%s →</span></a>'
            % (sid, sid, num, H.escape(nombre), int(num), H.escape(minu), H.escape(rot)))
    return (
        '<section class="franja franja--oscura" id="mapa-viaje">'
        '<div class="env">'
        '<header class="titmapa titmapa--claro reveal">'
        '<p class="titmapa__k">Mapa 01 · El viaje del paciente</p>'
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
        '<section class="hero">'
        '<div class="env hero__grid">'
        '  <div class="hero__txt">'
        '<p class="hero__k">Centro de Excelencia Implantológica · Ourense</p>'
        '<h1 class="hero__t">No medias<br><em>sonrisas</em></h1>'
        '<p class="hero__p">Le devolvemos su sonrisa completa, en el menor tiempo '
        'posible, y le cuidamos para siempre. Todo el método del centro, '
        'ordenado y a la vista.</p>'
        '<div class="hero__cta">'
        '<a class="hero__ir" href="#mapa-viaje">Descubrir el método <i>↓</i></a>'
        '<a class="hero__ghost" href="#primera-visita" data-ve="primera-visita">'
        'Su primera visita</a>'
        '</div>'
        '  </div>'
        '  <div class="hero__vis" aria-hidden="true"><div class="hero__disc">'
        + LOGO_EMBLEMA + '</div></div>'
        '</div>'
        '<div class="env"><div class="cifras cifras--hero">%s</div></div>'
        '</section>' % cajas)
    return (
        '<section class="vista" id="v-inicio">\n'
        + hero + mapa_viaje(meta) + banda_lema() + mapa_sistema(meta)
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
    prins = "".join(
        '<a class="prin reveal" href="#%s" data-ve="%s">'
        '<span class="prin__n">%s</span>'
        '<div class="prin__c"><p class="prin__k">%s</p>'
        '<p class="prin__cifra">%s</p>'
        '<p class="prin__t">%s</p>'
        '<span class="prin__ir">Ver en el sistema →</span></div></a>'
        % (sid, sid, num, H.escape(tit), H.escape(cifra), H.escape(texto))
        for num, tit, cifra, sid, texto in principios)

    # Su primera visita, contada como experiencia (no como lista clínica): las
    # cuatro cosas humanas que la hacen distinta, ancladas a las fases reales.
    pasos_pv = [
        ("Le escuchamos primero", "Antes de mirar una sola radiografía, "
         "escuchamos qué le preocupa y qué espera. El plan se construye sobre eso, "
         "no sobre una plantilla."),
        ("Ve su caso en 3D", "Con imagen en tres dimensiones se ven el hueso, los "
         "nervios y las raíces. Usted lo ve con nosotros, sobre su propia boca, "
         "antes de decidir nada."),
        ("Le proponemos, no le vendemos", "Sale con un plan por escrito: qué se "
         "hace, en qué orden, cuánto dura y cuánto cuesta. Lo que no se explica, "
         "no se firma."),
        ("Decide usted, con tiempo", "Ninguna decisión se toma con prisa en el "
         "sillón. Se lleva el plan, lo piensa y vuelve cuando quiera. La calma "
         "también es parte del tratamiento."),
    ]
    pv_html = "".join(
        '<a class="pvpaso reveal" href="#primera-visita" data-ve="primera-visita">'
        '<span class="pvpaso__n">%02d</span>'
        '<span class="pvpaso__c"><b>%s</b><span>%s</span></span></a>'
        % (i, H.escape(t), H.escape(x)) for i, (t, x) in enumerate(pasos_pv, 1))
    primera = (
        '<section class="franja"><div class="env">'
        '<header class="titmapa reveal">'
        '<p class="titmapa__k">Qué esperar</p>'
        '<h2>Su primera visita,<br>sin sorpresas</h2>'
        '<p class="titmapa__p">La primera cita no es un trámite: es donde se '
        'decide todo. Está pensada para que salga de ella sabiendo exactamente '
        'qué tiene, qué se puede hacer y qué cuesta —sin presión y sin letra '
        'pequeña—. Ciento veintitrés minutos, y ni uno de relleno.</p></header>'
        '<div class="pvpasos">' + pv_html + '</div>'
        '</div></section>')

    hero = (
        '<section class="hero2 hero2--exp"><div class="env">'
        '<p class="hero2__k reveal">La experiencia · Lo que se siente, no solo lo que se hace</p>'
        '<h1 class="hero2__t reveal">Una sonrisa no es<br>un trabajo terminado:<br>'
        '<em>es una persona.</em></h1>'
        '<p class="hero2__p reveal">Es alguien que vuelve a reír sin taparse la boca. '
        'En Alma no entendemos la excelencia como una máquina más cara ni un '
        'material más nuevo, sino como la mitad del trabajo que nadie ve —y que '
        'el paciente sí nota—. Esa mitad invisible es la única que ningún '
        'competidor puede comprar.</p>'
        '</div></section>')

    # La implantología, sin misterio: qué le devuelve de verdad un implante.
    # Hechos generales de la disciplina, en la voz de Alma. Nada de marcas ni
    # de cifras que el sistema no sostenga.
    imp = [
        ("Restaura la pieza", "Vuelve el diente que faltaba —su forma y su "
         "función— sin tallar los sanos de al lado."),
        ("Preserva el hueso", "La raíz artificial se integra en el hueso "
         "—osteointegración— y lo mantiene vivo. Sin raíz, el hueso se reabsorbe."),
        ("Función natural", "Se muerde y se mastica como con un diente propio, "
         "no como con una prótesis que se mueve."),
        ("Duradero, si se cuida", "Con el mantenimiento adecuado, la solución más "
         "estable que existe hoy para un diente perdido."),
    ]
    imp_html = "".join(
        '<div class="tar reveal"><h3>%s</h3><p>%s</p></div>'
        % (H.escape(t), H.escape(x)) for t, x in imp)
    implantologia = (
        '<section class="franja"><div class="env">'
        '<header class="titmapa reveal">'
        '<p class="titmapa__k">La implantología, sin misterio</p>'
        '<h2>Qué le devuelve un implante</h2>'
        '<p class="titmapa__p">Un implante no es un diente postizo: es una raíz '
        'nueva. Por eso, bien puesto, no se nota que está —ni al comer, ni al '
        'reír, ni al mirarse—.</p></header>'
        '<div class="rej">' + imp_html + '</div>'
        '</div></section>')

    # La tecnología, atada a las fases reales (imagen, 3D, guía, protocolo).
    # Sin superlativos ni nombres de aparatos que no podamos verificar.
    tec = [
        ("Imagen en tres dimensiones", "Se ven el hueso, los nervios y las raíces "
         "antes de tocar nada. Se decide sobre datos, no sobre una placa plana."),
        ("El caso, en 3D", "Usted ve su propio caso en tres dimensiones antes de "
         "decidir. Lo que aprueba es lo que se hace."),
        ("Colocación guiada", "Lo planificado se traslada a la boca con guía: el "
         "implante va donde se decidió, no donde se pudo."),
        ("Protocolo medido", "Cada fase con su tiempo y su verificación. La "
         "precisión no es una máquina: es un método que se cumple."),
    ]
    tec_html = "".join(
        '<div class="tar reveal"><h3>%s</h3><p>%s</p></div>'
        % (H.escape(t), H.escape(x)) for t, x in tec)
    tecnologia = (
        '<section class="franja franja--oscura"><div class="env">'
        '<header class="titmapa titmapa--claro reveal">'
        '<p class="titmapa__k">La precisión, al detalle</p>'
        '<h2>La técnica, al servicio<br>de lo humano</h2>'
        '<p class="titmapa__p">La tecnología no está para impresionar en la sala '
        'de espera, sino para que dos cosas coincidan: lo que se planifica y lo '
        'que se coloca.</p></header>'
        '<div class="rej rej--oscura">' + tec_html + '</div>'
        '</div></section>')

    # El equipo: los seis puestos reales, sin inventar nombres ni credenciales.
    roles = ["Dirección", "Doctor", "Recepción", "RAC · Producción",
             "Auxiliar", "Higienista"]
    roles_html = "".join(
        '<a class="rolchip reveal" href="#protocolos" data-ve="protocolos">%s</a>'
        % H.escape(r) for r in roles)
    equipo = (
        '<section class="franja"><div class="env">'
        '<header class="titmapa reveal">'
        '<p class="titmapa__k">El equipo</p>'
        '<h2>Un equipo, un criterio</h2>'
        '<p class="titmapa__p">Seis puestos, de la recepción a la dirección, y un '
        'solo criterio entre todos. No es una suma de profesionales: es un sistema '
        'en el que cada persona sabe qué le toca, de qué responde y qué se rompe '
        'aguas abajo si no lo hace. Por eso usted no repite su historia en cada '
        'visita —el sistema la lleva por usted— y por eso lo tratado se sostiene '
        'años después de la última cita.</p></header>'
        '<div class="roles">' + roles_html + '</div>'
        '</div></section>')

    principios_sec = (
        '<section class="franja"><div class="env">'
        '<header class="titmapa reveal">'
        '<p class="titmapa__k">Cinco maneras de notarlo</p>'
        '<h2>Lo que cambia, para usted</h2>'
        '<p class="titmapa__p">Cinco promesas que el sistema entero está montado '
        'para cumplir. Cada una lleva a donde se detalla, por escrito.</p></header>'
        '<div class="prins">' + prins + '</div>'
        '</div></section>')

    cierre = (
        '<section class="banda"><div class="env">'
        '<p class="banda__k reveal">La promesa</p>'
        '<p class="banda__t reveal">No medias sonrisas.<br><em>Ni medias '
        'decisiones.</em></p>'
        '<p class="banda__p reveal">Le devolvemos su sonrisa completa, en el menor '
        'tiempo posible, y le cuidamos para siempre.</p>'
        '</div></section>')

    return (
        '<section class="vista" id="v-experiencia">\n'
        + hero + primera + implantologia + principios_sec + tecnologia + equipo
        + cierre + '\n</section>')


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

    ico = SECC_ICONO.get(sid, "")
    return (
        '<section class="vista" id="v-%s">\n'
        '  <header class="sh reveal"><div class="env sh__grid">\n'
        '    <div class="sh__txt">\n'
        '    <p class="sh__n">Sección %02d <i>de %02d</i> · %s</p>\n'
        '    <h1>%s</h1>\n'
        '    <p class="sh__p">%s</p>\n'
        '    </div>%s\n'
        '  </div></header>\n'
        '  %s\n'
        '  <div class="env">\n'
        '  %s\n'
        '  <div class="cuerpo">\n'
        '    <details class="toc" aria-label="Apartados de la sección">'
        '<summary class="toc__t">En esta sección</summary>'
        '<div class="toc__body">%s</div></details>\n'
        '    <div class="wlista">%s</div>\n'
        '  </div>\n'
        '  %s\n'
        '  </div>\n</section>'
        % (sid, k, n_sec, H.escape(nombre), H.escape(rot), H.escape(texto),
           ico, camino, docif, toc, "\n".join(aps), ruta))


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

/* Rejilla de tarjetas (implantología, tecnología) */
.rej{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:1px;
  background:var(--linea);border:1px solid var(--linea);border-radius:14px;overflow:hidden}
.tar{background:var(--panel);padding:clamp(1.5rem,3vw,2.2rem);display:flex;flex-direction:column;gap:.7rem}
.tar h3{font-family:var(--serif);font-weight:400;font-size:1.4rem;color:var(--tinta);margin:0;line-height:1.12}
.tar p{font-size:.95rem;line-height:1.6;color:var(--ink-2);margin:0}
.rej--oscura{background:rgba(157,187,216,.2);border-color:rgba(157,187,216,.2)}
.rej--oscura .tar{background:var(--pizarra-fuerte)}
.rej--oscura .tar h3{color:#fff}
.rej--oscura .tar p{color:#B9C7D6}

/* Los seis puestos, como fichas */
.roles{display:flex;flex-wrap:wrap;gap:.7rem}
.rolchip{font-family:var(--mono);font-size:.68rem;letter-spacing:.06em;text-transform:uppercase;
  color:var(--pizarra);text-decoration:none;border:1px solid var(--pizarra-linea);border-radius:100px;
  padding:.6rem 1.1rem;transition:background .18s,color .18s}
.rolchip:hover{background:var(--pizarra);color:#fff}

/* Su primera visita: cuatro pasos */
.pvpasos{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:1px;
  background:var(--linea);border:1px solid var(--linea);border-radius:14px;overflow:hidden}
.pvpaso{display:flex;flex-direction:column;gap:.7rem;background:var(--panel);
  padding:clamp(1.5rem,3vw,2.2rem);text-decoration:none;transition:background .18s}
.pvpaso:hover{background:var(--pizarra-soft)}
.pvpaso__n{font-family:var(--serif);font-size:2rem;color:var(--pizarra);line-height:1}
.pvpaso__c b{font-family:var(--serif);font-weight:400;font-size:1.25rem;color:var(--tinta);
  display:block;margin-bottom:.4rem;line-height:1.15}
.pvpaso__c span{font-size:.95rem;line-height:1.6;color:var(--ink-2)}

/* Pie de página: la marca y la dirección real, para cerrar el conjunto */
.pie-web{border-top:1px solid var(--linea);background:var(--panel-2);
  padding:clamp(2.5rem,6vh,4rem) 0}
.pie-web .env{display:flex;flex-direction:column;gap:1rem;align-items:flex-start}
.pie-web .marca__e{width:2.2rem;height:2rem}
.pie-web__lema{font-family:var(--serif);font-size:clamp(1.6rem,4vw,2.4rem);
  color:var(--tinta);margin:.4rem 0 0;line-height:1}
.pie-web__lema em{font-style:italic;color:var(--pizarra)}
.pie-web__d{font-family:var(--mono);font-size:.64rem;letter-spacing:.12em;
  text-transform:uppercase;color:var(--muted);margin:.6rem 0 0;line-height:1.7}

@media(max-width:640px){
  .ruta__i{grid-template-columns:auto 1fr auto}
  .ruta__c{display:none}
  .salta-nav{grid-template-columns:1fr}
  .salta--ant,.salta--sig{grid-column:1;text-align:left}
  .marca__t{display:none}
}
@media(max-width:560px){.prin{grid-template-columns:1fr}}
"""


MODERNO = """
/* ============ Dos acentos y más escala tipográfica ============
   Azul pizarra = el SISTEMA (la estructura, los mapas, las secciones).
   Terracota cálido = la capa HUMANA (la experiencia, las cifras que hay que
   mirar, la ruta de lectura). Con esto la web gana color e intuición —cada
   cosa tiene el suyo— y más contraste de tamaños para que la jerarquía se lea
   sola. */

/* Las cifras, en cálido: saltan sobre el azul de los titulares */
.cifra b,.docif__i b{color:var(--calido)}
.cifra{border-top:2px solid transparent}
.cifras--hero .cifra{border-top-color:var(--calido-linea)}

/* Escala: saltos más grandes entre lo enorme y lo pequeño */
.hero2__t{font-size:clamp(3.4rem,13vw,9.5rem)}
.titmapa h2{font-size:clamp(2.4rem,6.5vw,4.6rem)}
.titmapa__k{font-size:.72rem;letter-spacing:.2em}
.titmapa__p{font-size:1.18rem;line-height:1.5;max-width:44ch}
.sh h1{font-size:clamp(2.6rem,6.5vw,4.4rem)}
.sh__n{font-size:.74rem;letter-spacing:.18em}
.sh__p{font-size:1.15rem}

/* Números decorativos, más grandes y presentes */
.ruta__n{font-size:2.1rem}
.prin__n{font-size:clamp(2rem,5vw,3.2rem)}
.pvpaso__n{font-size:2.4rem}

/* Mapa 03 · la ruta, en cálido: los tres mapas se distinguen por color */
#mapa-ruta .titmapa__k,#mapa-ruta .ruta__n,#mapa-ruta .ruta__f{color:var(--calido)}
#mapa-ruta .ruta__i:hover{background:var(--calido-soft)}

/* La experiencia: el acento cálido manda en toda la capa humana */
#v-experiencia .hero2__t em{color:var(--calido)}
#v-experiencia .titmapa__k{color:var(--calido)}
#v-experiencia .prin__n,#v-experiencia .prin__ir,#v-experiencia .pvpaso__n{color:var(--calido)}
#v-experiencia .prin:hover,#v-experiencia .pvpaso:hover{background:var(--calido-soft)}
#v-experiencia .rolchip{border-color:var(--calido-linea);color:var(--calido-fuerte)}
#v-experiencia .rolchip:hover{background:var(--calido);color:#fff}
/* en las franjas oscuras de la experiencia, el cálido se aclara para contrastar */
#v-experiencia .franja--oscura .titmapa__k{color:#E7B7A3}
#v-experiencia .banda__t em{color:#E8C0AE}

/* El pie: el lema con la cursiva en cálido */
.pie-web__lema em{color:var(--calido)}

/* ====== Repaso de lectura: aire, medida y ritmo ======
   El contenido de los documentos venía apelotonado: líneas larguísimas de lado
   a lado y bloques pegados. Se controla la MEDIDA de línea (unos 68 caracteres,
   lo cómodo), se separa cada apartado y se da ritmo vertical. Minimalista. */
.wart{padding:clamp(2.8rem,7vh,4.6rem) 0}
.wart p{font-size:1.06rem;line-height:1.78;margin:0 0 1.3rem;max-width:68ch}
.wart li{line-height:1.72;margin:.55rem 0;max-width:66ch}
.wart h3{margin:2.6rem 0 1rem}
.wart .eyebrow{margin:0 0 1rem;display:inline-block}
.wart table{margin:2.2rem 0}
.wart figure{margin:2.6rem 0}
.wart blockquote{max-width:62ch}
.wart__k{margin-bottom:1.4rem;font-size:.64rem;letter-spacing:.14em}

/* Botones y controles, más modernos: relleno, pastilla, sombra al vuelo */
.hero2__baja{background:var(--pizarra);color:#fff;border-color:var(--pizarra);
  padding:.9rem 1.7rem;box-shadow:0 12px 26px -14px rgba(51,88,124,.6)}
.hero2__baja:hover{background:var(--pizarra-fuerte);color:#fff;transform:translateY(-2px)}
.cab__l{border-radius:100px}
.cab__l.on{background:var(--pizarra);color:#fff}
.cab__l.on:hover{background:var(--pizarra-fuerte);color:#fff}
.rolchip,.salta{border-radius:100px}
.salta{border-radius:16px}

/* La ilustración de cada sección, en su cabecera */
.sh__grid{display:grid;grid-template-columns:1fr auto;
  gap:clamp(1.5rem,4vw,3rem);align-items:center}
.sh__txt{min-width:0}
.sh__ico{width:clamp(3.2rem,7vw,5.6rem);height:auto;color:var(--pizarra);flex:none}
@media(max-width:680px){.sh__ico{display:none}}
"""


# ------------------------------------------------------------ la piel premium
# Oscuro premium: fondo tinta, oro como único acento, Fraunces en los titulares
# y Roboto en el cuerpo. Sombras profundas, filetes de oro tenue, mucho aire.
# Va la ÚLTIMA en la cascada para dar el acabado sobre todo lo anterior.
ELEGANTE = """
/* velo de oro sobre la tinta, apenas insinuado */
html:root:root body{
  background:
    radial-gradient(120% 80% at 100% -8%, rgba(185,150,83,.12), transparent 58%),
    radial-gradient(90% 60% at -8% 4%, rgba(185,150,83,.06), transparent 55%),
    var(--fondo);
}
html:root:root ::selection{background:var(--pizarra);color:var(--honda)}

/* ---- titulares en Fraunces, con el aire de una revista ---- */
html:root:root .whero h1,html:root:root .hero__t,html:root:root .sh h1,
html:root:root .titmapa h2,html:root:root .banda__t,html:root:root .wart h2,
html:root:root .lema,html:root:root .prin__t{
  font-family:var(--serif);font-weight:400;letter-spacing:-.015em;
  line-height:1.04;text-transform:none;
}
html:root:root .wart h3{font-family:var(--serif);font-weight:500;letter-spacing:-.01em;
  text-transform:none;line-height:1.25}
html:root:root .hero__t em,html:root:root .whero h1 em,html:root:root .lema em{
  font-style:italic;color:var(--calido-fuerte);font-weight:400}

/* ---- etiquetas: Roboto en versalita, tracking amplio, en oro ---- */
html:root:root .sh__n,html:root:root .hero__k,html:root:root .titmapa__k,
html:root:root .whero__k,html:root:root .wart__k,html:root:root .banda__k{
  font-family:var(--sans);font-weight:600;text-transform:uppercase;
  letter-spacing:.16em;font-size:.66rem;color:var(--calido-fuerte);
}

/* ---- cabecera fina y oscura, translúcida ---- */
html:root:root .cab{background:rgba(20,24,28,.82);backdrop-filter:blur(12px);
  border-bottom:1px solid var(--linea)}
html:root:root .cab__m,html:root:root .marca__t{font-family:var(--serif);
  font-weight:500;text-transform:none;letter-spacing:0}
html:root:root .cab__l{font-family:var(--sans);font-weight:500;text-transform:none;
  letter-spacing:.005em;border-radius:100px;border:1px solid transparent}
html:root:root .cab__l:hover{background:var(--pizarra-soft);color:var(--pizarra-fuerte)}
html:root:root .cab__l.on{background:var(--pizarra);color:var(--honda)}
html:root:root .cab__l.on:hover{background:var(--pizarra-fuerte);color:var(--honda)}
html:root:root #prog{background:var(--calido)}

/* ======================= LA PORTADA ======================= */
html:root:root .hero{padding:clamp(2rem,5vh,4.5rem) 0 clamp(2.5rem,6vh,4rem)}
html:root:root .hero__grid{display:grid;grid-template-columns:1.15fr .85fr;
  gap:clamp(2rem,5vw,4.5rem);align-items:center}
html:root:root .hero__k{font-family:var(--sans);font-weight:600;
  text-transform:uppercase;letter-spacing:.18em;font-size:.68rem;
  color:var(--calido-fuerte);margin:0 0 1.4rem}
html:root:root .hero__t{font-family:var(--serif);font-weight:380;
  font-size:clamp(3rem,8.5vw,6.4rem);line-height:.98;letter-spacing:-.02em;
  color:var(--tinta);margin:0 0 1.5rem}
html:root:root .hero__t em{font-style:italic;color:var(--calido-fuerte);font-weight:400}
html:root:root .hero__p{font-family:var(--sans);font-size:clamp(1.05rem,1.5vw,1.22rem);
  line-height:1.7;color:var(--ink-2);max-width:40ch;margin:0 0 2rem}
html:root:root .hero__cta{display:flex;flex-wrap:wrap;gap:.9rem;align-items:center}
html:root:root .hero__ir{display:inline-flex;align-items:center;gap:.5rem;
  font-family:var(--sans);font-weight:600;font-size:.95rem;text-decoration:none;
  background:var(--pizarra);color:var(--honda);border-radius:100px;padding:.9rem 1.9rem;
  box-shadow:0 18px 34px -16px rgba(0,0,0,.8);transition:background .2s,transform .15s,box-shadow .2s}
html:root:root .hero__ir:hover{background:var(--pizarra-fuerte);color:var(--honda);transform:translateY(-2px)}
html:root:root .hero__ir i{font-style:normal}
html:root:root .hero__ghost{display:inline-flex;align-items:center;
  font-family:var(--sans);font-weight:600;font-size:.95rem;text-decoration:none;
  color:var(--calido);border-bottom:1px solid var(--calido-linea);
  padding:.2rem .1rem;transition:color .15s,border-color .15s}
html:root:root .hero__ghost:hover{color:var(--pizarra-fuerte);border-bottom-color:var(--calido)}
/* el disco de oro de la derecha, con el emblema, sobre la tinta */
html:root:root .hero__vis{display:flex;justify-content:center}
html:root:root .hero__disc{width:min(30rem,80vw);aspect-ratio:1;border-radius:50%;
  display:flex;align-items:center;justify-content:center;color:var(--calido);
  background:
    radial-gradient(circle at 34% 26%, rgba(207,168,98,.28), transparent 46%),
    radial-gradient(circle at 68% 78%, rgba(185,150,83,.14), transparent 50%),
    linear-gradient(150deg, #1C2228, var(--honda) 70%);
  box-shadow:inset 0 1px 40px rgba(207,168,98,.14),0 50px 90px -46px rgba(0,0,0,.9);
  border:1px solid rgba(207,168,98,.32)}
html:root:root .hero__disc svg{width:44%;height:44%;stroke-width:1.4}
@media(max-width:820px){
  html:root:root .hero__grid{grid-template-columns:1fr;text-align:left}
  html:root:root .hero__vis{order:-1;margin-bottom:1rem;justify-content:flex-start}
  html:root:root .hero__disc{width:min(15rem,55vw)}
}

/* ---- botón principal (por si queda algún .hero2__baja) ---- */
html:root:root .hero2__baja{border-radius:100px;background:var(--pizarra);color:var(--honda);
  border:0;box-shadow:0 18px 34px -16px rgba(0,0,0,.8);font-family:var(--sans);
  font-weight:600;text-transform:none;letter-spacing:.005em}
html:root:root .hero2__baja:hover{background:var(--pizarra-fuerte);color:var(--honda);transform:translateY(-2px)}

/* ---- tarjetas y cuadros: esquinas suaves, filete tenue, sombra al vuelo ---- */
html:root:root .tarjeta,html:root:root .rej,html:root:root .prin,
html:root:root .pvpaso,html:root:root .cifra,html:root:root .salta,
html:root:root .rolchip{
  border-radius:18px;border:1px solid var(--linea);background:var(--panel)}
html:root:root .tarjeta:hover,html:root:root .prin:hover,
html:root:root .pvpaso:hover,html:root:root .salta:hover{
  box-shadow:var(--sombra-2);transform:translateY(-3px);border-color:var(--pizarra-linea)}
html:root:root .rolchip{border-radius:100px}
html:root:root .cifra{padding:1.35rem 1.3rem;border-top:1px solid var(--linea)}
html:root:root .cifras--hero .cifra{border-top:2px solid var(--calido-linea)}
html:root:root .cifra b{font-family:var(--serif);font-weight:400;color:var(--calido-fuerte)}
html:root:root .cifra span{font-family:var(--sans);color:var(--muted)}

/* ---- números decorativos: Fraunces fina, cifras tabulares, limpios ---- */
html:root:root .ruta__n,html:root:root .prin__n,html:root:root .pvpaso__n,
html:root:root .ram__n,html:root:root .rama__q i,html:root:root .paso__n,
html:root:root .hito__n{font-family:var(--serif);font-weight:300;color:var(--calido-fuerte);
  font-variant-numeric:tabular-nums;letter-spacing:-.01em}

/* ---- tablas y figuras, suaves ---- */
html:root:root .wart table{border:1px solid var(--linea);border-radius:14px;
  overflow:hidden;border-collapse:separate;border-spacing:0}
html:root:root .wart th{background:var(--panel-2);color:var(--tinta);
  font-family:var(--sans);font-weight:600}
html:root:root .wart td{border-top:1px solid var(--linea-2)}
html:root:root .wart figure{border-radius:16px;overflow:hidden}

/* ---- cabecera de sección: filete fino, ilustración en oro ---- */
html:root:root .sh{border-top:1px solid var(--linea)}
html:root:root .sh__ico{color:var(--pizarra)}

/* ---- el índice de la sección: plegable, cerrado por defecto ----
   Con 20+ apartados una lista fija estorba. Ahora es un <details> a ancho
   completo, cerrado de entrada: una barra «En esta sección» que se despliega
   solo si el lector la pulsa. El texto va a ancho completo debajo. */
html:root:root .cuerpo{display:block}
html:root:root .toc{position:static;max-height:none;overflow:visible;
  background:var(--panel);border:1px solid var(--linea);border-radius:14px;
  padding:0;margin:0 0 clamp(2rem,5vh,3rem);box-shadow:none}
html:root:root .toc__t{font-family:var(--sans);font-weight:600;color:var(--calido-fuerte);
  letter-spacing:.14em;text-transform:uppercase;font-size:.66rem;cursor:pointer;
  list-style:none;display:flex;align-items:center;justify-content:space-between;
  gap:1rem;padding:1.05rem 1.3rem;margin:0;border:0;
  transition:color .15s,background .15s;border-radius:14px}
html:root:root .toc__t::-webkit-details-marker{display:none}
html:root:root .toc__t::after{content:"";width:.6rem;height:.6rem;flex:none;
  border-right:2px solid var(--calido-fuerte);border-bottom:2px solid var(--calido-fuerte);
  transform:rotate(45deg);transition:transform .2s;margin-top:-.2rem}
html:root:root .toc[open] .toc__t::after{transform:rotate(-135deg);margin-top:.15rem}
html:root:root .toc__t:hover{color:var(--pizarra-fuerte)}
html:root:root .toc[open] .toc__t{border-bottom:1px solid var(--linea);
  border-radius:14px 14px 0 0}
html:root:root .toc__body{padding:1rem 1.3rem 1.3rem;
  columns:2;column-gap:2.6rem}
html:root:root .toc a{display:block;text-decoration:none;color:var(--ink-2);
  padding:.32rem 0 .32rem .8rem;border-left:2px solid transparent;line-height:1.4;
  break-inside:avoid;transition:color .15s,border-color .15s}
html:root:root .toc a:hover{color:var(--tinta);border-left-color:var(--calido-linea)}
html:root:root .toc a.on{color:var(--pizarra-fuerte);border-left-color:var(--pizarra);font-weight:600}
html:root:root .toc__parte{font-family:var(--sans);font-weight:600;color:var(--calido-fuerte);
  letter-spacing:.08em;text-transform:uppercase;font-size:.58rem;
  margin:1.1rem 0 .4rem;padding-left:.8rem;break-inside:avoid}
html:root:root .toc__parte:first-child{margin-top:0}
@media(max-width:680px){html:root:root .toc__body{columns:1}}

/* ---- voces del glosario: subrayado en oro, elegante ---- */
html:root:root .gl{font-family:var(--sans);font-weight:500;color:var(--pizarra-fuerte);
  background:transparent;border:0;border-bottom:1px solid var(--calido-linea);
  padding:0 .03em;cursor:pointer;transition:color .15s,border-color .15s}
html:root:root .gl:hover{color:var(--calido-fuerte);border-bottom-color:var(--calido)}
html:root:root .gl::after{content:"\\2039";color:var(--calido);margin-left:.15em;font-weight:600}

/* ============ franjas oscuras: recolocadas al oro sobre tinta honda ============
   Los mapas y bandas venían con fondo azul y texto azul claro. En la piel
   premium se hunden a la tinta honda y el texto pasa a crema y oro. */
html:root:root .franja--oscura,html:root:root .banda,
html:root:root .rej--oscura .tar,html:root:root .hito{
  background:var(--honda);color:var(--tinta)}
html:root:root .franja--oscura,html:root:root .banda{
  border-top:1px solid var(--linea);border-bottom:1px solid var(--linea)}
html:root:root .banda{background:
  radial-gradient(90% 120% at 100% 0%, rgba(185,150,83,.14), transparent 55%),var(--honda)}
html:root:root .rej--oscura{background:var(--linea);border-color:var(--linea)}
html:root:root .hitos{background:var(--linea);border-color:var(--linea)}
html:root:root .hito:hover,html:root:root .paso:hover{background:var(--pizarra-soft)}
/* textos que eran azul claro → oro/crema */
html:root:root .paso__min,html:root:root .paso__sec,html:root:root .banda__k,
html:root:root .hito__m,html:root:root .titmapa--claro .titmapa__k{color:var(--calido-fuerte)}
html:root:root .paso__cuerpo b,html:root:root .hito__t,html:root:root .banda__t,
html:root:root .titmapa--claro h2,html:root:root .rej--oscura .tar h3{color:var(--tinta)}
html:root:root .banda__t em,html:root:root .titmapa--claro .titmapa__p,
html:root:root .paso:hover .paso__sec,html:root:root .banda__p,
html:root:root .rej--oscura .tar p{color:var(--ink-2)}
html:root:root .banda__t em{color:var(--calido)}
/* el círculo de la fase, en oro con anillo hondo */
html:root:root .paso__n,html:root:root .hito__n{color:var(--calido-fuerte)}
html:root:root .paso__n{background:var(--pizarra);color:var(--honda);
  box-shadow:0 0 0 6px rgba(185,150,83,.18)}
html:root:root .camino::before{background:var(--pizarra-linea)}

/* ============ POP-UPS ============ */
.overlay{position:fixed;inset:0;z-index:120;display:flex;align-items:center;
  justify-content:center;padding:clamp(1.2rem,5vw,3rem);
  background:rgba(0,0,0,.6);backdrop-filter:blur(4px);
  opacity:0;transition:opacity .4s ease}
.overlay.on{opacity:1}
.overlay[hidden]{display:none}
.portal__caja,.voz__caja{background:var(--panel);border:1px solid var(--pizarra-linea);
  border-radius:24px;box-shadow:0 50px 100px -34px rgba(0,0,0,.9);position:relative;
  transform:translateY(16px) scale(.985);
  transition:transform .45s cubic-bezier(.2,.9,.2,1)}
.overlay.on .portal__caja,.overlay.on .voz__caja{transform:none}

.portal__caja{max-width:40rem;width:100%;padding:clamp(2rem,5vw,3.4rem)}
.portal__k{font-family:var(--sans);font-weight:600;font-size:.66rem;
  letter-spacing:.2em;text-transform:uppercase;color:var(--calido-fuerte);margin:0 0 1.4rem}
.portal__marca{display:flex;align-items:center;gap:.7rem;margin:0 0 1.5rem;color:var(--pizarra)}
.portal__marca svg{width:2.3rem;height:2.3rem}
.portal__marca b{font-family:var(--serif);font-weight:500;font-size:1.3rem;color:var(--tinta)}
.portal__lema{font-family:var(--serif);font-weight:400;font-size:clamp(2.6rem,7vw,4rem);
  line-height:1;color:var(--tinta);margin:0 0 1.2rem;letter-spacing:-.02em}
.portal__lema em{font-style:italic;color:var(--calido-fuerte)}
.portal__p{font-family:var(--sans);font-size:1rem;line-height:1.7;color:var(--ink-2);
  max-width:46ch;margin:0 0 2rem}
.portal__pie{display:flex;flex-wrap:wrap;align-items:center;gap:1rem;justify-content:space-between}
.portal__entrar{font-family:var(--sans);font-weight:600;font-size:.9rem;letter-spacing:.005em;
  background:var(--pizarra);color:var(--honda);border:0;border-radius:100px;padding:.9rem 2rem;cursor:pointer;
  box-shadow:0 18px 34px -16px rgba(0,0,0,.8);transition:background .2s,transform .15s}
.portal__entrar:hover{background:var(--pizarra-fuerte);transform:translateY(-2px)}
.portal__dir{font-family:var(--sans);font-size:.72rem;letter-spacing:.02em;color:var(--muted)}

.voz__caja{max-width:32rem;width:100%;padding:clamp(1.8rem,4vw,2.6rem)}
.voz__k{font-family:var(--sans);font-weight:600;font-size:.62rem;letter-spacing:.2em;
  text-transform:uppercase;color:var(--calido-fuerte);margin:0 0 .9rem}
.voz__sigla{font-family:var(--serif);font-weight:400;font-size:clamp(2rem,6vw,2.8rem);
  line-height:1.05;color:var(--tinta);margin:0 0 .8rem;letter-spacing:-.01em}
.voz__def{font-family:var(--sans);font-size:.98rem;line-height:1.72;color:var(--ink-2);margin:0}
.cerrar{position:absolute;top:1rem;right:1rem;width:2.2rem;height:2.2rem;line-height:1;
  border:1px solid var(--linea);background:var(--panel);color:var(--ink-2);cursor:pointer;
  border-radius:100px;font-family:var(--sans);font-size:1.1rem;display:flex;
  align-items:center;justify-content:center;transition:background .15s,color .15s,border-color .15s}
.cerrar:hover{background:var(--pizarra);color:var(--honda);border-color:var(--pizarra)}

/* ---- marca: Klinikare (el sistema) sobre Clínica Alma (la clínica) ---- */
html:root:root .marca__tt{display:inline-flex;flex-direction:column;line-height:1.02}
html:root:root .marca__t{display:block;font-family:var(--serif);font-weight:500;
  color:var(--tinta);letter-spacing:.01em}
html:root:root .marca__sub{font-family:var(--sans);font-weight:600;
  letter-spacing:.22em;text-transform:uppercase;color:var(--calido-fuerte);margin-top:.22rem}
/* cabecera: la marca, más grande */
html:root:root .cab .marca__t{font-size:1.75rem}
html:root:root .cab .marca__sub{font-size:.66rem}
html:root:root .cab .marca__e{width:2.3rem;height:2.1rem}
/* pie: la marca, aún más grande */
html:root:root .pie-web .marca__t{font-size:2.2rem}
html:root:root .pie-web .marca__sub{font-size:.78rem}
html:root:root .pie-web .marca__e{width:2.8rem;height:2.55rem}
html:root:root .portal__marca-tt{display:inline-flex;flex-direction:column;line-height:1.02}
html:root:root .portal__marca-tt b{font-family:var(--serif);font-weight:500;font-size:1.7rem;color:var(--tinta)}
html:root:root .portal__marca-tt i{font-family:var(--sans);font-style:normal;font-weight:600;
  font-size:.7rem;letter-spacing:.22em;text-transform:uppercase;color:var(--calido-fuerte);margin-top:.22rem}
html:root:root .portal__marca svg{width:2.8rem;height:2.8rem}
@media(max-width:560px){html:root:root .cab .marca__t{font-size:1.4rem}
  html:root:root .marca__sub{display:none}}

/* ---- listas numeradas del texto: números en oro, sangría francesa ----
   Los «1. 2. 3.» de los documentos se rehacen con número en serif dorada,
   alineados y con aire, en vez del punto gris por defecto del navegador. */
html:root:root .wart ol:not([class]),html:root:root .wart ol.steps,
html:root:root .wart ol.pasos{
  list-style:none;counter-reset:li;padding-left:0;margin:1.4rem 0}
html:root:root .wart ol:not([class]) > li,html:root:root .wart ol.steps > li,
html:root:root .wart ol.pasos > li{
  counter-increment:li;position:relative;padding-left:2.2rem;margin:.7rem 0;
  line-height:1.72;max-width:66ch}
html:root:root .wart ol:not([class]) > li::before,html:root:root .wart ol.steps > li::before,
html:root:root .wart ol.pasos > li::before{
  content:counter(li) ".";position:absolute;left:0;top:0;
  font-family:var(--serif);font-weight:500;font-size:1em;color:var(--calido-fuerte);
  font-variant-numeric:tabular-nums}
html:root:root .wart ol:not([class]) > li::marker,
html:root:root .wart ol.steps > li::marker,
html:root:root .wart ol.pasos > li::marker{content:none}

/* ---- botón Índice en la cabecera, distinto de los enlaces ---- */
html:root:root .cab__indice{border:1px solid var(--pizarra-linea);color:var(--calido-fuerte);
  font-weight:600;cursor:pointer;background:transparent}
html:root:root .cab__indice:hover{background:var(--pizarra);color:var(--honda);border-color:var(--pizarra)}

/* ---- el ÍNDICE global (overlay) ---- */
.indice__caja{background:var(--panel);border:1px solid var(--pizarra-linea);border-radius:22px;
  box-shadow:0 50px 100px -34px rgba(0,0,0,.9);max-width:60rem;width:100%;
  padding:clamp(1.8rem,4vw,3rem);position:relative;max-height:86vh;overflow:auto;
  transform:translateY(16px) scale(.985);transition:transform .4s cubic-bezier(.2,.9,.2,1)}
.overlay.on .indice__caja{transform:none}
.indice__tt{font-family:var(--serif);font-weight:400;font-size:clamp(1.6rem,4vw,2.4rem);
  color:var(--tinta);margin:0 0 1.6rem;letter-spacing:-.01em}
.indice__cols{display:grid;grid-template-columns:1fr 1fr;gap:clamp(1.6rem,4vw,3rem);align-items:start}
.indice__k{font-family:var(--sans);font-weight:600;font-size:.62rem;letter-spacing:.16em;
  text-transform:uppercase;color:var(--calido-fuerte);margin:0 0 1rem;
  padding-bottom:.8rem;border-bottom:1px solid var(--linea)}
.idx-fases,.idx-secs{display:grid;gap:.25rem}
.idx-fase,.idx-sec{display:flex;align-items:baseline;gap:.9rem;text-decoration:none;
  padding:.5rem .6rem;border-radius:10px;transition:background .15s}
.idx-fase:hover,.idx-sec:hover{background:var(--pizarra-soft)}
.idx-fase__n,.idx-sec__n{font-family:var(--serif);font-weight:300;color:var(--calido-fuerte);
  font-variant-numeric:tabular-nums;width:2rem;flex:none;text-align:right;font-size:1.1rem;line-height:1.3}
.idx-fase__t,.idx-sec__t{display:flex;flex-direction:column;gap:.1rem;min-width:0}
.idx-fase__t b,.idx-sec__t b{font-family:var(--sans);font-weight:600;color:var(--tinta);font-size:.98rem}
.idx-fase__m,.idx-sec__c{font-family:var(--sans);font-size:.72rem;color:var(--muted)}
@media(max-width:640px){.indice__cols{grid-template-columns:1fr}}
"""

def main():
    secciones, menus, indice, orden, voces, mapa = bs.monta()
    total = len(orden)

    nav = ('<button type="button" class="cab__l cab__indice" data-indice '
           'aria-haspopup="dialog">Índice</button>'
           '<a class="cab__l" href="#inicio" data-ve="inicio">Inicio</a>'
           '<a class="cab__l" href="#experiencia" data-ve="experiencia">La experiencia</a>'
           + "".join(
               '<a class="cab__l" href="#%s" data-ve="%s">%s</a>' % (sid, sid, H.escape(rot))
               for sid, rot, _d, _n in SECCIONES))

    # casar cada sección con su contenido por su sid (monta() lo devuelve en
    # ORDEN_MONTA, no en el orden de MENÚ)
    contenido = dict(zip(ORDEN_MONTA, secciones))

    vistas = [bloque_inicio(indice, total), bloque_experiencia()]
    for k, (sid, rot, doc, nombre) in enumerate(SECCIONES, 1):
        vistas.append(bloque_seccion(k, sid, rot, nombre, contenido[sid]))

    estilo = ("<style>%s</style>\n<style>%s\n%s\n%s\n%s\n%s\n%s</style>"
              % (css_documentos(), fuentes_incrustadas(), TEMA, SHELL, BOLD, MODERNO, ELEGANTE))

    # ---- los dos pop-ups ----
    # 1) El manifiesto de entrada: se muestra una vez por sesión, al abrir.
    portal = (
        '<div class="overlay portal" id="portal" role="dialog" aria-modal="true" '
        'aria-labelledby="portal-lema" hidden>\n'
        '  <div class="portal__caja">\n'
        '    <p class="portal__k">Centro de Excelencia Implantológica</p>\n'
        '    <p class="portal__marca">' + LOGO_EMBLEMA
        + '<span class="portal__marca-tt"><b>Klinikare</b>'
        '<i>Clínica Alma</i></span></p>\n'
        '    <h2 class="portal__lema" id="portal-lema">No medias <em>sonrisas</em></h2>\n'
        '    <p class="portal__p">Un solo criterio: la excelencia o nada. '
        'Implantología guiada, un sistema documental que no deja cabos sueltos '
        'y un trato que empieza mucho antes de la primera visita.</p>\n'
        '    <div class="portal__pie">\n'
        '      <button type="button" class="portal__entrar" data-cerrar>Entrar</button>\n'
        '      <span class="portal__dir">Calle Progreso 2 · Ourense</span>\n'
        '    </div>\n'
        '  </div>\n'
        '</div>')

    # 2) El concepto técnico: se abre al pulsar una voz del glosario.
    voz_modal = (
        '<div class="overlay voz-modal" id="voz-modal" role="dialog" aria-modal="true" '
        'aria-labelledby="voz-sigla" hidden>\n'
        '  <div class="voz__caja">\n'
        '    <button type="button" class="cerrar" data-cerrar-voz aria-label="Cerrar">×</button>\n'
        '    <p class="voz__k">Concepto del sistema</p>\n'
        '    <h2 class="voz__sigla" id="voz-sigla" data-voz-sigla></h2>\n'
        '    <p class="voz__def" data-voz-def></p>\n'
        '  </div>\n'
        '</div>')

    # el diccionario de voces, para el pop-up de concepto (solo la definición)
    voces_js = json.dumps({k: v[0] for k, v in voces.items()}, ensure_ascii=False)

    # 3) El ÍNDICE global: un botón en la cabecera lo abre desde cualquier
    # página. Reúne las 14 fases (etiquetadas «Fase N de 14», las 12 de la
    # primera visita y las 2 del después) y las ocho secciones, para saltar a
    # cualquier punto del sistema.
    meta_idx = _meta(indice)
    fases_html = "".join(
        '<a class="idx-fase" href="#%s" data-idx-ir>'
        '<span class="idx-fase__n">%s</span>'
        '<span class="idx-fase__t"><b>%s</b>'
        '<span class="idx-fase__m">Fase %d de 14 · %s</span></span></a>'
        % (fase_ancla(num), num, H.escape(nombre), int(num), H.escape(minu))
        for num, nombre, minu, sid in FASES)
    secs_html = "".join(
        '<a class="idx-sec" href="#%s" data-ve="%s" data-idx-ir>'
        '<span class="idx-sec__n">%02d</span>'
        '<span class="idx-sec__t"><b>%s</b>'
        '<span class="idx-sec__c">%s</span></span></a>'
        % (sid, sid, meta_idx[sid][3], H.escape(rot),
           H.escape(cuenta_txt(sid, meta_idx[sid][2], nombre)))
        for sid, rot, _d, nombre in SECCIONES)
    indice_overlay = (
        '<div class="overlay indice" id="indice" role="dialog" aria-modal="true" '
        'aria-label="Índice del sistema" hidden>\n'
        '  <div class="indice__caja">\n'
        '    <button type="button" class="cerrar" data-cerrar-indice aria-label="Cerrar">×</button>\n'
        '    <p class="indice__tt">Índice del sistema</p>\n'
        '    <div class="indice__cols">\n'
        '      <div class="indice__col">\n'
        '        <p class="indice__k">Las 14 fases · la primera visita y el después</p>\n'
        '        <div class="idx-fases">' + fases_html + '</div>\n'
        '      </div>\n'
        '      <div class="indice__col">\n'
        '        <p class="indice__k">Las ocho secciones</p>\n'
        '        <div class="idx-secs">' + secs_html + '</div>\n'
        '      </div>\n'
        '    </div>\n'
        '  </div>\n'
        '</div>')

    # Se arma por trozos (sin %-format) para no chocar con el «%» del favicon
    # ni con las llaves del SVG del logo.
    cabecera = (
        '<a class="cab__m marca" href="#inicio" data-ve="inicio" '
        'aria-label="Klinikare · Clínica Alma · inicio">' + LOGO_EMBLEMA
        + '<span class="marca__tt"><span class="marca__t">Klinikare</span>'
        '<span class="marca__sub">Clínica Alma</span></span></a>')

    doc = (
        '<!doctype html>\n<html lang="es">\n<head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<title>Klinikare · Clínica Alma · Sistema documental</title>\n'
        '<link rel="icon" href="' + LOGO_FAVICON + '">\n'
        + estilo + '\n</head>\n<body>\n'
        + portal + '\n' + voz_modal + '\n' + indice_overlay + '\n'
        '<header class="cab">\n  ' + cabecera + '\n'
        '  <nav class="cab__nav" aria-label="Secciones">' + nav + '</nav>\n'
        '  <div class="cab__prog" id="prog" aria-hidden="true"></div>\n'
        '</header>\n'
        '<main>\n' + "\n".join(vistas) + '\n</main>\n'
        '<footer class="pie-web"><div class="env">'
        '<a class="marca" href="#inicio" data-ve="inicio" aria-label="Klinikare · Clínica Alma">'
        + LOGO_EMBLEMA + '<span class="marca__tt"><span class="marca__t">Klinikare</span>'
        '<span class="marca__sub">Clínica Alma</span></span></a>'
        '<p class="pie-web__lema">No medias <em>sonrisas</em></p>'
        '<p class="pie-web__d">Sistema documental · Centro de Excelencia Implantológica · '
        'Calle Progreso 2 · Ourense<br>Uso interno y confidencial</p>'
        '</div></footer>\n'
        '<script>window.__VOCES__=' + voces_js + ';</script>\n'
        '<script>' + JS + '</script>\n'
        '</body>\n</html>\n')

    salida = RAIZ / "web.html"
    # El software del centro es Klinikare: donde los documentos decían el nombre
    # anterior de la herramienta —«Clinic Cloud»— ahora dice «Klinikare». Se
    # sustituye en todo el documento (texto, voz del glosario y su definición),
    # de modo que el pop-up de concepto sigue resolviendo.
    doc = re.sub(r"Clinic\s+Cloud", "Klinikare", doc)
    salida.write_text(doc, encoding="utf-8")
    print("web.html · %d secciones · %d apartados · %d KB"
          % (len(SECCIONES), total, len(doc.encode("utf-8")) // 1024))


if __name__ == "__main__":
    main()
