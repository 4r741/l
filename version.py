#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""La versión del sistema documental. Un solo sitio.

    python3 version.py          # la versión vigente

Todas las piezas comparten número y fecha: si una cambia lo bastante como para
merecer versión nueva, la reciben todas. Esa regla estaba escrita desde la v6.0
y aun así el número vivía tecleado en catorce archivos, de modo que subir de
versión era una tarea manual con catorce oportunidades de olvidarse de una.

Ahora lo leen de aquí los generadores, el verificador y los nombres de los
archivos que se publican. Subir de versión es cambiar esta línea.
"""
VERSION = "7.0"
FECHA = "Agosto 2026"

# Solo el número mayor, para los nombres de archivo: Giraldo-TODO-EN-UNO-v7.html
CORTA = VERSION.split(".")[0]

if __name__ == "__main__":
    print("v%s · %s" % (VERSION, FECHA))
