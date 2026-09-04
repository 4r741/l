#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Arma la carpeta de entrega: los cuatro archivos que se mandan, y nada más.

    python3 build-entrega.py

La entrega se venía copiando a mano, y una copia a mano se olvida: en la versión
8 se entregó un centro.html que pedía las tipografías a Google al abrirse, de
modo que el archivo que se anunciaba como «doble clic y funciona sin conexión»
se veía con otra letra en una sala sin red. Aquí la entrega se construye, se
comprueba y se firma sola.

Lo que comprueba antes de dar nada por bueno:

  · que ningún archivo entregado apunte a la máquina que lo compiló;
  · que ninguno pida nada a la red para verse como debe;
  · que los cuatro lleven la misma versión;
  · que ninguno mencione lo que no puede mencionarse.
"""
import pathlib
import re
import shutil
import sys

RAIZ = pathlib.Path(__file__).parent

_v = {}
exec(compile((RAIZ / "version.py").read_text(encoding="utf-8"), "version.py", "exec"), _v)
VERSION, FECHA, CORTA = _v["VERSION"], _v["FECHA"], _v["CORTA"]

DESTINO = RAIZ / "entrega"
EXPORT = RAIZ / "export"

# origen → nombre con el que viaja
PIEZAS = [
    (RAIZ / "centro.html", "centro.html"),
    (EXPORT / ("Giraldo-TODO-EN-UNO-v%s.html" % CORTA), "Giraldo-TODO-EN-UNO-v%s.html" % CORTA),
    (EXPORT / ("Sistema-Documental-Giraldo-v%s.pdf" % VERSION),
     "Sistema-Documental-Giraldo-v%s.pdf" % VERSION),
    (EXPORT / ("Sistema-Documental-Giraldo-v%s.docx" % VERSION),
     "Sistema-Documental-Giraldo-v%s.docx" % VERSION),
]

# Nombres que no pueden aparecer en nada de lo que sale del centro.
PROHIBIDOS = ["Höllenback", "Hollenback", "Hermes"]

# Rastros de la máquina que compiló, que en la de cualquier otro lector no
# llevan a ninguna parte.
RASTROS = [
    (re.compile(r"file:///(?:home|Users|root)/"), "rutas del disco de compilación"),
    (re.compile(r"https?://fonts\.(?:googleapis|gstatic)\.com"), "tipografías pedidas a la red"),
    (re.compile(r"http://localhost|127\.0\.0\.1"), "un servidor local"),
]

ENLACE_FUENTES = re.compile(
    r'<link rel="preconnect"[^>]*>\s*<link rel="preconnect"[^>]*>\s*'
    r'<link rel="stylesheet" href="https://fonts\.googleapis\.com[^"]*">', re.S)


def sin_conexion(html):
    """Cambia el enlace a Google Fonts por las tipografías ya incrustadas."""
    cache = EXPORT / "_fuentes.html"
    if not cache.exists():
        sys.exit("  faltan las tipografías incrustadas: ejecute antes python3 build-export.py")
    estilo = cache.read_text(encoding="utf-8")
    nuevo, cuantos = ENLACE_FUENTES.subn(lambda _: estilo, html, count=1)
    if not cuantos:
        return html          # ya venía incrustado
    return nuevo


def texto_de(ruta):
    """Lo legible de un archivo, sea HTML, PDF o Word."""
    if ruta.suffix in (".html", ".md", ".txt"):
        return ruta.read_text(encoding="utf-8", errors="replace")
    if ruta.suffix == ".docx":
        import zipfile
        with zipfile.ZipFile(ruta) as z:
            return " ".join(re.findall(r">([^<]+)<", z.read("word/document.xml").decode("utf-8")))
    if ruta.suffix == ".pdf":
        from pypdf import PdfReader
        lector = PdfReader(str(ruta))
        partes = []
        for p in lector.pages:
            for a in (p.get("/Annots") or []):
                o = a.get_object()
                accion = o.get("/A")
                accion = accion.get_object() if accion is not None else None
                if accion is not None and accion.get("/URI"):
                    partes.append(str(accion["/URI"]))
        return " ".join(partes)
    return ""


def main():
    faltan = [o.name for o, _ in PIEZAS if not o.exists()]
    if faltan:
        sys.exit("  faltan piezas de la entrega: %s\n"
                 "  ejecute antes python3 build.py --todo" % ", ".join(faltan))

    DESTINO.mkdir(exist_ok=True)
    # lo que sobra de versiones anteriores no se queda: una carpeta de entrega
    # con dos versiones dentro es una carpeta en la que alguien abre la vieja
    guardar = {n for _o, n in PIEZAS} | {"LEEME.md"}
    for viejo in DESTINO.iterdir():
        if viejo.is_file() and viejo.name not in guardar:
            viejo.unlink()
            print("  · retirado de la entrega: %s" % viejo.name)

    escritos = []
    for origen, nombre in PIEZAS:
        salida = DESTINO / nombre
        if origen.suffix == ".html":
            salida.write_text(sin_conexion(origen.read_text(encoding="utf-8")), encoding="utf-8")
        else:
            shutil.copy2(origen, salida)
        escritos.append(salida)
        print("  · %-44s %6d KB" % (nombre, salida.stat().st_size // 1024))

    # ------------------------------------------------------------ la revisión
    problemas = []
    for ruta in escritos:
        contenido = texto_de(ruta)
        for patron, que in RASTROS:
            cuantos = len(patron.findall(contenido))
            if cuantos:
                problemas.append("%s · %d rastros de %s" % (ruta.name, cuantos, que))
        for nombre in PROHIBIDOS:
            if nombre.lower() in contenido.lower():
                problemas.append("%s · nombra «%s»" % (ruta.name, nombre))
        if ruta.suffix == ".html" and ("v%s" % CORTA) not in ruta.name and VERSION not in contenido:
            problemas.append("%s · no dice qué versión es" % ruta.name)

    if problemas:
        print("\n  La entrega no sale:")
        for p in problemas:
            print("    ✗ %s" % p)
        sys.exit(1)

    print("  · %d archivos · %.1f MB · sin rastros de la máquina, sin red, v%s"
          % (len(escritos), sum(r.stat().st_size for r in escritos) / 1e6, VERSION))


if __name__ == "__main__":
    main()
