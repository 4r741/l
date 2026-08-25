#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Le pone ancla a todo titular que no la tenga.

    python3 anclas.py            # recorre los documentos y añade las que faltan

Un índice detallado exige que cada línea lleve a algún sitio, y de los más de
cuatrocientos titulares del sistema solo nueve tenían identificador: el resto no
se podía enlazar. Este guion se los pone, derivados del propio texto, de modo
que la misma frase produzca siempre la misma ancla y los enlaces guardados
sigan valiendo entre ediciones.

Solo añade. Un titular que ya tiene ancla se queda como está, porque hay
enlaces publicados que apuntan a ella.
"""
import pathlib
import re
import sys
import unicodedata

RAIZ = pathlib.Path(__file__).parent

# archivo → prefijo del ancla, para que no colisionen entre documentos
DOCUMENTOS = {
    "memoria.html": "t",
    "marketing.html": "k",
    "manual.html": "m",
    "index.html": "p",
    "otros.html": "o",
    "instrumentos/captura.html": "c",
}

CORTAS = {"y", "de", "del", "la", "el", "los", "las", "un", "una", "en", "que",
          "a", "al", "lo", "se", "su", "sus", "por", "con", "para", "es"}


def sosa(texto):
    """Un ancla legible a partir del titular: sin tildes, sin ruido, corta."""
    limpio = re.sub(r"<[^>]+>", " ", texto)
    limpio = re.sub(r"&[a-z]+;|&#\d+;", " ", limpio)
    limpio = unicodedata.normalize("NFD", limpio)
    limpio = "".join(c for c in limpio if unicodedata.category(c) != "Mn")
    limpio = re.sub(r"[^A-Za-z0-9]+", " ", limpio).lower().strip()
    palabras = [p for p in limpio.split() if p not in CORTAS] or limpio.split()
    return "-".join(palabras[:6])[:52].strip("-")


def anclar(html, prefijo):
    """Devuelve (html, cuántas anclas nuevas). No toca las que ya existen."""
    usadas = set(re.findall(r'\sid="([^"]+)"', html))
    nuevas = 0

    def pon(m):
        nonlocal nuevas
        entero, atributos, texto = m.group(0), m.group(2), m.group(3)
        if "id=" in atributos:
            return entero
        base = sosa(texto)
        if not base:
            return entero
        ancla = "%s-%s" % (prefijo, base)
        n = 2
        while ancla in usadas:
            ancla = "%s-%s-%d" % (prefijo, base, n)
            n += 1
        usadas.add(ancla)
        nuevas += 1
        return "<h%s%s id=\"%s\">%s</h%s>" % (m.group(1), atributos, ancla, texto, m.group(1))

    html = re.sub(r"<h([23])((?:\s[^>]*)?)>(.*?)</h\1>", pon, html, flags=re.S)
    return html, nuevas


def main():
    total = 0
    for archivo, prefijo in DOCUMENTOS.items():
        ruta = RAIZ / archivo
        html = ruta.read_text(encoding="utf-8")
        # la cabecera y el pie no llevan titulares que indexar
        i = html.index("<main") if "<main" in html else 0
        cuerpo, nuevas = anclar(html[i:], prefijo)
        if nuevas:
            ruta.write_text(html[:i] + cuerpo, encoding="utf-8")
        total += nuevas
        print("  %-28s %3d anclas nuevas" % (archivo, nuevas))
    print("anclas añadidas: %d" % total)
    return 0


if __name__ == "__main__":
    sys.exit(main())
