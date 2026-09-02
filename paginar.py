#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parte cada documento en apartados navegables. No toca ni una palabra.

    python3 paginar.py

Un documento del sistema es una sola columna de texto de doscientos a
cuatrocientos cincuenta kilobytes. El menú lleva a un ancla, sí, pero uno cae
en mitad de un río y a partir de ahí no sabe dónde está, cuánto queda del
apartado que está leyendo ni cómo pasar al siguiente: solo puede arrastrar.
Cuarenta mil píxeles de arrastre.

Este guion envuelve cada tramo del cuerpo en su propio apartado, usando como
tijera las mismas anclas que declara menu.py. La literatura no se toca: se
mueve una etiqueta de apertura y otra de cierre alrededor de lo que ya había.
Con eso, la hoja de estilos puede enseñar un apartado cada vez y el guion puede
dar anterior y siguiente. Sin guiones —y al imprimir— se ven todos seguidos,
que es exactamente lo que había antes.

Es idempotente: si el documento ya está partido, lo vuelve a partir igual.
"""
import pathlib
import re
import sys
import types
from html.parser import HTMLParser

RAIZ = pathlib.Path(__file__).parent

menu = types.ModuleType("menu")
menu.__file__ = str(RAIZ / "menu.py")
exec(compile((RAIZ / "menu.py").read_text(encoding="utf-8"), menu.__file__, "exec"),
     menu.__dict__)

# El identificador de la portada de cada documento, el tramo anterior al
# primer apartado. Es el mismo en los siete para que el guion no tenga que
# saberse una lista.
PORTADA = "portada-doc"

# Dos no se parten. La portada del sistema es una página corta que se lee de un
# scroll —quién es esto, qué documento abro, dónde busco— y trocearla en cuatro
# pantallas sería inventar un recorrido donde no hay ninguno. Y la hoja de los
# números es un instrumento que se rellena, no un texto que se recorre.
ENTERAS = {"inicio.html", "instrumentos/captura.html", "protocolos.html"}

VACIOS = {"br", "img", "meta", "link", "input", "hr", "source", "col", "area",
          "base", "path", "circle", "rect", "line", "use", "stop", "polygon",
          "polyline", "ellipse", "text", "tspan", "g", "defs", "clippath"}


class Hijos(HTMLParser):
    """Dónde empieza cada hijo directo de <main>, y qué identificador lleva."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.d = 0
        self.dentro = False
        self.abre = []          # (offset, id o None)
        self.main = None        # (inicio del contenido, fin del contenido)
        self._lineas = None

    def posicion(self):
        linea, col = self.getpos()
        return self._lineas[linea - 1] + col

    def handle_starttag(self, tag, attrs):
        if tag == "main":
            self.dentro = True
            self.d = 0
            return
        if not self.dentro:
            return
        if self.d == 0:
            self.abre.append((self.posicion(), dict(attrs).get("id")))
        if tag not in VACIOS:
            self.d += 1

    def handle_startendtag(self, tag, attrs):
        if self.dentro and self.d == 0:
            self.abre.append((self.posicion(), dict(attrs).get("id")))

    def handle_endtag(self, tag):
        if tag == "main":
            self.dentro = False
            return
        if self.dentro and tag not in VACIOS:
            self.d -= 1


def hijos_de_main(html):
    p = Hijos()
    p._lineas = [0]
    for linea in html.splitlines(keepends=True):
        p._lineas.append(p._lineas[-1] + len(linea))
    p.feed(html)
    return p.abre


def anclas_de(archivo):
    """Las anclas que el menú declara como apartado, en orden de documento."""
    fuera = []
    for _, ancla_grupo, entradas in menu.MENUS[archivo]["grupos"]:
        if ancla_grupo:
            fuera.append(ancla_grupo)
        fuera += [a for a, _, _ in entradas]
    return fuera


def rotulos_de(archivo):
    """ancla → (número, rótulo, grupo), para el pie de anterior y siguiente."""
    fuera = {}
    for grupo, ancla_grupo, entradas in menu.MENUS[archivo]["grupos"]:
        if ancla_grupo:
            fuera[ancla_grupo] = ("", grupo, grupo)
        for ancla, numero, rotulo in entradas:
            fuera[ancla] = (numero, rotulo, grupo)
    return fuera


def despagina(html):
    """Deja el cuerpo como estaba, para poder volver a partirlo."""
    html = re.sub(r'\n?<article class="ap"[^>]*>\n', "\n", html)
    html = re.sub(r'\n</article><!--/ap-->\n', "\n", html)
    return html


def parte(html, archivo):
    html = despagina(html)
    i = html.index("<main")
    fin = html.rindex("</main>")

    cortes = {}
    for off, ident in hijos_de_main(html):
        if ident:
            cortes.setdefault(ident, off)

    orden = [(cortes[a], a) for a in anclas_de(archivo) if a in cortes]
    orden.sort()
    if not orden:
        return html, 0

    rot = rotulos_de(archivo)

    # Lo que va antes del primer apartado es la portada del documento: el
    # titular, el lema y la ficha de cabecera. Si se queda fuera, se ve pegada
    # encima de cualquier apartado que se abra. Es un apartado más, el primero.
    preambulo = html[html.index(">", i) + 1:orden[0][0]]
    hay_portada = bool(re.sub(r"<[^>]+>", "", preambulo).strip())

    piezas = [html[:html.index(">", i) + 1]]
    if hay_portada:
        piezas.append(
            '\n<article class="ap" data-ap="%s" data-n="" data-rotulo="Portada" data-grupo="">\n'
            % PORTADA)
        piezas.append(preambulo.strip("\n"))
        piezas.append("\n</article><!--/ap-->\n")
    else:
        piezas.append(preambulo)
    for k, (desde, ancla) in enumerate(orden):
        hasta = orden[k + 1][0] if k + 1 < len(orden) else fin
        numero, rotulo, grupo = rot.get(ancla, ("", ancla, ""))
        piezas.append(
            '\n<article class="ap" data-ap="%s" data-n="%s" data-rotulo="%s" data-grupo="%s">\n'
            % (ancla, numero, rotulo.replace('"', "&quot;"), grupo.replace('"', "&quot;")))
        piezas.append(html[desde:hasta].strip("\n"))
        piezas.append("\n</article><!--/ap-->\n")
    piezas.append(html[fin:])
    return "".join(piezas), len(orden)


def main():
    total = 0
    for archivo in menu.MENUS:
        ruta = RAIZ / archivo
        html = ruta.read_text(encoding="utf-8")
        if archivo in ENTERAS:
            nuevo, n = despagina(html), 0
        else:
            nuevo, n = parte(html, archivo)
        if nuevo != html:
            ruta.write_text(nuevo, encoding="utf-8")
        print("  %-28s %s" % (archivo, "%2d apartados" % n if n else " entera"))
        total += n
    print("apartados navegables: %d" % total)
    return 0


if __name__ == "__main__":
    sys.exit(main())
