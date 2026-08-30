#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cambia el nombre del documento de gobierno: «Tesis» pasa a «Plan de Dirección».

    python3 renombra.py --ver     # dice qué cambiaría
    python3 renombra.py           # lo cambia

El cuidado está en el género. «La Tesis» es femenino y «el Plan» es masculino,
de modo que un reemplazo directo dejaría «de la Plan de Dirección» por todas
partes. Aquí se cambian primero las formas con artículo y preposición, y solo
después el nombre suelto.
"""
import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).parent
ARCHIVOS = (sorted(RAIZ.glob("fuentes/*.html"))
            + sorted(RAIZ.glob("generadores/*.py"))
            + [RAIZ / n for n in ("manual.html", "index.html", "otros.html",
                                  "build-inicio.py", "build-captura.py",
                                  "build-libro.py", "build-export.py", "build-pdf.py",
                                  "build-pdf-completo.py", "build-word.py",
                                  "build.py", "catalogo-acciones.py",
                                  "modelo-campanas.py", "indice.py",
                                  "check-coherencia.py")])

# El orden manda: lo más largo y lo que lleva artículo, primero.
CAMBIOS = [
    # el nombre completo
    ("Tesis de Dirección", "Plan de Dirección"),
    ("tesis de dirección", "plan de dirección"),
    # con artículo y preposición, donde cambia el género
    ("de la Tesis", "del Plan de Dirección"),
    ("De la Tesis", "Del Plan de Dirección"),
    ("a la Tesis", "al Plan de Dirección"),
    ("la Tesis", "el Plan de Dirección"),
    ("La Tesis", "El Plan de Dirección"),
    ("esta Tesis", "este Plan de Dirección"),
    ("Esta Tesis", "Este Plan de Dirección"),
    ("una Tesis", "un Plan de Dirección"),
    # el apartado que se llamaba así, que es la palabra que sobra. Va antes que
    # el nombre suelto: si no, «2 · Tesis» —la entrada corta de ese apartado en
    # la barra— se convertiría en el nombre del documento entero.
    ("Tesis del proyecto", "La apuesta del proyecto"),
    ("· Tesis</a>", "· La apuesta</a>"),
    ("·Tesis</a>", "·La apuesta</a>"),
    (">Tesis</a>", ">La apuesta</a>"),
    ("· Tesis<", "· La apuesta<"),
    ("Tesis de escalado", "La apuesta de escalado"),
    # el nombre suelto, ya sin artículo delante
    ("Tesis", "Plan de Dirección"),
]

# Y la palabra en minúscula, cuando nombra al documento y no una idea.
MENUDOS = [
    ("la tesis de este documento", "la apuesta de este documento"),
    ("La tesis de este documento", "La apuesta de este documento"),
    ("la tesis del proyecto", "la apuesta del proyecto"),
    ("La tesis del proyecto", "La apuesta del proyecto"),
    ("la tesis del apartado", "la apuesta del apartado"),
    ("La tesis del apartado", "La apuesta del apartado"),
    ("nuestra tesis", "nuestra apuesta"),
    ("La tesis", "La apuesta"),
    ("la tesis", "la apuesta"),
]


def convierte(texto):
    for viejo, nuevo in CAMBIOS + MENUDOS:
        texto = texto.replace(viejo, nuevo)
    # el generador se llama tesis.py y el identificador es doc-tesis: son
    # nombres de fichero y de ancla, no texto que nadie lee
    texto = texto.replace("Plan de Dirección.py", "tesis.py")
    texto = texto.replace("doc-Plan de Dirección", "doc-tesis")
    return texto


def main():
    solo_ver = "--ver" in sys.argv
    total = 0
    for ruta in ARCHIVOS:
        if not ruta.exists():
            continue
        antes = ruta.read_text(encoding="utf-8")
        if "Tesis" not in antes and "tesis" not in antes:
            continue
        despues = convierte(antes)
        if antes == despues:
            continue
        n = len(re.findall(r"[Tt]esis", antes)) - len(re.findall(r"[Tt]esis", despues))
        total += n
        print("  %-42s %3d" % (ruta.relative_to(RAIZ), n))
        if solo_ver:
            for a, b in zip(antes.split("\n"), despues.split("\n")):
                if a != b:
                    print("      − %s" % a.strip()[:96])
                    print("      + %s" % b.strip()[:96])
                    break
        else:
            ruta.write_text(despues, encoding="utf-8")
    print("\n  %d apariciones cambiadas" % total)


if __name__ == "__main__":
    main()
