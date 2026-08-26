#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Estampa la versión vigente en los documentos escritos a mano.

    python3 versiona.py          # los pone al día
    python3 versiona.py --ver    # solo dice qué cambiaría

Los cinco documentos generados toman la versión de version.py al construirse.
Los tres que se escriben a mano —el Manual, el Protocolo y Otros documentos— la
llevaban tecleada, y eso convertía subir de versión en un trabajo manual con
tantas oportunidades de olvidarse como sitios donde estuviera escrita. El pie
del Manual se quedó anunciando una versión vieja durante tres ediciones sin que
nadie lo viera: está a seis mil líneas del principio y nadie baja hasta ahí a
leer un número que da por supuesto.

Este guion los pone al día desde version.py, y el verificador comprueba después
que no ha quedado ninguno atrás.
"""
import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).parent

_v = {}
exec(compile((RAIZ / "version.py").read_text(encoding="utf-8"), "version.py", "exec"), _v)
VERSION, FECHA = _v["VERSION"], _v["FECHA"]

A_MANO = ("manual.html", "index.html", "otros.html")

# Las formas en que un documento declara su versión. Se reescribe el número, no
# la frase: cada documento dice lo suyo y eso se respeta.
FORMAS = (
    (r"\bv\d+\.\d+\b", "v" + VERSION),
    (r"\bVersión \d+\.\d+\b", "Versión " + VERSION),
    (r"\bversión v\d+\.\d+\b", "versión v" + VERSION),
    # La ficha de control pone el rótulo en una casilla y el número en la de al
    # lado, de modo que la palabra «versión» no llega a tocar la cifra. Así se
    # quedó una atrás mientras las otras cuatro apariciones del mismo documento
    # se actualizaban.
    (r"(<td>Versión</td><td>)v?\d+\.\d+", r"\1v" + VERSION),
)


def versiona(texto):
    for patron, nuevo in FORMAS:
        texto = re.sub(patron, nuevo, texto)
    return texto


def main():
    solo_ver = "--ver" in sys.argv
    tocados = 0
    for nombre in A_MANO:
        ruta = RAIZ / nombre
        antes = ruta.read_text(encoding="utf-8")
        despues = versiona(antes)
        if antes == despues:
            print("  %-14s ya está en v%s" % (nombre, VERSION))
            continue
        cuantas = sum(1 for a, b in zip(antes.split("\n"), despues.split("\n")) if a != b)
        tocados += 1
        if solo_ver:
            print("  %-14s %d línea(s) cambiarían a v%s" % (nombre, cuantas, VERSION))
        else:
            ruta.write_text(despues, encoding="utf-8")
            print("  %-14s %d línea(s) a v%s" % (nombre, cuantas, VERSION))
    if not tocados:
        print("  nada que hacer: los tres están en v%s · %s" % (VERSION, FECHA))


if __name__ == "__main__":
    main()
