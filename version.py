#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""La versión del sistema documental. Un solo sitio.

    python3 version.py          # la versión vigente

Todas las piezas comparten número y fecha: si una cambia lo bastante como para
merecer versión nueva, la reciben todas. El número vive aquí y solo aquí: lo
leen los generadores, el verificador, el libro de cálculo y los nombres de los
archivos que se publican. Subir de versión es cambiar esta línea.
"""
VERSION = "10.0"
FECHA = "Septiembre 2026"

# Solo el número mayor, para los nombres de archivo: Giraldo-TODO-EN-UNO-v8.html
CORTA = VERSION.split(".")[0]

if __name__ == "__main__":
    print("v%s · %s" % (VERSION, FECHA))
