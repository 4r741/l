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
    "memoria.html": "Memoria-Direccion-Giraldo.html",
    "deck.html": "Presentacion-Junta-Giraldo.html",
    "manual.html": "Manual-Maestro-Giraldo-v5.html",
    "index.html": "Protocolo-Primera-Visita-Giraldo.html",
    "otros.html": "Otros-Documentos-Giraldo.html",
}

DOCUMENTOS = {
    "memoria.html": ("doc-memoria", "mem-"),
    "manual.html": ("doc-manual", ""),
    "index.html": ("doc-protocolo", "pv-"),
    "otros.html": ("doc-otros", "ot-"),
}

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

UNIFICADO = "Giraldo-Documentacion-Completa.html"

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
</style>"""


def cuerpo(html):
    """Devuelve el contenido de <body> sin el <script> final."""
    inicio = html.index("<body>") + len("<body>")
    fin = html.rindex("<script>")
    return html[inicio:fin]


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

    bloques = []
    for nombre, (ident, prefijo) in DOCUMENTOS.items():
        cuerpo_doc = cuerpo(fuentes[nombre])
        if prefijo:
            cuerpo_doc = prefijar(cuerpo_doc, prefijo)
        cuerpo_doc = conmutadores(cuerpo_doc, nombre)
        oculto = "" if ident == "doc-memoria" else " hidden"
        bloques.append('<div class="doc" id="%s"%s>\n%s\n</div>' % (ident, oculto, cuerpo_doc))

    documento = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Documentación operativa del Centro de Excelencia Implantológica Giraldo: Manual Maestro de Operaciones, Protocolo de Experiencia Clínica de la Primera Visita y Otros documentos del sistema, en un solo archivo.">
<title>Documentación Giraldo</title>
{fuentes}
{estilos}
{estilo_doc}
</head>
<body>
{documentos}
{script}
</body>
</html>
"""
    return documento.format(
        fuentes=estilo_fuentes,
        estilos=estilos,
        estilo_doc=ESTILO_DOC,
        documentos="\n".join(bloques),
        script=SCRIPT,
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
            html = re.sub(
                r'href="%s(#[^"]*)?"' % re.escape(otro_origen),
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
