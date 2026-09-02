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
    ("memoria.html", "Plan de Dirección", "Gobierno",
     "Qué creemos, qué apostamos y las quince decisiones que se someten a la Junta",
     "Junta Directiva"),
    ("deck.html", "Presentación de Junta", "Derivado",
     "El Plan de Dirección para proyectar, con guion del ponente y ruta corta",
     "Quien presenta"),
    ("marketing.html", "Plan Maestro de Marketing", "Plan",
     "Las 76 acciones sobre los 12 estados del paciente, y el programa Giraldo Te Cuida",
     "Dirección y Gerencia"),
    ("protocolos.html", "Protocolos por puesto", "Vista operativa",
     "El protocolo del centro visto desde cada uno de los seis puestos",
     "Todo el equipo"),
    ("manual.html", "Manual Maestro de Operaciones", "Troncal",
     "Las 14 fases del recorrido, los 6 puestos, RACI, indicadores e incentivos",
     "Todo el equipo"),
    ("index.html", "Protocolo de Primera Visita", "Troncal",
     "Las 12 fases de la primera visita, minuto a minuto",
     "Recepción, Doctor, RAC"),
    ("otros.html", "Otros documentos del sistema", "Troncal",
     "Los 14 documentos de apoyo, del compendio maestro a la continuidad legal",
     "Según el documento"),
    ("instrumentos/captura.html", "Los números del centro", "Instrumento",
     "Los 10 indicadores y los 5 números, mes a mes",
     "Gerencia"),
]


def entradas(archivo):
    """El índice de dos niveles de un documento.

    El primer nivel son los apartados que el propio documento declara en su
    tira de secciones —el orden es el suyo, no uno inventado— y el segundo, los
    titulares que viven dentro de cada uno. El segundo nivel existe porque un
    índice que solo llega al apartado obliga a rebuscar dentro: quien busca «la
    matriz RACI de la fase 7» quiere esa línea, no el capítulo que la contiene.
    """
    t = (RAIZ / archivo).read_text(encoding="utf-8")
    tira = re.search(r'<nav class="strip"[^>]*>(.*?)</nav>', t, re.S)
    if not tira:
        return []
    cuerpo = t[t.index("<main"):] if "<main" in t else t

    def limpio(s):
        # Las etiquetas se sustituyen por un espacio para que «uno<br>otro» no
        # salga pegado; el precio es que «<em>x</em>: y» sale con un espacio
        # delante de los dos puntos. Se recoge aquí, junto a la puntuación que
        # abre y la que cierra, para que el índice se lea como se escribe.
        s = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()
        s = re.sub(r"\s+([:;,.!?%»)\]])", r"\1", s)
        s = re.sub(r"([«(\[¿¡])\s+", r"\1", s)
        return s

    # dónde empieza cada apartado dentro del cuerpo
    nivel1 = []
    for ancla, rotulo in re.findall(r'<a href="#([^"]+)">(.*?)</a>', tira.group(1), re.S):
        m = re.search(r'\sid="%s"' % re.escape(ancla), cuerpo)
        nivel1.append({"ancla": ancla, "rotulo": limpio(rotulo),
                       "desde": m.start() if m else -1, "hijos": []})

    # todos los titulares con ancla, en orden de aparición
    titulares = [(m.start(), m.group(1), limpio(m.group(2)))
                 for m in re.finditer(r'<h[23][^>]*\sid="([^"]+)"[^>]*>(.*?)</h[23]>',
                                      cuerpo, re.S)]

    ordenados = sorted([e for e in nivel1 if e["desde"] >= 0], key=lambda e: e["desde"])
    for n, apartado in enumerate(ordenados):
        hasta = ordenados[n + 1]["desde"] if n + 1 < len(ordenados) else len(cuerpo)
        for pos, ancla, rotulo in titulares:
            if not (apartado["desde"] < pos < hasta):
                continue
            # el titular del propio apartado no se repite como hijo suyo
            if ancla == apartado["ancla"] or not rotulo or len(rotulo) > 96:
                continue
            apartado["hijos"].append({"ancla": ancla, "rotulo": rotulo})
    return nivel1


def calcula():
    fuera = []
    for archivo, rotulo, clase, que, quien in DOCUMENTOS:
        fuera.append({"archivo": archivo, "rotulo": rotulo, "clase": clase,
                      "que": que, "quien": quien, "entradas": entradas(archivo)})
    return fuera


def main():
    d = calcula()
    total = sum(len(x["entradas"]) for x in d)
    hijos = sum(len(e["hijos"]) for x in d for e in x["entradas"])
    print("ÍNDICE GENERAL · %d documentos · %d apartados · %d subapartados\n"
          % (len(d), total, hijos))
    for x in d:
        print("%s  ·  %s  ·  %d apartados" % (x["rotulo"], x["clase"], len(x["entradas"])))
        for e in x["entradas"]:
            print("   %s" % e["rotulo"])
            for h in e["hijos"]:
                print("        %s" % h["rotulo"])
        print()


if __name__ == "__main__":
    main()
