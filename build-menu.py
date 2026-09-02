#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pone el menú nuevo en los seis documentos y unifica la cuenta.

    python3 build-menu.py

Dos cosas, y las dos vienen del mismo sitio. La primera: el índice de secciones
deja de ser una fila que se arrastra a lo ancho y pasa a ser un panel que se
abre. Treinta y cuatro apartados no caben en una línea de mil doscientos
píxeles, y la fila no lo decía: se cortaba y ya. La segunda: una sola cuenta.
La memoria numeraba «00, 0.1, 01» mezclando las partes en romano con los
apartados; el marketing arrastraba un «apartado 3» que se coló al quitar el
símbolo de sección; otros documentos escribía «1 ·» y el manual, nada. Ahora
los apartados llevan dos cifras, las partes son encabezados del panel y los
anexos van con letra.

El guion es idempotente: si se pasa dos veces, la segunda no cambia nada.
"""
import pathlib
import re
import sys
import types

RAIZ = pathlib.Path(__file__).parent

# El modelo se lee y se ejecuta, no se importa. Con `import` Python guarda el
# resultado compilado en __pycache__ y lo reutiliza si el archivo le parece el
# mismo; una edición del mismo tamaño dentro del mismo segundo se lo parece, y
# entonces el menú se dibuja con un modelo viejo sin que nada avise. Pasó: la
# entrega salió con «05 Mapa competitivo» donde el modelo decía 03.
menu = types.ModuleType("menu")
menu.__file__ = str(RAIZ / "menu.py")
exec(compile((RAIZ / "menu.py").read_text(encoding="utf-8"), menu.__file__, "exec"),
     menu.__dict__)

# Retoques del cuerpo para que el texto diga lo mismo que el menú. Cada uno es
# una pareja (lo que hay, lo que debe haber) y se exige que aparezca: si un
# retoque deja de encontrar su objetivo es que el documento cambió debajo y hay
# que mirarlo, no seguir en silencio.
CUERPO = {
    "memoria.html": [
        # El censo no es un apartado: es la lista de lo que existe. Numerarlo
        # «0.1» obligaba a inventar una cuenta decimal para una sola línea.
        ("0.1 · Censo documental", "Censo documental"),
        ("censados en el apartado 0.1—", "censados en el censo documental—"),
    ],
    "marketing.html": [
        # Los anexos en romano chocaban con las partes en romano: «Anexo III» y
        # «Parte III» a dos dedos en la misma pantalla. Las letras no chocan.
        ('<p class="eyebrow">Anexo III</p>', '<p class="eyebrow">Anexo C</p>'),
        ('<p class="eyebrow">Anexo II</p>', '<p class="eyebrow">Anexo B</p>'),
        ('<p class="eyebrow">Anexo I</p>', '<p class="eyebrow">Anexo A</p>'),
        ('<a href="#anexo-legal">Anexo I</a>', '<a href="#anexo-legal">Anexo A</a>'),
    ],
}

# «Documento 1» a «Documento 01»: dos cifras como en todos los demás.
CUERPO["otros.html"] = [("Documento %d<" % n, "Documento %02d<" % n)
                        for n in range(9, 0, -1)]


def retoca(texto, archivo):
    cambios = 0
    for viejo, nuevo in CUERPO.get(archivo, []):
        if nuevo in texto and viejo not in texto:
            continue  # ya estaba hecho
        assert viejo in texto, "%s: no aparece %r" % (archivo, viejo)
        texto = texto.replace(viejo, nuevo)
        cambios += 1
    return texto, cambios


# --------------------------------------------------------------------------
#  Los tres documentos escritos a mano llevan copia de la hoja del manual
# --------------------------------------------------------------------------
# El protocolo y «otros documentos» no se generan: se escriben. Cada uno lleva
# su copia de la hoja de estilos y del guion, y por eso se quedaron con la tira
# antigua cuando el manual ya tenía el panel. Aquí se les trae la parte del
# menú desde el manual, que es la que manda, en cada construcción.
COPIAS = ["index.html", "otros.html"]


def _region(texto, desde, hasta, incluir=True):
    """El trozo entre dos marcas, con la de cierre dentro o fuera."""
    i = texto.index(desde)
    j = texto.index(hasta, i + len(desde))
    return texto[i:j + (len(hasta) if incluir else 0)]


def _sustituye(texto, reemplazo, marcas, incluir=True):
    """Cambia el primer trozo que aparezca de una lista de parejas de marcas.

    La lista va de la versión nueva a la vieja: la primera vez que corre, el
    documento aún tiene el código antiguo; a partir de la segunda tiene ya el
    del manual, y hay que poder volver a pisarlo cuando el manual cambie.
    """
    for desde, hasta in marcas:
        if desde in texto and hasta in texto[texto.index(desde):]:
            return texto.replace(_region(texto, desde, hasta, incluir), reemplazo, 1)
    return texto


# La región de estilos que se copia desde el manual va del menú al final de la
# capa de apartados: son la misma cosa —cómo se recorre un documento— y separar
# una de otra dejaba a los dos documentos escritos a mano con el menú nuevo y
# el cuerpo antiguo, que es peor que no tener ninguno de los dos.
# El sistema visual entero: los tokens y los titulares. Sin esto, el protocolo
# y «otros documentos» —que llevan copia propia de la hoja— se quedaban con la
# paleta de dos ediciones atrás mientras el resto ya era otro sistema.
RAIZ_INI = ":root{"
RAIZ_FIN = "  color-scheme:light;\n}"
TITULARES_INI = "h1,h2,h3,h4{"
TITULARES_FIN = 'h3,h4{font-variation-settings:"wdth" 100;letter-spacing:-.02em;line-height:1.18}'

# La barra superior: negra y con el acento ácido. Vive fuera de la región del
# menú, así que se copia aparte.
BARRA_INI = ("/* La barra es negra y no se disimula: es el borde del sistema, no un adorno\n"
             "   translúcido sobre el texto. */")
BARRA_FIN = ".topbar .menu__panel .menu__gt{color:var(--muted)}"
BARRA_VIEJA = (".topbar{", "}")

# Retoques sueltos de puesta al día del sistema visual.
PARCHES = [
    (".hero h1 em{font-style:italic;color:var(--accent-ink)}",
     ".hero h1 em{font-style:normal;color:var(--accent)}"),
    ("font-family:var(--f-display);font-style:italic;font-size:1.08rem;",
     "font-family:var(--f-display);font-style:normal;font-weight:500;font-size:1.08rem;"),
    ('.script{\n  border:1px solid var(--line);background:var(--surface);\n'
     '  padding:1.15rem 1.3rem;margin-top:1rem;max-width:68ch;\n}',
     '.script{\n  border:1px solid var(--line);border-radius:var(--radio-s);'
     'background:var(--surface);\n  padding:1.2rem 1.35rem 1.3rem;margin-top:1.2rem;'
     'max-width:68ch;\n}'),
]

CSS_INI = ("/* ---------------------------------------------------------------------------\n"
           "   EL MENÚ DE SECCIONES")
CSS_FIN = "@media print{.rastro{display:none}}"
CSS_MENU = (CSS_INI, CSS_FIN)
# Los finales que tuvo esta región en ediciones anteriores, para que un
# documento que se quedó atrás pueda ponerse al día de una sola pasada.
CSS_MENU_ANTES = [
    (CSS_INI, "  .lateral{display:none!important}\n}"),
    (CSS_INI, "@media print{.strip{display:none}}"),
]
CSS_MOVIL = ("  /* Cuatro pastillas de documento",
             "  .menu__g a:not(.menu__gt a){padding:.42rem .4rem .42rem .1rem}")
CSS_VELA = (".strip--nota{\n  --vel-izq:0px",
            "@media(prefers-reduced-motion:reduce){.strip--nota{scroll-behavior:auto}}")
JS_MENU = ("  /* ---- el menú de secciones ---",
           '\n  var targets = Array.prototype.slice.call(document.querySelectorAll("main section[id]')
JS_ROTULO = ("      var enlaces = [].slice.call(tira.querySelectorAll(\"a[href^='#']\"));",
             "      }")

# Lo que había antes en los documentos escritos a mano, para la primera pasada.
CSS_MENU_VIEJO = ("/* tira de fases */", ".strip a.is-off{opacity:.3}")
CSS_MOVIL_VIEJO = ("  .strip a{font-size:.68rem;padding:.38rem .5rem 0}",
                   "  .strip a{font-size:.68rem;padding:.38rem .5rem 0}")
CSS_VELA_VIEJO = (".strip,.strip--nota{",
                  "@media(prefers-reduced-motion:reduce){.strip,.strip--nota{scroll-behavior:auto}}")
JS_MENU_VIEJO = ("  /* ---- sección activa en la tira superior ---- */", JS_MENU[1])


def sincroniza():
    fuente = (RAIZ / "manual.html").read_text(encoding="utf-8")
    css_menu = _region(fuente, *CSS_MENU)
    css_movil = _region(fuente, *CSS_MOVIL)
    css_vela = _region(fuente, *CSS_VELA)
    js_menu = _region(fuente, *JS_MENU, incluir=False)
    js_rotulo = _region(fuente, *JS_ROTULO)
    raiz = _region(fuente, RAIZ_INI, RAIZ_FIN)
    barra = _region(fuente, BARRA_INI, BARRA_FIN)
    titulares = _region(fuente, TITULARES_INI, TITULARES_FIN)

    cambiados = 0
    for archivo in COPIAS:
        ruta = RAIZ / archivo
        texto = antes = ruta.read_text(encoding="utf-8")

        texto = _sustituye(texto, raiz, [(RAIZ_INI, RAIZ_FIN)])
        texto = _sustituye(texto, titulares, [(TITULARES_INI, TITULARES_FIN),
                                              (TITULARES_INI, "line-height:1.12}")])
        texto = _sustituye(texto, barra, [(BARRA_INI, BARRA_FIN), BARRA_VIEJA])
        for viejo_p, nuevo_p in PARCHES:
            texto = texto.replace(viejo_p, nuevo_p)
        texto = _sustituye(texto, css_menu,
                           [CSS_MENU] + CSS_MENU_ANTES + [CSS_MENU_VIEJO])
        texto = _sustituye(texto, css_movil, [CSS_MOVIL, CSS_MOVIL_VIEJO])
        texto = _sustituye(texto, css_vela, [CSS_VELA, CSS_VELA_VIEJO])
        texto = texto.replace(".strip a,.cabecera__docs button{scroll-margin-inline:44px}",
                              ".cabecera__docs button{scroll-margin-inline:44px}", 1)

        texto = texto.replace(
            'var tiras = [].slice.call(document.querySelectorAll(".strip,.strip--nota,.cabecera__docs"));',
            'var tiras = [].slice.call(document.querySelectorAll(".strip--nota,.cabecera__docs"));', 1)
        texto = _sustituye(texto, js_rotulo, [JS_ROTULO])
        texto = texto.replace("if(d) destinos.push({a:a, d:d, r:a.textContent.trim()});",
                              "if(d) destinos.push({a:a, d:d, r:rotulo(a)});", 1)
        texto = texto.replace(
            'var stripLinks = Array.prototype.slice.call(document.querySelectorAll("#strip a"));',
            'var stripLinks = Array.prototype.slice.call('
            'document.querySelectorAll("nav.strip .menu__g:not(.menu__g--docs) a"));', 1)
        texto = _sustituye(texto, js_menu, [JS_MENU, JS_MENU_VIEJO], incluir=False)
        texto = texto.replace("if(activo) centrarEnTira(activo);", "if(activo) situa(activo);", 1)

        if texto != antes:
            ruta.write_text(texto, encoding="utf-8")
            cambiados += 1
        print("  %-28s hoja y guion del menú al día" % archivo)
    return cambiados


def main():
    total = 0
    for archivo in menu.MENUS:
        ruta = RAIZ / archivo
        texto = ruta.read_text(encoding="utf-8")

        m = re.search(r'( *)<nav class="strip"[^>]*>.*?</nav>', texto, re.S)
        assert m, "%s: no tiene tira de secciones" % archivo
        nuevo = menu.dibuja(archivo, m.group(1))
        texto2 = texto[:m.start()] + m.group(1) + nuevo + texto[m.end():]

        texto2, cambios = retoca(texto2, archivo)
        if texto2 != texto:
            ruta.write_text(texto2, encoding="utf-8")
            total += 1
        print("  %-28s %2d destinos · %d retoques de texto"
              % (archivo, menu.cuantas(archivo), cambios))
    total += sincroniza()
    print("documentos con menú nuevo: %d" % total)
    return 0


if __name__ == "__main__":
    sys.exit(main())
