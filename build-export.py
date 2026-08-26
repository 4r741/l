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
import json
import pathlib
import html as html_mod
import re
import urllib.request

RAIZ = pathlib.Path(__file__).parent

# La versión no se teclea: sale de version.py, que es el único sitio donde vive.
_v = {}
exec(compile((RAIZ / "version.py").read_text(encoding="utf-8"), "version.py", "exec"), _v)
VERSION, FECHA, CORTA = _v["VERSION"], _v["FECHA"], _v["CORTA"]

DESTINO = RAIZ / "export"

# Los archivos a exportar: nombre de salida, identificador dentro del archivo
# único y prefijo con el que se evitan las colisiones de identificadores.
PAGINAS = {
    "inicio.html": "Giraldo-INICIO-AQUI.html",
    "memoria.html": "Tesis-Direccion-Giraldo-v%s.html" % CORTA,
    "deck.html": "Presentacion-Junta-Giraldo-v%s.html" % CORTA,
    "marketing.html": "Plan-Marketing-Giraldo-v%s.html" % CORTA,
    "manual.html": "Manual-Maestro-Giraldo-v%s.html" % CORTA,
    "index.html": "Protocolo-Primera-Visita-Giraldo-v%s.html" % CORTA,
    "otros.html": "Otros-Documentos-Giraldo-v%s.html" % CORTA,
    "instrumentos/captura.html": "Captura-Linea-Base-Giraldo-v%s.html" % CORTA,
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

CORTOS = {
    "doc-inicio": "Inicio",
    "doc-tesis": "Tesis",
    "doc-deck": "Presentación",
    "doc-marketing": "Marketing",
    "doc-captura": "Captura",
    "doc-manual": "Manual",
    "doc-protocolo": "Protocolo",
    "doc-otros": "Otros",
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

UNIFICADO = "Giraldo-TODO-EN-UNO-v%s.html" % CORTA

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
    document.querySelectorAll(".cabecera [data-ir-a]").forEach(function(b){
      b.setAttribute("aria-current", String(b.dataset.irA === id));
    });
    var activo = document.getElementById(id);
    /* el índice de la cabecera es el del documento abierto, y solo ese */
    document.querySelectorAll(".cabecera .strip").forEach(function(s){
      s.hidden = (s.dataset.de !== id);
    });
    /* nada puede quedar sin revelar al cambiar de documento */
    activo.querySelectorAll(".reveal").forEach(function(el){ el.classList.add("in"); });
    avanzar();
    if(moverScroll) window.scrollTo(0, 0);
    try { history.replaceState(null, "", "#" + id); } catch(e){}
  }
  /* ---- hilo de avance del documento abierto ---- */
  var hilo = document.createElement("div");
  hilo.className = "avance";
  document.body.appendChild(hilo);
  function avanzar(){
    var alto = document.documentElement.scrollHeight - window.innerHeight;
    hilo.style.width = (alto > 40 ? (window.scrollY / alto) * 100 : 0) + "%";
  }
  window.addEventListener("scroll", avanzar, {passive:true});
  window.addEventListener("resize", avanzar);

  var cabecera = document.querySelector(".cabecera");
  function medirCabecera(){
    if(!cabecera) return;
    var alto = Math.round(cabecera.getBoundingClientRect().height) + "px";
    document.documentElement.style.setProperty("--cabecera", alto);
    /* la hoja base reserva ese hueco por encima de todo destino con
       identificador; aquí la barra es esta, no la de los documentos sueltos */
    document.documentElement.style.setProperty("--barra", alto);
  }
  medirCabecera();
  window.addEventListener("resize", medirCabecera);
  if("ResizeObserver" in window) new ResizeObserver(medirCabecera).observe(cabecera);


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
    boton("Índice", "Ir al índice general del sistema", LISTA)
      .addEventListener("click", function(){
        mostrar("doc-inicio", true);
        var idx = document.querySelector(".idx__mando");
        if(idx) idx.scrollIntoView({behavior: quieto ? "auto" : "smooth", block:"start"});
        else window.scrollTo({top:0, behavior: quieto ? "auto" : "smooth"});
      });
    boton("Arriba", "Volver al principio del documento", FLECHA)
      .addEventListener("click", function(){
        window.scrollTo({top:0, behavior: quieto ? "auto" : "smooth"});
      });
    document.body.appendChild(caja);
    var visible = false;
    function mirar(){
      var deck = document.getElementById("doc-deck");
      var enDeck = deck && deck.style.display !== "none" && deck.offsetParent !== null;
      var debe = !enDeck && window.scrollY > window.innerHeight * 1.2;
      if(debe !== visible){ visible = debe; caja.classList.toggle("se-ve", debe); }
    }
    mirar();
    window.addEventListener("scroll", mirar, {passive:true});
    window.addEventListener("resize", mirar);
  })();

  /* ---- teclado: se pasa de documento como se pasa de capítulo ---- */
  document.addEventListener("keydown", function(e){
    if(e.ctrlKey || e.metaKey || e.altKey) return;
    var t = e.target;
    if(t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.isContentEditable)) return;
    /* Se usan corchetes y no flechas a propósito: la presentación conduce sus
       diapositivas con las flechas, y quien está dentro de ella tiene que poder
       salir con el teclado igual que entró. */
    if(e.key !== "[" && e.key !== "]") return;
    var abierto = docs.filter(function(d){ return !d.hidden; })[0];
    if(!abierto) return;
    var orden = docs.map(function(d){ return d.id; });
    var i = orden.indexOf(abierto.id) + (e.key === "]" ? 1 : -1);
    if(i < 0 || i >= orden.length) return;
    e.preventDefault();
    mostrar(orden[i], true);
  });

  /* ------------------------------------------------------------------------
     Buscador. La tira de secciones se corta por la derecha —la Tesis tiene
     treinta y cinco entradas y en pantalla caben doce—, así que llegar a un
     apartado concreto obligaba a rascar hasta encontrarlo. Aquí se escriben dos
     letras y se llega, sin salir del teclado y sin saber en qué documento está.

     Busca en el texto completo, no solo en los titulares: quien escribe
     «descuento» o «miedo» quiere el apartado que habla de eso, y ese apartado
     casi nunca se llama así. El texto no se incrusta —ya está en la página—,
     se lee del propio documento la primera vez que hace falta y se guarda.
     ------------------------------------------------------------------------ */
  var paleta = document.getElementById("paleta");
  var campo = document.getElementById("paleta-texto");
  var lista = document.getElementById("paleta-lista");
  var cuenta = document.getElementById("paleta-cuenta");
  var indice = window.__INDICE__ || [];
  var filas = [], elegida = -1, ultimoFoco = null, guardado = {}, crudos = {};

  /* Sin tildes y en minúscula: nadie escribe «asimetría» con tilde al buscar.
     Se traduce carácter a carácter en vez de descomponer en NFD porque la
     longitud tiene que conservarse: las posiciones que encuentra la búsqueda se
     usan luego para recortar el texto original, con sus tildes y sus mayúsculas. */
  var CON = "áàäâãéèëêíìïîóòöôõúùüûñçÁÀÄÂÃÉÈËÊÍÌÏÎÓÒÖÔÕÚÙÜÛÑÇ";
  var SIN = "aaaaaeeeeiiiiooooouuuuncaaaaaeeeeiiiiooooouuuunc";
  function llano(s){
    var fuera = "";
    for(var i = 0; i < s.length; i++){
      var c = s.charAt(i), j = CON.indexOf(c);
      fuera += j > -1 ? SIN.charAt(j) : c.toLowerCase();
    }
    return fuera;
  }
  function escapar(s){
    return s.replace(/[&<>]/g, function(c){ return {"&":"&amp;","<":"&lt;",">":"&gt;"}[c]; });
  }
  /* Principio de palabra: si no, «acta» aparece dentro de «exactamente». */
  function donde(texto, trozo){
    var i = texto.indexOf(trozo);
    while(i > -1){
      var antes = i === 0 ? " " : texto.charAt(i - 1);
      if(!/[a-z0-9]/.test(antes)) return i;
      i = texto.indexOf(trozo, i + 1);
    }
    return -1;
  }
  function casan(texto, trozos){
    for(var i = 0; i < trozos.length; i++) if(donde(texto, trozos[i]) < 0) return false;
    return true;
  }

  /* El texto de un apartado: del titular al siguiente titular del mismo rango.
     Se pasa por el marcado y no por textContent porque textContent pega las
     palabras de bloques contiguos —«es amplioansiedad»— y eso ensucia el
     retazo que se le enseña al lector. */
  var cajon = document.createElement("div");
  function plano(html){
    cajon.innerHTML = html.replace(/<[^>]+>/g, " ");
    return (cajon.textContent || "").replace(/\s+/g, " ").trim();
  }
  function crudoDe(ancla){
    if(crudos[ancla] !== undefined) return crudos[ancla];
    var el = document.getElementById(ancla), t = "";
    if(el){
      if(/^H[23]$/.test(el.tagName)){
        var tope = el.tagName, n = el.nextElementSibling, trozos = [el.outerHTML];
        while(n && !(/^H[23]$/.test(n.tagName) && n.tagName <= tope)){
          trozos.push(n.outerHTML); n = n.nextElementSibling;
        }
        t = plano(trozos.join(" "));
      } else {
        t = plano(el.innerHTML || "");
      }
    }
    crudos[ancla] = t.slice(0, 6000);
    return crudos[ancla];
  }
  function textoDe(ancla){
    if(guardado[ancla] === undefined) guardado[ancla] = llano(crudoDe(ancla));
    return guardado[ancla];
  }

  function resaltar(texto, trozos){
    if(!trozos.length) return escapar(texto);
    var plano = llano(texto), mejor = -1, largo = 0;
    trozos.forEach(function(p){
      var i = donde(plano, p);
      if(i > -1 && (mejor < 0 || i < mejor)){ mejor = i; largo = p.length; }
    });
    if(mejor < 0) return escapar(texto);
    return escapar(texto.slice(0, mejor)) + "<mark>" +
           escapar(texto.slice(mejor, mejor + largo)) + "</mark>" +
           escapar(texto.slice(mejor + largo));
  }

  /* Un trozo del cuerpo alrededor de la primera coincidencia, para que se vea
     por qué sale ese resultado sin tener que abrirlo. */
  function retazo(ancla, trozos){
    var texto = textoDe(ancla), i = -1;
    for(var n = 0; n < trozos.length && i < 0; n++) i = donde(texto, trozos[n]);
    if(i < 0) return "";
    var crudo = crudoDe(ancla);
    /* Delante de la coincidencia va poco contexto y detrás bastante: la
       línea se recorta por la derecha con puntos suspensivos, y con cuarenta y
       seis caracteres de entradilla la palabra buscada se salía del recorte en
       una pantalla estrecha. Lo que hay que ver siempre es la palabra. */
    var margen = window.innerWidth < 720 ? 18 : 40;
    var desde = Math.max(0, i - margen), hasta = Math.min(crudo.length, i + 96);
    var trozo = (desde ? "…" : "") + crudo.slice(desde, hasta).trim() +
                (hasta < crudo.length ? "…" : "");
    return resaltar(trozo, trozos);
  }

  /* Cuántas veces aparece el trozo más largo: sirve de relevancia sin montar
     un índice invertido para un archivo que se abre con doble clic. */
  function veces(texto, trozo){
    if(!trozo) return 0;
    var n = 0, desde = 0;
    while(n < 40){
      var i = donde(texto.slice(desde), trozo);
      if(i < 0) break;
      n++;
      desde += i + trozo.length;
    }
    return n;
  }

  function pintar(consulta){
    var trozos = llano(consulta).split(/\s+/).filter(Boolean);
    var largo = trozos.slice().sort(function(a, b){ return b.length - a.length; })[0] || "";
    var grupos = [];

    indice.forEach(function(doc){
      var titulo = llano(doc.titulo), propias = [];
      if(!trozos.length || casan(titulo, trozos))
        propias.push({doc: doc.doc, ancla: null, rotulo: doc.titulo, esDoc: true,
                      retazo: "", punto: 1000});
      doc.entradas.forEach(function(e){
        var rot = llano(e.rotulo);
        if(!trozos.length){
          propias.push({doc: doc.doc, ancla: e.ancla, rotulo: e.rotulo, esDoc: false,
                        retazo: "", punto: 0});
          return;
        }
        if(casan(rot + " " + titulo, trozos)){
          /* El titular manda sobre el cuerpo, y empezar por el término manda
             sobre mencionarlo a mitad de frase. */
          var punto = 500 + (donde(rot, largo) === 0 ? 60 : 0) +
                      (casan(rot, trozos) ? 30 : 0);
          propias.push({doc: doc.doc, ancla: e.ancla, rotulo: e.rotulo, esDoc: false,
                        retazo: "", punto: punto});
          return;
        }
        var cuerpo = textoDe(e.ancla);
        if(casan(cuerpo, trozos))
          propias.push({doc: doc.doc, ancla: e.ancla, rotulo: e.rotulo, esDoc: false,
                        retazo: retazo(e.ancla, trozos), punto: 100 + veces(cuerpo, largo)});
      });
      if(!propias.length) return;
      if(trozos.length){
        propias.sort(function(a, b){ return b.punto - a.punto; });
        grupos.push({doc: doc, filas: propias,
                     punto: propias.reduce(function(m, r){ return Math.max(m, r.punto); }, 0)});
      } else {
        grupos.push({doc: doc, filas: propias, punto: 0});
      }
    });
    /* Con búsqueda, manda la relevancia; sin ella, el orden de los documentos. */
    if(trozos.length) grupos.sort(function(a, b){ return b.punto - a.punto; });

    var html = [], total = 0;
    filas = [];
    grupos.forEach(function(g){
      html.push('<p class="paleta__grupo">' + escapar(g.doc.titulo) + "</p>");
      g.filas.forEach(function(r){
        var i = filas.length;
        filas.push(r);
        html.push('<button type="button" class="paleta__fila' + (r.esDoc ? " paleta__fila--doc" : "") +
          '" role="option" data-i="' + i + '"><span><b>' + resaltar(r.rotulo, trozos) + "</b>" +
          (r.retazo ? "<em>" + r.retazo + "</em>" : "") + "</span>" +
          (r.esDoc ? "<i>abrir el documento</i>" : "") + "</button>");
        total++;
      });
    });
    lista.innerHTML = html.length ? html.join("") :
      '<p class="paleta__vacio">Nada con «' + escapar(consulta) + "». Pruebe con menos palabras.</p>";
    cuenta.textContent = total ? total + (total === 1 ? " resultado" : " resultados") : "";
    lista.scrollTop = 0;
    marcar(filas.length ? 0 : -1, false);
  }

  function marcar(i, mover){
    elegida = i;
    var botones = lista.querySelectorAll(".paleta__fila");
    botones.forEach(function(b, n){ b.setAttribute("aria-selected", String(n === i)); });
    if(mover && botones[i]) botones[i].scrollIntoView({block:"nearest"});
  }

  function ir(r){
    if(!r) return;
    cerrarPaleta();
    mostrar(r.doc, !r.ancla);
    if(r.ancla){
      var destino = document.getElementById(r.ancla);
      if(destino) destino.scrollIntoView({behavior:"instant", block:"start"});
      try { history.replaceState(null, "", "#" + r.ancla); } catch(e){}
    }
  }

  function abrirPaleta(){
    if(!paleta) return;
    ultimoFoco = document.activeElement;
    paleta.hidden = false;
    document.body.style.overflow = "hidden";
    campo.value = "";
    pintar("");
    campo.focus();
  }
  function cerrarPaleta(){
    if(!paleta || paleta.hidden) return;
    paleta.hidden = true;
    document.body.style.overflow = "";
    if(ultimoFoco && ultimoFoco.focus) ultimoFoco.focus();
  }

  if(paleta){
    var abrir = document.getElementById("abrir-buscador");
    if(abrir) abrir.addEventListener("click", abrirPaleta);
    paleta.querySelectorAll("[data-cerrar]").forEach(function(el){
      el.addEventListener("click", cerrarPaleta);
    });
    campo.addEventListener("input", function(){ pintar(campo.value); });
    lista.addEventListener("click", function(e){
      var fila = e.target.closest(".paleta__fila");
      if(fila) ir(filas[+fila.dataset.i]);
    });
    lista.addEventListener("mousemove", function(e){
      var fila = e.target.closest(".paleta__fila");
      if(fila && +fila.dataset.i !== elegida) marcar(+fila.dataset.i, false);
    });
    campo.addEventListener("keydown", function(e){
      if(e.key === "ArrowDown" || e.key === "ArrowUp"){
        e.preventDefault();
        if(!filas.length) return;
        marcar((elegida + (e.key === "ArrowDown" ? 1 : filas.length - 1)) % filas.length, true);
      } else if(e.key === "Enter"){
        e.preventDefault(); ir(filas[elegida]);
      } else if(e.key === "Escape"){
        e.preventDefault(); cerrarPaleta();
      }
    });
    document.addEventListener("keydown", function(e){
      if(e.key === "Escape" && !paleta.hidden){ cerrarPaleta(); return; }
      var t = e.target;
      if(t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.isContentEditable)) return;
      /* La barra inclinada es el gesto que todo el mundo tiene aprendido; se
         admite además Ctrl+K y Cmd+K, que es el otro. */
      if(e.key === "/" && !e.ctrlKey && !e.metaKey){ e.preventDefault(); abrirPaleta(); }
      else if(e.key.toLowerCase() === "k" && (e.ctrlKey || e.metaKey)){ e.preventDefault(); abrirPaleta(); }
    });
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
  document.querySelectorAll(".cabecera .strip").forEach(function(s){
    s.hidden = (s.dataset.de !== "doc-inicio");
  });
  avanzar();
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
    var tira = document.querySelector('.cabecera .strip[data-de="' + doc.id + '"]');
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

/* ---------------------------------------------------------------------------
   Cabecera única. El archivo no depende de ningún enlace externo y no apila
   barras: una fila con la marca y los documentos, otra con el índice de
   secciones del documento que esté abierto.
   --------------------------------------------------------------------------- */
:root{--cabecera:92px}  /* valor de arranque; el guion lo mide y lo corrige */
.cabecera{position:sticky;top:0;z-index:95}
.cabecera__in{
  width:min(100% - 2rem,1180px);margin-inline:auto;
  display:flex;align-items:center;gap:.3rem .9rem;
}
.cabecera__fila{
  background:var(--ink);color:var(--surface);
  border-bottom:1px solid rgba(247,248,245,.14);
}
.cabecera__fila .cabecera__in{flex-wrap:wrap;padding:.52rem 0}
.cabecera__marca{
  font-family:var(--f-display);font-size:.98rem;white-space:nowrap;
}
.cabecera__marca b{font-weight:600}
.cabecera__marca span{
  font-family:var(--f-mono);font-size:.6rem;letter-spacing:.14em;text-transform:uppercase;
  color:#7FD3C9;margin-left:.5rem;
}
.cabecera__docs{display:flex;gap:2px;flex-wrap:wrap;margin-left:auto;justify-content:flex-end}
.cabecera__docs button{
  font:inherit;font-family:var(--f-mono);font-size:.62rem;letter-spacing:.1em;
  text-transform:uppercase;background:transparent;border:1px solid transparent;
  color:rgba(247,248,245,.72);padding:.36rem .55rem;border-radius:999px;cursor:pointer;
  white-space:nowrap;
  transition:color .16s ease,border-color .16s ease,background .16s ease;
}
.cabecera__docs button:hover{color:#7FD3C9;border-color:rgba(127,211,201,.4)}
.cabecera__docs button[aria-current="true"]{
  background:rgba(127,211,201,.16);border-color:#7FD3C9;color:#7FD3C9;
}

/* Segunda fila: el índice del documento activo. Si el documento no tiene
   índice —la presentación— la fila desaparece y no deja un hueco vacío. */
.cabecera__indice{
  background:var(--paper);border-bottom:1px solid var(--line);
}
/* Altura fija: si la fila cambia de alto al conmutar, el texto pega un salto y
   se nota la costura. Todos los índices ocupan lo mismo, tengan lo que tengan. */
.cabecera__indice .cabecera__in{display:block;height:44px}
.cabecera__indice .strip{height:44px;align-items:center;padding:0}
.cabecera__indice .strip a{padding:.3rem .58rem 0;border-top-width:2px}
.strip--nota{
  display:flex;gap:.4rem 1.5rem;flex-wrap:nowrap;align-items:center;overflow-x:auto;
  white-space:nowrap;scrollbar-width:none;
  font-family:var(--f-mono);font-size:.66rem;letter-spacing:.08em;
  text-transform:uppercase;color:var(--muted);
}
.strip--nota::-webkit-scrollbar{display:none}
.strip--nota>*{flex:0 0 auto}
.strip--nota b{color:var(--accent-ink);font-weight:400;letter-spacing:.1em}
.strip--nota kbd{
  font:inherit;background:var(--surface);border:1px solid var(--line);
  border-radius:3px;padding:.05rem .3rem;color:var(--ink-2);
}

/* Hilo de avance: dice cuánto queda del documento abierto sin ocupar sitio. */
.avance{
  position:fixed;top:0;left:0;height:2px;width:0;z-index:99;
  background:var(--accent);transition:width .12s linear;
}
@media(prefers-reduced-motion:reduce){.avance{transition:none}}

/* La presentación ocupa la altura libre bajo la cabecera. */
#doc-deck .deck{height:calc(100vh - var(--cabecera))}
#doc-deck .hud{bottom:14px}

@media(max-width:700px){
  /* La fila de documentos se plegaba en tres líneas y la cabecera se comía la
     quinta parte de la pantalla de un teléfono, en un archivo que se lee casi
     todo hacia abajo. Ahora la marca y el buscador comparten renglón y los ocho
     documentos se desplazan en uno solo, con su desvanecido diciendo por dónde
     sigue la fila. */
  .cabecera__fila .cabecera__in{flex-wrap:wrap;gap:.3rem .6rem;padding:.44rem 0}
  .cabecera__marca{font-size:.86rem;margin:0}
  .buscador{margin-left:auto}
  .cabecera__docs{
    order:3;width:100%;margin-left:0;justify-content:flex-start;
    flex-wrap:nowrap;overflow-x:auto;scrollbar-width:none;
    --vel-izq:0px;--vel-der:0px;
    -webkit-mask-image:linear-gradient(to right,transparent 0,#000 var(--vel-izq),
                       #000 calc(100% - var(--vel-der)),transparent 100%);
    mask-image:linear-gradient(to right,transparent 0,#000 var(--vel-izq),
               #000 calc(100% - var(--vel-der)),transparent 100%);
  }
  .cabecera__docs::-webkit-scrollbar{display:none}
  .cabecera__docs.hay-izq{--vel-izq:26px}
  .cabecera__docs.hay-der{--vel-der:26px}
}


/* ---------------------------------------------------------------------------
   Buscador de la cabecera y paleta de índice completo
   --------------------------------------------------------------------------- */
.buscador{
  flex:0 0 auto;display:flex;align-items:center;gap:.45rem;font:inherit;cursor:pointer;
  font-family:var(--f-mono);font-size:.64rem;letter-spacing:.09em;text-transform:uppercase;
  background:rgba(247,248,245,.07);border:1px solid rgba(247,248,245,.22);
  color:rgba(247,248,245,.72);padding:.34rem .6rem;border-radius:999px;
  transition:border-color .16s ease,color .16s ease,background .16s ease;
}
.buscador:hover{color:#7FD3C9;border-color:rgba(127,211,201,.55);background:rgba(127,211,201,.1)}
.buscador kbd{
  font:inherit;border:1px solid rgba(247,248,245,.28);border-radius:3px;
  padding:0 .28rem;line-height:1.35;
}

.paleta{position:fixed;inset:0;z-index:200;display:flex;justify-content:center;
  align-items:flex-start;padding:clamp(1rem,7vh,5rem) 1rem 1rem}
.paleta[hidden]{display:none}
.paleta__velo{position:absolute;inset:0;background:rgba(11,26,32,.55);backdrop-filter:blur(2px)}
.paleta__caja{
  position:relative;width:min(100%,720px);max-height:min(72vh,640px);
  display:flex;flex-direction:column;background:var(--paper);
  border:1px solid var(--line);box-shadow:0 24px 64px rgba(11,26,32,.28);
}
.paleta__campo{display:flex;align-items:center;gap:.7rem;padding:.9rem 1.1rem;
  border-bottom:1px solid var(--line);color:var(--muted)}
.paleta__campo input{
  flex:1;font:inherit;font-family:var(--f-body);font-size:1.02rem;color:var(--ink);
  background:transparent;border:0;outline:none;min-width:0;
}
.paleta__campo input::placeholder{color:var(--muted)}
.paleta__campo input::-webkit-search-cancel-button{display:none}
.paleta__cerrar{
  font:inherit;font-family:var(--f-mono);font-size:.62rem;letter-spacing:.1em;
  text-transform:uppercase;background:var(--surface);border:1px solid var(--line);
  border-radius:3px;color:var(--muted);padding:.14rem .4rem;cursor:pointer;
}
.paleta__cerrar:hover{color:var(--ink);border-color:var(--ink-2)}

.paleta__lista{overflow-y:auto;padding:.4rem 0;scrollbar-width:thin}
.paleta__grupo{
  font-family:var(--f-mono);font-size:.6rem;letter-spacing:.15em;text-transform:uppercase;
  color:var(--muted);padding:.85rem 1.1rem .3rem;
}
.paleta__grupo:first-child{padding-top:.35rem}
.paleta__fila{
  display:flex;align-items:baseline;gap:.8rem;width:100%;text-align:left;
  font:inherit;background:transparent;border:0;cursor:pointer;
  padding:.44rem 1.1rem;color:var(--ink);border-left:2px solid transparent;
}
.paleta__fila:hover{background:var(--surface)}
.paleta__fila[aria-selected="true"]{background:var(--accent-soft);border-left-color:var(--accent)}
.paleta__fila>span{min-width:0;display:block}
.paleta__fila b{font-weight:500;font-size:.95rem;display:block}
.paleta__fila em{
  display:block;font-style:normal;font-size:.82rem;color:var(--muted);
  margin-top:.12rem;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;
}
.paleta__fila em mark{background:rgba(14,143,132,.18);color:var(--ink-2);border-radius:2px}
.paleta__fila b mark{background:rgba(14,143,132,.2);color:inherit;padding:0 .05em;border-radius:2px}
.paleta__fila i{
  margin-left:auto;font-style:normal;font-family:var(--f-mono);font-size:.6rem;
  letter-spacing:.11em;text-transform:uppercase;color:var(--muted);white-space:nowrap;
}
.paleta__fila--doc b{font-family:var(--f-display);font-size:1.05rem}
.paleta__vacio{padding:1.4rem 1.1rem;color:var(--muted);font-size:.95rem}
.paleta__pie{
  display:flex;gap:1.1rem;align-items:center;padding:.5rem 1.1rem;
  border-top:1px solid var(--line);background:var(--surface);
  font-family:var(--f-mono);font-size:.6rem;letter-spacing:.1em;
  text-transform:uppercase;color:var(--muted);
}
.paleta__pie kbd{
  font:inherit;background:var(--paper);border:1px solid var(--line);border-radius:3px;
  padding:0 .3rem;margin-right:.2rem;color:var(--ink-2);
}
.paleta__cuenta{margin-left:auto}
.paleta__tacto{display:none}
@media(max-width:700px){
  .buscador span{display:none}
  .paleta__caja{max-height:82vh}
}
/* Donde se toca con el dedo no hay Esc, ni flechas, ni intro. El pie dejaba de
   explicar cómo se usa esto y pasaba a explicar teclas que no existen, y el
   único botón para cerrar decía «esc», que en un teléfono no es un botón: es
   una palabra. */
@media(pointer:coarse){
  .paleta__pie span:not(.paleta__tacto):not(.paleta__cuenta){display:none}
  .paleta__tacto{display:inline;text-transform:none;letter-spacing:.02em;font-size:.68rem}
  .paleta__cerrar{
    font-size:0;min-width:44px;min-height:44px;
    display:flex;align-items:center;justify-content:center;
  }
  .paleta__cerrar::before{
    content:"\2715";font-size:.95rem;letter-spacing:0;line-height:1;
  }
}
@media print{.paleta{display:none!important}}

@media print{
  .cabecera,.avance{display:none}
  .doc[hidden]{display:none!important}
  #doc-deck .deck{height:auto}
}
</style>
"""





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
    # la portada solo aporta el del índice, y ahí es donde más falta hace: sin
    # él el filtro de las 649 líneas queda muerto justo en el archivo único
    "inicio.html": slice(0, None),
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


# Fila de índice para los dos documentos que no tienen secciones. No es relleno:
# dice lo que a esa altura le hace falta saber a quien está mirando.
SIN_INDICE = {
    # La portada llevaba aquí una fila de instrucciones —qué barra hace qué, qué
    # tecla pulsar— que en un documento de gobierno no pinta nada. En su lugar,
    # lo que identifica al documento: qué es y para quién.
    "doc-inicio": ("<b>Sistema documental del Centro de Excelencia Implantológica Giraldo</b>"
                   "<span>Rúa Bolivia nº 2 · Vigo</span>"
                   "<span>Uso interno y confidencial</span>"),
    "doc-deck": ("<b>43 diapositivas · 16:9</b>"
                 "<span><kbd>←</kbd> <kbd>→</kbd> <kbd>espacio</kbd> pasar</span>"
                 "<span><kbd>N</kbd> guion del ponente</span>"
                 "<span><kbd>E</kbd> ruta corta de doce</span>"
                 "<span><kbd>Inicio</kbd> <kbd>Fin</kbd> primera y última</span>"),
}


# ---------------------------------------------------------------------------
# El índice completo, buscable. La tira de secciones se corta por la derecha —la
# Tesis tiene treinta y cinco entradas y en pantalla caben doce—, así que ir a un
# apartado concreto obligaba a rascar horizontalmente hasta encontrarlo. Esto lo
# sustituye por lo que uno espera: escribir dos letras y llegar.
# ---------------------------------------------------------------------------
PALETA = """
<div class="paleta" id="paleta" hidden>
  <div class="paleta__velo" data-cerrar></div>
  <div class="paleta__caja" role="dialog" aria-modal="true" aria-label="Buscar en los siete documentos">
    <div class="paleta__campo">
      <svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true">
        <circle cx="7" cy="7" r="4.6" fill="none" stroke="currentColor" stroke-width="1.6"/>
        <path d="M10.4 10.4 L14.4 14.4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
      </svg>
      <input type="search" id="paleta-texto" autocomplete="off" spellcheck="false"
             placeholder="Escriba un apartado, un documento o una palabra">
      <button type="button" class="paleta__cerrar" data-cerrar aria-label="Cerrar">esc</button>
    </div>
    <div class="paleta__lista" id="paleta-lista" role="listbox"></div>
    <div class="paleta__pie">
      <span><kbd>&#8593;</kbd><kbd>&#8595;</kbd> moverse</span>
      <span><kbd>&#8629;</kbd> abrir</span>
      <span><kbd>esc</kbd> cerrar</span>
      <span class="paleta__tacto">Toque un resultado para abrirlo</span>
      <span class="paleta__cuenta" id="paleta-cuenta" role="status" aria-live="polite" aria-atomic="true"></span>
    </div>
  </div>
</div>
"""


def solo_texto(html):
    """Texto plano de un fragmento, en una línea y sin entidades."""
    return re.sub(r"\s+", " ", html_mod.unescape(re.sub(r"<[^>]+>", " ", html))).strip()


def titulares(cuerpo):
    """Todo titular del documento con su ancla, para que el buscador llegue hondo.

    Con solo las entradas de la tira, buscar «acta» no encontraba el «Anexo A ·
    Acuerdos», que es exactamente lo que uno busca cuando escribe «acta». Aquí
    se recorre el cuerpo entero y se empareja cada <h2> y <h3> con el
    identificador más cercano por encima, que es el que sirve de destino.
    """
    anclas = [(m.start(), m.group(1)) for m in re.finditer(r'\sid="([^"]+)"', cuerpo)]
    fuera = []
    for m in re.finditer(r"<h([23])\b[^>]*>(.*?)</h\1>", cuerpo, re.S):
        rotulo = solo_texto(m.group(2))
        if not rotulo or len(rotulo) > 110:
            continue
        propio = re.search(r'\sid="([^"]+)"', m.group(0))
        if propio:
            fuera.append((propio.group(1), rotulo))
            continue
        previas = [a for pos, a in anclas if pos < m.start()]
        if previas:
            fuera.append((previas[-1], rotulo))
    vistas, limpias = set(), []
    for ancla, rotulo in fuera:
        clave = (ancla, rotulo.lower())
        if clave in vistas:
            continue
        vistas.add(clave)
        limpias.append({"ancla": ancla, "rotulo": rotulo})
    return limpias


def descabezar(html, ident):
    """Quita la cabecera propia del documento y devuelve su índice de secciones.

    En el archivo único solo puede haber una cabecera. La del documento repetía
    la marca, repetía los enlaces a los demás documentos —que el conmutador ya
    ofrece— y dejaba tres barras apiladas encima del texto. El índice de
    secciones sí sirve, así que sube a la cabecera común y se muestra cuando su
    documento está activo.
    """
    cabecera = re.search(r'<header class="topbar">.*?</header>', html, re.S)
    if cabecera:
        html = html.replace(cabecera.group(0), "", 1)
    tira = re.search(r'<nav class="strip"[^>]*>.*?</nav>',
                     cabecera.group(0) if cabecera else "", re.S)
    if tira:
        marcado = re.sub(r'\sid="[^"]*"', "", tira.group(0), count=1)
        marcado = marcado.replace('<nav class="strip"', '<nav class="strip" data-de="%s"' % ident, 1)
        entradas = [{"ancla": a, "rotulo": re.sub(r"\s+", " ", html_mod.unescape(r)).strip()}
                    for a, r in re.findall(r'<a href="#([^"]+)">(.*?)</a>', marcado, re.S)]
        return html, "      " + marcado, entradas
    # La portada y la presentación no tienen índice de secciones. Si su fila se
    # queda vacía, la cabecera cambia de altura al conmutar y el texto pega un
    # salto: es la última costura que quedaba. Se les da una fila propia.
    suplente = SIN_INDICE.get(ident)
    if not suplente:
        return html, "", []
    return html, ('      <nav class="strip strip--nota" data-de="%s">%s</nav>' % (ident, suplente)), []


def unificado(estilo_fuentes):
    fuentes = {nombre: (RAIZ / nombre).read_text(encoding="utf-8") for nombre in DOCUMENTOS}

    # la hoja de estilos del manual es un superconjunto de la de las otras páginas
    estilos = "\n".join(re.findall(r"<style>.*?</style>", fuentes["manual.html"], re.S))
    # la capa editorial de la tesis no existe en el manual: se añade aparte
    capa = re.search(r"(/\* =+\n   CAPA EDITORIAL.*?)</style>", fuentes["memoria.html"], re.S)
    assert capa, "no se encuentra la capa editorial de la tesis"
    estilos += "\n<style>\n" + capa.group(1) + "</style>"

    # La portada trae los suyos —la rejilla de fichas y el índice general— y no
    # viajaban al archivo único: el índice salía como una lista numerada sin
    # formato. Sus clases son propias, así que entran sin acotar.
    portada = estilos_propios(fuentes["inicio.html"], ".puerta__ficha{")
    assert portada, "no se encuentran los estilos de la portada"
    estilos += "\n<style>\n" + portada + "</style>"

    # la hoja de captura trae los suyos, sin colisiones con el sistema común
    hoja = estilos_propios(fuentes["instrumentos/captura.html"], "HOJA DE CAPTURA")
    assert hoja, "no se encuentran los estilos de la hoja de captura"
    estilos += "\n<style>\n" + hoja + "</style>"

    # la presentación sí colisiona —redefine body, table, .eyebrow— y se acota
    deck = estilos_propios(fuentes["deck.html"], ".slide{")
    assert deck, "no se encuentran los estilos de la presentación"
    deck = re.sub(r"^\s*:root\{.*?\n\}", "", deck, count=1, flags=re.S)
    estilos += "\n<style>\n" + escopar(deck, "#doc-deck") + "</style>"

    bloques, tiras, indice = [], [], []
    for nombre, (ident, prefijo) in DOCUMENTOS.items():
        cuerpo_doc = cuerpo(fuentes[nombre])
        if prefijo:
            cuerpo_doc = prefijar(cuerpo_doc, prefijo)
        cuerpo_doc = conmutadores(cuerpo_doc, nombre)
        # Aquí se cierra la fisura: cada documento traía su propia cabecera con
        # su marca y sus enlaces cruzados, de modo que el archivo único
        # apilaba tres barras y repetía la navegación dos veces. Se le quita la
        # cabecera y su índice de secciones sube a la cabecera común.
        cuerpo_doc, tira, entradas = descabezar(cuerpo_doc, ident)
        if tira:
            tiras.append(tira)
        vistos = {e["ancla"] for e in entradas}
        for h in titulares(cuerpo_doc):
            if h["ancla"] not in vistos:
                vistos.add(h["ancla"])
                entradas.append(h)
        indice.append({"doc": ident, "titulo": dict(ROTULOS)[ident], "entradas": entradas})
        oculto = "" if ident == "doc-inicio" else " hidden"
        bloques.append('<div class="doc" id="%s"%s>\n%s\n</div>' % (ident, oculto, cuerpo_doc))

    barra = "\n".join(
        '        <button type="button" data-ir-a="%s"%s title="%s">%s</button>' % (
            ident, ' aria-current="true"' if ident == "doc-inicio" else "",
            rotulo, CORTOS[ident])
        for ident, rotulo in ROTULOS)
    conmutador = (
        '<header class="cabecera">\n'
        '  <div class="cabecera__fila">\n'
        '    <div class="cabecera__in">\n'
        '      <span class="cabecera__marca">Sistema documental <b>Giraldo</b>'
        '<span>v' + VERSION + '</span></span>\n'
        '      <nav class="cabecera__docs" aria-label="Documentos del sistema">\n%s\n'
        '      </nav>\n'
        '      <button type="button" class="buscador" id="abrir-buscador" '
        'aria-haspopup="dialog">'
        '<svg width="13" height="13" viewBox="0 0 16 16" aria-hidden="true">'
        '<circle cx="7" cy="7" r="4.6" fill="none" stroke="currentColor" stroke-width="1.6"/>'
        '<path d="M10.4 10.4 L14.4 14.4" stroke="currentColor" stroke-width="1.6" '
        'stroke-linecap="round"/></svg>'
        '<span>Buscar</span><kbd>/</kbd></button>\n'
        '    </div>\n  </div>\n'
        '  <div class="cabecera__indice">\n    <div class="cabecera__in">\n%s\n'
        '    </div>\n  </div>\n</header>\n' % (barra, "\n".join(tiras))) + PALETA

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
        script=('<script>window.__INDICE__ = ' + json.dumps(indice, ensure_ascii=False)
                + ';</script>\n' + SCRIPT) + "\n" + "\n".join(
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
