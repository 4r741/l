#!/usr/bin/env python3
"""Exporta los documentos a HTML autónomos, con las tipografías incrustadas.

Genera en export/ una copia de cada página que funciona sin conexión: descarga
las fuentes de Google Fonts, las incrusta como data URI y reescribe los enlaces
cruzados a los nombres de archivo exportados.

    python3 build-export.py

Requiere conexión solo durante la exportación. El resultado no depende de nada
externo: ni fuentes, ni scripts, ni imágenes.
"""
import base64
import pathlib
import re
import urllib.request

RAIZ = pathlib.Path(__file__).parent
DESTINO = RAIZ / "export"

# Los archivos a exportar: nombre de salida, identificador dentro del archivo
# único y prefijo con el que se evitan las colisiones de identificadores.
PAGINAS = {
    "inicio.html": "Giraldo-INICIO-AQUI.html",
    "memoria.html": "Tesis-Direccion-Giraldo-v6.html",
    "deck.html": "Presentacion-Junta-Giraldo-v6.html",
    "marketing.html": "Plan-Marketing-Giraldo-v6.html",
    "manual.html": "Manual-Maestro-Giraldo-v6.html",
    "index.html": "Protocolo-Primera-Visita-Giraldo-v6.html",
    "otros.html": "Otros-Documentos-Giraldo-v6.html",
    "instrumentos/captura.html": "Captura-Linea-Base-Giraldo-v6.html",
}

DOCUMENTOS = {
    "inicio.html": ("doc-inicio", "in-"),
    "memoria.html": ("doc-tesis", "tes-"),
    "deck.html": ("doc-deck", "dk-"),
    "marketing.html": ("doc-marketing", "mk-"),
    "instrumentos/captura.html": ("doc-captura", "cp-"),
    "manual.html": ("doc-manual", ""),
    "index.html": ("doc-protocolo", "pv-"),
    "otros.html": ("doc-otros", "ot-"),
}

# Rótulo de cada documento en el conmutador permanente del archivo único.
ROTULOS = [
    ("doc-inicio", "Inicio"),
    ("doc-tesis", "Tesis de Dirección"),
    ("doc-deck", "Presentación"),
    ("doc-marketing", "Plan de Marketing"),
    ("doc-captura", "Captura"),
    ("doc-manual", "Manual Maestro"),
    ("doc-protocolo", "Protocolo"),
    ("doc-otros", "Otros documentos"),
]

# Solo se incrustan estos subconjuntos: el resto (cirílico, vietnamita) no se usa
SUBCONJUNTOS = ("latin", "latin-ext")

# Navegador moderno, para que Google Fonts devuelva woff2
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

ENLACES_FUENTES = re.compile(
    r'<link rel="preconnect"[^>]*>\s*<link rel="preconnect"[^>]*>\s*'
    r'<link rel="stylesheet" href="(https://fonts\.googleapis\.com[^"]*)">',
    re.S,
)


def descargar(url):
    peticion = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(peticion) as respuesta:
        return respuesta.read()


def fuentes_incrustadas(url_css):
    """Devuelve un <style> con las @font-face de los subconjuntos latinos."""
    css = descargar(url_css).decode("utf-8")
    bloques = re.findall(r"/\*\s*([a-z\-]+)\s*\*/\s*(@font-face\s*\{.*?\})", css, re.S)
    incrustados, peso = [], 0
    for subconjunto, bloque in bloques:
        if subconjunto not in SUBCONJUNTOS:
            continue
        encontrada = re.search(r"url\((https://[^)]+\.woff2)\)", bloque)
        if not encontrada:
            continue
        datos = descargar(encontrada.group(1))
        peso += len(datos)
        b64 = base64.b64encode(datos).decode()
        incrustados.append(
            bloque.replace(encontrada.group(1), "data:font/woff2;base64," + b64)
        )
    print(f"  {len(incrustados)} tipografías incrustadas · {peso // 1024} KB")
    return (
        "<style>\n/* Tipografías incrustadas (subconjuntos latin y latin-ext) "
        "para uso sin conexión */\n" + "\n".join(incrustados) + "\n</style>"
    )



# ---------------------------------------------------------------------------
# Archivo único: los tres documentos dentro de un solo HTML
# ---------------------------------------------------------------------------

UNIFICADO = "Giraldo-TODO-EN-UNO-v6.html"

# Un único script para los tres documentos: el original de cada página busca sus
# elementos por id, y al unirlos habría colisiones. Aquí todo se busca dentro
# del contenedor de cada documento.
SCRIPT = """<script>
(function(){
  "use strict";
  var quieto = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var docs = Array.prototype.slice.call(document.querySelectorAll(".doc"));

  /* ---- conmutador entre documentos ---- */
  function mostrar(id, moverScroll){
    var existe = docs.some(function(d){ return d.id === id; });
    if(!existe) return;
    docs.forEach(function(d){ d.hidden = (d.id !== id); });
    document.querySelectorAll(".conmutador [data-ir-a]").forEach(function(b){
      b.setAttribute("aria-current", String(b.dataset.irA === id));
    });
    var activo = document.getElementById(id);
    /* nada puede quedar sin revelar al cambiar de documento */
    activo.querySelectorAll(".reveal").forEach(function(el){ el.classList.add("in"); });
    if(moverScroll) window.scrollTo(0, 0);
    try { history.replaceState(null, "", "#" + id); } catch(e){}
  }
  document.querySelectorAll("[data-ir-a]").forEach(function(a){
    a.addEventListener("click", function(e){
      e.preventDefault();
      var ancla = a.dataset.ancla ? document.getElementById(a.dataset.ancla) : null;
      mostrar(a.dataset.irA, !ancla);
      if(ancla) ancla.scrollIntoView({behavior:"instant"});
      try { history.replaceState(null, "", "#" + (a.dataset.ancla || a.dataset.irA)); } catch(err){}
    });
  });
  if(location.hash){
    var destino = document.getElementById(location.hash.slice(1));
    if(destino && destino.classList.contains("doc")) mostrar(destino.id, false);
    else if(destino){
      var contenedor = destino.closest(".doc");
      if(contenedor) mostrar(contenedor.id, false);
    }
  }

  /* ---- por documento: filtro por puesto, sección activa y revelado ---- */
  docs.forEach(function(doc){
    var fases = Array.prototype.slice.call(doc.querySelectorAll(".phase"));
    var tira = doc.querySelector(".strip");
    var enlaces = tira ? Array.prototype.slice.call(tira.querySelectorAll("a")) : [];
    var chips = Array.prototype.slice.call(doc.querySelectorAll(".chip[data-role]"));
    var limpiar = doc.querySelector(".legend .chip:not([data-role])");
    var rolActivo = null;

    function coincide(ph){
      if(!rolActivo) return true;
      return (" " + ph.dataset.roles + " ").indexOf(" " + rolActivo + " ") > -1;
    }
    function aplicarFiltro(){
      fases.forEach(function(ph){ ph.classList.toggle("is-dimmed", !coincide(ph)); });
      enlaces.forEach(function(a){
        var ph = doc.querySelector(a.getAttribute("href"));
        var esFase = ph && ph.classList.contains("phase");
        a.classList.toggle("is-off", esFase ? !coincide(ph) : false);
      });
      var barra = doc.querySelector(".timemap__bar");
      if(barra){
        Array.prototype.slice.call(barra.children).forEach(function(seg){
          var ph = doc.querySelector("#" + seg.dataset.target);
          if(ph) seg.style.opacity = coincide(ph) ? "1" : "0.25";
        });
      }
      chips.forEach(function(c){ c.setAttribute("aria-pressed", String(c.dataset.role === rolActivo)); });
    }
    chips.forEach(function(c){
      c.addEventListener("click", function(){
        rolActivo = (rolActivo === c.dataset.role) ? null : c.dataset.role;
        aplicarFiltro();
      });
    });
    if(limpiar) limpiar.addEventListener("click", function(){ rolActivo = null; aplicarFiltro(); });

    /* barra de tiempos, si el documento la tiene */
    var barra = doc.querySelector(".timemap__bar");
    if(barra && !barra.children.length){
      fases.forEach(function(ph){
        var min = parseInt(ph.dataset.min, 10) || 5;
        var lider = (ph.dataset.roles || "").split(" ")[0] || "director";
        var seg = document.createElement("button");
        seg.type = "button";
        seg.className = "timemap__seg";
        seg.dataset.role = lider;
        seg.dataset.target = ph.id;
        seg.style.flex = min + " 1 0";
        var t = ph.dataset.time || (min + " min");
        seg.title = ph.dataset.label + " · " + t;
        seg.setAttribute("aria-label", "Ir a la fase " + ph.dataset.label + ", " + t);
        seg.innerHTML = "<span>" + ph.id.replace(/\\D/g, "") + "</span>";
        seg.addEventListener("click", function(){ ph.scrollIntoView({behavior: quieto ? "auto" : "smooth", block: "start"}); });
        barra.appendChild(seg);
      });
    }

    function centrarEnTira(a){
      if(!tira) return;
      var destino = a.offsetLeft - tira.clientWidth / 2 + a.offsetWidth / 2;
      destino = Math.max(0, Math.min(destino, tira.scrollWidth - tira.clientWidth));
      if(Math.abs(destino - tira.scrollLeft) < 24) return;
      tira.scrollTo({left: destino, behavior: quieto ? "auto" : "smooth"});
    }

    var objetivos = Array.prototype.slice.call(doc.querySelectorAll("main section[id], main article[id], main div.parthead[id]"));
    if("IntersectionObserver" in window){
      var espia = new IntersectionObserver(function(entradas){
        entradas.forEach(function(e){
          if(!e.isIntersecting) return;
          var activo = null;
          enlaces.forEach(function(a){
            var on = a.getAttribute("href") === "#" + e.target.id;
            a.setAttribute("aria-current", String(on));
            if(on) activo = a;
          });
          if(activo) centrarEnTira(activo);
        });
      }, {rootMargin: "-130px 0px -70% 0px", threshold: 0});
      objetivos.forEach(function(t){ espia.observe(t); });

      var revelado = new IntersectionObserver(function(entradas){
        entradas.forEach(function(e){
          if(e.isIntersecting){ e.target.classList.add("in"); revelado.unobserve(e.target); }
        });
      }, {rootMargin: "0px 0px -8% 0px", threshold: 0});
      doc.querySelectorAll(".reveal").forEach(function(el){ revelado.observe(el); });
    } else {
      doc.querySelectorAll(".reveal").forEach(function(el){ el.classList.add("in"); });
    }
  });
})();
</script>"""

ESTILO_DOC = """<style>
/* Contenedor de cada documento dentro del archivo único */
[hidden]{display:none!important}
.doc{display:block}

/* Conmutador permanente: el archivo no depende de ningún enlace externo */
:root{--conmutador:52px}
.conmutador{
  position:sticky;top:0;z-index:90;background:var(--ink);color:var(--surface);
  border-bottom:1px solid rgba(247,248,245,.18);
}
.conmutador__in{
  width:min(100% - 2rem,1180px);margin-inline:auto;
  display:flex;align-items:center;gap:.4rem 1.2rem;flex-wrap:wrap;padding:.5rem 0;
}
.conmutador__marca{
  font-family:var(--f-display);font-size:.95rem;margin-right:auto;white-space:nowrap;
}
.conmutador__marca b{font-weight:600}
.conmutador__marca span{
  font-family:var(--f-mono);font-size:.6rem;letter-spacing:.14em;text-transform:uppercase;
  color:#7FD3C9;margin-left:.5rem;
}
.conmutador__botones{display:flex;gap:2px;flex-wrap:wrap}
.conmutador button{
  font:inherit;font-family:var(--f-mono);font-size:.62rem;letter-spacing:.1em;
  text-transform:uppercase;background:transparent;border:1px solid transparent;
  color:rgba(247,248,245,.7);padding:.36rem .6rem;border-radius:999px;cursor:pointer;
}
.conmutador button:hover{color:#7FD3C9;border-color:rgba(127,211,201,.4)}
.conmutador button[aria-current="true"]{
  background:rgba(127,211,201,.16);border-color:#7FD3C9;color:#7FD3C9;
}
.doc .topbar{top:var(--conmutador)}
/* la presentación ocupa la altura libre bajo el conmutador */
#doc-deck .deck{height:calc(100vh - var(--conmutador))}
#doc-deck .hud{bottom:14px}
@media print{
  .conmutador{display:none}
  .doc[hidden]{display:none!important}
  #doc-deck .deck{height:auto}
}
</style>"""


# Dentro del archivo único, la portada no puede seguir hablando de «mantener los
# archivos en la misma carpeta»: aquí no hay archivos que separar.
CONTEXTO_UNICO = [
    ("Cada archivo es una página completa: se abre en el navegador que tenga instalado, "
     "sin conexión y sin ningún programa adicional. Mantenga los seis en la misma carpeta "
     "para que los enlaces entre ellos funcionen.",
     "Está usted dentro del archivo único: los siete documentos viven en este mismo fichero, "
     "con las tipografías y los gráficos incrustados. No hay nada que mantener junto ni nada "
     "que se pueda separar; use la barra de arriba para moverse entre ellos."),
    ("Copie la carpeta completa en una memoria o envíela comprimida. No hay servidor, ni "
     "cuenta, ni dependencia externa: lo que ve aquí es todo lo que hace falta.",
     "Copie este único archivo en una memoria o envíelo por correo. No hay servidor, ni "
     "cuenta, ni dependencia externa, ni segundo archivo que se pueda perder: lo que ve aquí "
     "es todo lo que hace falta."),
    ("Seis documentos que se abren en cualquier navegador, sin instalar nada y sin conexión. "
     "Todos comparten la versión <strong>v6.0</strong>",
     "Siete documentos dentro de un solo archivo, que se abre en cualquier navegador sin "
     "instalar nada y sin conexión. Todos comparten la versión <strong>v6.0</strong>"),
]


def _bloque(css, apertura):
    """Devuelve (contenido, posición tras el cierre) de la llave en `apertura`."""
    profundidad, i = 0, apertura
    while i < len(css):
        if css[i] == "{":
            profundidad += 1
        elif css[i] == "}":
            profundidad -= 1
            if profundidad == 0:
                return css[apertura + 1:i], i + 1
        i += 1
    return css[apertura + 1:], len(css)


def _partir(selectores):
    """Separa una lista de selectores por comas de primer nivel."""
    partes, actual, profundidad = [], "", 0
    for c in selectores:
        if c in "([":
            profundidad += 1
        elif c in ")]":
            profundidad -= 1
        if c == "," and profundidad == 0:
            partes.append(actual); actual = ""
        else:
            actual += c
    partes.append(actual)
    return [p.strip() for p in partes if p.strip()]


def escopar(css, ambito):
    """Encierra una hoja de estilos dentro de un ámbito.

    La presentación trae su propio CSS con selectores globales —`body`, `table`,
    `.eyebrow`— que en el archivo único pisarían a los de los demás documentos.
    Cada selector se antepone con el contenedor de la presentación; las reglas
    de `@keyframes` y `@page` se dejan intactas porque ahí no hay selectores.
    """
    salida, i = [], 0
    while i < len(css):
        if css.startswith("/*", i):
            fin = css.find("*/", i)
            fin = len(css) if fin < 0 else fin + 2
            salida.append(css[i:fin]); i = fin; continue
        if css[i].isspace():
            salida.append(css[i]); i += 1; continue
        apertura = css.find("{", i)
        if apertura < 0:
            salida.append(css[i:]); break
        prelude = css[i:apertura].strip()
        contenido, siguiente = _bloque(css, apertura)
        if prelude.startswith("@"):
            regla = re.match(r"@[-\w]+", prelude).group(0)
            dentro = escopar(contenido, ambito) if regla in ("@media", "@supports") else contenido
            salida.append("%s{%s}" % (prelude, dentro))
        else:
            nuevos = []
            for s in _partir(prelude):
                if s in ("html", "body", "html,body"):
                    nuevos.append(ambito)
                elif s.startswith("body"):        # estados puestos en el <body> real
                    resto = s[4:]
                    corte = len(resto) - len(resto.lstrip())
                    marca = resto[:corte] if corte else ""
                    j = 0
                    while j < len(resto) and resto[j] not in " >+~":
                        j += 1
                    nuevos.append("body%s %s%s" % (resto[:j], ambito, resto[j:]))
                elif s.startswith(ambito):
                    nuevos.append(s)
                else:
                    nuevos.append("%s %s" % (ambito, s))
            salida.append("%s{%s}" % (",".join(dict.fromkeys(nuevos)), contenido))
        i = siguiente
    return "".join(salida)


def estilos_propios(html, marca):
    """El bloque de estilos que un documento añade sobre el sistema común."""
    bloques = re.findall(r"<style>(.*?)</style>", html, re.S)
    for b in bloques:
        if marca in b:
            return b
    return ""


def cuerpo(html):
    """Devuelve el contenido de <body> sin los guiones del final.

    Se corta en el PRIMER <script>, no en el último: la Tesis lleva dos —el de
    comportamiento común y el de la comprobación en directo— y cortar por el
    último dejaba el primero duplicado dentro del archivo único.
    """
    inicio = html.index("<body>") + len("<body>")
    fin = html.find("<script>", inicio)
    if fin < 0:                       # la portada no lleva guion propio
        fin = html.rindex("</body>")
    return html[inicio:fin]


# Guiones que cada documento aporta al archivo único. El de comportamiento
# común (filtro por puesto, tira de secciones, revelado) lo sustituye SCRIPT;
# el resto —calculadora de la Tesis, hoja de captura, presentación— viaja tal
# cual porque cada uno se ancla ya a su propio contenedor.
GUIONES = {
    "memoria.html": slice(1, None),
    "marketing.html": slice(1, None),
    "deck.html": slice(0, None),
    "instrumentos/captura.html": slice(0, None),
}


def guiones_propios(nombre, html):
    """Los <script> que un documento añade sobre el de comportamiento común."""
    corte = GUIONES.get(nombre)
    if corte is None:
        return ""
    return "\n".join(re.findall(r"<script>.*?</script>", html, re.S)[corte])


def prefijar(html, prefijo):
    """Evita colisiones de identificadores entre los dos documentos."""
    html = re.sub(r'\bid="([^"]+)"', lambda m: 'id="%s%s"' % (prefijo, m.group(1)), html)
    html = re.sub(r'href="#([^"]+)"', lambda m: 'href="#%s%s"' % (prefijo, m.group(1)), html)
    html = re.sub(r"url\(#([^)]+)\)", lambda m: "url(#%s%s)" % (prefijo, m.group(1)), html)
    return html


def conmutadores(html, propio):
    """Convierte los enlaces entre archivos en conmutadores internos.

    Contempla tanto el enlace al documento completo (`manual.html`) como el
    enlace a una sección concreta (`manual.html#m13`), que de otro modo
    quedaría muerto en el archivo unificado.
    """
    for nombre, (destino, prefijo) in DOCUMENTOS.items():
        if nombre == propio:
            continue

        def sustituir(coincidencia, destino=destino, prefijo=prefijo):
            ancla = coincidencia.group(2)
            if not ancla:
                return 'href="#%s" data-ir-a="%s"' % (destino, destino)
            ancla = prefijo + ancla
            return 'href="#%s" data-ir-a="%s" data-ancla="%s"' % (ancla, destino, ancla)

        html = re.sub(r'href="%s(#([^"]+))?"' % re.escape(nombre), sustituir, html)
    return html


def unificado(estilo_fuentes):
    fuentes = {nombre: (RAIZ / nombre).read_text(encoding="utf-8") for nombre in DOCUMENTOS}

    # la hoja de estilos del manual es un superconjunto de la de las otras páginas
    estilos = "\n".join(re.findall(r"<style>.*?</style>", fuentes["manual.html"], re.S))
    # la capa editorial de la tesis no existe en el manual: se añade aparte
    capa = re.search(r"(/\* =+\n   CAPA EDITORIAL.*?)</style>", fuentes["memoria.html"], re.S)
    assert capa, "no se encuentra la capa editorial de la tesis"
    estilos += "\n<style>\n" + capa.group(1) + "</style>"

    # la hoja de captura trae los suyos, sin colisiones con el sistema común
    hoja = estilos_propios(fuentes["instrumentos/captura.html"], "HOJA DE CAPTURA")
    assert hoja, "no se encuentran los estilos de la hoja de captura"
    estilos += "\n<style>\n" + hoja + "</style>"

    # la presentación sí colisiona —redefine body, table, .eyebrow— y se acota
    deck = estilos_propios(fuentes["deck.html"], ".slide{")
    assert deck, "no se encuentran los estilos de la presentación"
    deck = re.sub(r"^\s*:root\{.*?\n\}", "", deck, count=1, flags=re.S)
    estilos += "\n<style>\n" + escopar(deck, "#doc-deck") + "</style>"

    bloques = []
    for nombre, (ident, prefijo) in DOCUMENTOS.items():
        cuerpo_doc = cuerpo(fuentes[nombre])
        if nombre == "inicio.html":
            for viejo, sustituto in CONTEXTO_UNICO:
                assert cuerpo_doc.count(viejo) == 1, viejo[:50]
                cuerpo_doc = cuerpo_doc.replace(viejo, sustituto, 1)
        if prefijo:
            cuerpo_doc = prefijar(cuerpo_doc, prefijo)
        cuerpo_doc = conmutadores(cuerpo_doc, nombre)
        oculto = "" if ident == "doc-inicio" else " hidden"
        bloques.append('<div class="doc" id="%s"%s>\n%s\n</div>' % (ident, oculto, cuerpo_doc))

    barra = "\n".join(
        '      <button type="button" data-ir-a="%s"%s>%s</button>' % (
            ident, ' aria-current="true"' if ident == "doc-inicio" else "", rotulo)
        for ident, rotulo in ROTULOS)
    conmutador = (
        '<nav class="conmutador" aria-label="Documentos del sistema">\n'
        '  <div class="conmutador__in">\n'
        '    <span class="conmutador__marca">Sistema documental <b>Giraldo</b>'
        '<span>v6.0</span></span>\n'
        '    <div class="conmutador__botones">\n%s\n    </div>\n  </div>\n</nav>' % barra)

    documento = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Documentación completa del Centro de Excelencia Implantológica Giraldo: Tesis de Dirección, Manual Maestro de Operaciones, Protocolo de Experiencia Clínica de la Primera Visita y Otros documentos del sistema, en un solo archivo.">
<title>Documentación Giraldo</title>
{fuentes}
{estilos}
{estilo_doc}
</head>
<body>
{conmutador}
{documentos}
{script}
</body>
</html>
"""
    return documento.format(
        fuentes=estilo_fuentes,
        estilos=estilos,
        estilo_doc=ESTILO_DOC,
        conmutador=conmutador,
        documentos="\n".join(bloques),
        script=SCRIPT + "\n" + "\n".join(
            guiones_propios(nombre, fuentes[nombre]) for nombre in DOCUMENTOS),
    )


def main():
    DESTINO.mkdir(exist_ok=True)
    estilo = None
    for origen, salida in PAGINAS.items():
        print(origen)
        html = (RAIZ / origen).read_text(encoding="utf-8")
        coincidencia = ENLACES_FUENTES.search(html)
        if not coincidencia:
            raise SystemExit(f"No se encontró el enlace a Google Fonts en {origen}")
        if estilo is None:                      # las tres páginas usan las mismas fuentes
            estilo = fuentes_incrustadas(coincidencia.group(1))
        html = ENLACES_FUENTES.sub(lambda _: estilo, html, count=1)
        for otro_origen, otra_salida in PAGINAS.items():
            # en export/ todo queda plano: se admite el «../» que usan las
            # páginas guardadas en subcarpeta para apuntar a la raíz
            html = re.sub(
                r'href="(?:\.\./)?%s(#[^"]*)?"' % re.escape(otro_origen),
                lambda m, s=otra_salida: 'href="%s%s"' % (s, m.group(1) or ""),
                html,
            )
        (DESTINO / salida).write_text(html, encoding="utf-8")
        print(f"  → export/{salida} · {(DESTINO / salida).stat().st_size // 1024} KB")

    print("archivo único")
    (DESTINO / UNIFICADO).write_text(unificado(estilo), encoding="utf-8")
    print(f"  → export/{UNIFICADO} · {(DESTINO / UNIFICADO).stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
