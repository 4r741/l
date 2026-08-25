#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""El índice general del sistema: todo lo que hay, apartado por apartado.

    python3 indice.py            # el índice en pantalla

Lo extrae de los propios documentos —de la tira de secciones que cada uno lleva
en su cabecera—, así que no puede quedarse atrás: si un documento gana un
apartado, el índice lo tiene en la siguiente construcción. Un índice tecleado a
mano es un índice que a la tercera edición miente.
"""
import html
import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).parent

# archivo, rótulo, qué es, para quién
DOCUMENTOS = [
    ("memoria.html", "Tesis de Dirección", "Gobierno",
     "Qué creemos, qué apostamos y las quince decisiones que se someten a la Junta",
     "Junta Directiva"),
    ("deck.html", "Presentación de Junta", "Derivado",
     "La Tesis para proyectar, con guion del ponente y ruta corta",
     "Quien presenta"),
    ("marketing.html", "Plan Maestro de Marketing", "Plan",
     "Las 76 acciones posibles sobre los 12 estados del paciente",
     "Dirección y Gerencia"),
    ("manual.html", "Manual Maestro de Operaciones", "Troncal",
     "Las 14 fases del recorrido, los 6 puestos, RACI, indicadores e incentivos",
     "Todo el equipo"),
    ("index.html", "Protocolo de Primera Visita", "Troncal",
     "Las 12 fases de la primera visita, minuto a minuto",
     "Recepción, Doctor, RAC"),
    ("otros.html", "Otros documentos del sistema", "Troncal",
     "Los 14 documentos de apoyo, del compendio maestro al programa de cuidado",
     "Según el documento"),
    ("instrumentos/captura.html", "Captura de la línea base", "Instrumento",
     "Los 10 indicadores y los 5 números, mes a mes",
     "Gerencia"),
]


def entradas(archivo):
    """Los apartados de un documento, tal y como él mismo los declara."""
    t = (RAIZ / archivo).read_text(encoding="utf-8")
    tira = re.search(r'<nav class="strip"[^>]*>(.*?)</nav>', t, re.S)
    if not tira:
        return []
    return [{"ancla": a, "rotulo": re.sub(r"\s+", " ", html.unescape(r)).strip()}
            for a, r in re.findall(r'<a href="#([^"]+)">(.*?)</a>', tira.group(1), re.S)]


def calcula():
    fuera = []
    for archivo, rotulo, clase, que, quien in DOCUMENTOS:
        fuera.append({"archivo": archivo, "rotulo": rotulo, "clase": clase,
                      "que": que, "quien": quien, "entradas": entradas(archivo)})
    return fuera


def main():
    d = calcula()
    total = sum(len(x["entradas"]) for x in d)
    print("ÍNDICE GENERAL · %d documentos · %d apartados\n" % (len(d), total))
    for x in d:
        print("%s  ·  %s  ·  %d apartados" % (x["rotulo"], x["clase"], len(x["entradas"])))
        for e in x["entradas"]:
            print("     %s" % e["rotulo"])
        print()


if __name__ == "__main__":
    main()
