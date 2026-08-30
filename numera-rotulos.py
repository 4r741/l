#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Envuelve el número de apartado para que pueda dibujarse en grande.

    python3 numera-rotulos.py

El rótulo de un apartado es «03 · Mapa competitivo». Para poder dibujar el
número aparte del nombre hace falta poder señalarlo, y en el HTML no se puede
señalar un trozo de texto suelto. Esto le pone su etiqueta:

    <p class="eyebrow"><b class="num">03</b> Mapa competitivo</p>

Se ejecuta dentro de la construcción, después de generar cada documento, de modo
que las fuentes se sigan escribiendo con el rótulo tal cual.
"""
import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).parent
DOCUMENTOS = ["memoria.html", "marketing.html", "manual.html", "index.html",
              "otros.html", "instrumentos/captura.html"]


def main():
    total = 0
    for nombre in DOCUMENTOS:
        ruta = RAIZ / nombre
        if not ruta.exists():
            continue
        t = ruta.read_text(encoding="utf-8")
        # solo el rótulo que empieza por número, y solo si no lleva ya su marca
        patron = re.compile(
            r'(<p class="eyebrow"[^>]*>)\s*(\d{1,2}(?:\.\d+)?)\s*(?:·\s*)?(?!</p>)')

        def cambia(m):
            return '%s<b class="num">%s</b> ' % (m.group(1), m.group(2))

        nuevo, n = patron.subn(cambia, t)
        if n:
            ruta.write_text(nuevo, encoding="utf-8")
        total += n
        print("  %-28s %3d rótulos" % (nombre, n))
    print("  → %d números marcados" % total)
    if not total:
        sys.exit("  no se ha marcado ninguno")


if __name__ == "__main__":
    main()
