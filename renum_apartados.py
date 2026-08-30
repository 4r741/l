#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Renumerado de apartados al ensamblar.

Los fragmentos de la Tesis se escribieron con una numeración y el documento
final lleva otra: al integrarse con las partes nuevas, unos apartados se
desplazaron. El ensamblado los renumera al vuelo, y esto es lo que sabe hacerlo.

Vivía duplicado en dos generadores y con el signo § dentro del patrón, de modo
que al retirar el § dejó de encontrar nada y los apartados se habrían quedado
con su número de fragmento sin que nadie lo notara. Ahora está en un solo sitio
y entiende las dos formas en que un número de apartado aparece: como rótulo
—«05», dos cifras— y como cita dentro de una frase —«el apartado 5»—.
"""
import re

# fragmento → documento final
MAPA = {"3": "5", "4": "7", "5": "11", "6": "13", "7": "14", "8": "16",
        "9": "17", "10": "18"}

# Los sitios donde el número es rótulo. Fuera de ellos, un número suelto es un
# número y no se toca: en una tabla de cifras, «05» puede ser cualquier cosa.
ROTULOS = (
    r'<p class="eyebrow"[^>]*>(?:\s*)(\d{1,2})\b',
    r'<a href="#[^"]*">(?:\s*)(\d{1,2})\b',
    r'<h[1-4][^>]*>(?:\s*)(\d{1,2})\b',
    r'<span class="mono">(?:\s*)(\d{1,2})\b',
)


def _nuevo(n):
    return MAPA.get(str(int(n)), str(int(n)))


def renumera(texto, mapa=None):
    """Devuelve el texto con los apartados renumerados."""
    tabla = mapa if mapa is not None else MAPA

    def cambia(n):
        return tabla.get(str(int(n)), str(int(n)))

    # 1 · citas dentro de la frase
    texto = re.sub(r"\bapartados (\d{1,2}) a (\d{1,2})\b",
                   lambda m: "apartados %s a %s" % (cambia(m.group(1)), cambia(m.group(2))),
                   texto)
    texto = re.sub(r"\bapartados (\d{1,2}) y (\d{1,2})\b",
                   lambda m: "apartados %s y %s" % (cambia(m.group(1)), cambia(m.group(2))),
                   texto)
    texto = re.sub(r"\bapartado (\d{1,2})\b",
                   lambda m: "apartado " + cambia(m.group(1)), texto)

    # 2 · rótulos, que van a dos cifras
    for patron in ROTULOS:
        def rotulo(m):
            entero = m.group(0)
            viejo = m.group(1)
            return entero[: m.start(1) - m.start(0)] + "%02d" % int(cambia(viejo))
        texto = re.sub(patron, rotulo, texto)
    return texto
