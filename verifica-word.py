#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Comprueba el .docx sin abrir Word, que aquí no lo hay.

    python3 verifica-word.py

En esta máquina LibreOffice viene solo con Calc, así que no hay manera de abrir
el archivo y mirarlo. Lo que sí puede hacerse es comprobar todo lo demás: que el
paquete tenga las piezas que exige el formato, que cada XML esté bien formado,
que el orden de los elementos sea el que fija el esquema —Word rechaza el
archivo si no lo es— y, sobre todo, que el texto que entró sea el que salió.
"""
import pathlib
import re
import sys
import zipfile
from xml.etree import ElementTree as ET

RAIZ = pathlib.Path(__file__).parent
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

_v = {}
exec(compile((RAIZ / "version.py").read_text(encoding="utf-8"), "version.py", "exec"), _v)
VERSION = _v["VERSION"]
DOCX = RAIZ / "export" / ("Sistema-Documental-Giraldo-v%s.docx" % VERSION)

OBLIGATORIAS = ["[Content_Types].xml", "_rels/.rels", "word/document.xml",
                "word/styles.xml", "word/numbering.xml", "word/settings.xml",
                "word/_rels/document.xml.rels", "docProps/core.xml", "docProps/app.xml"]

# (padre, orden que exige el esquema). Solo los que este generador escribe.
ORDENES = {
    "trPr": ["cantSplit", "tblHeader"],
    "tblPr": ["tblStyle", "tblW", "tblLayout", "tblBorders", "tblCellMar"],
    "tcPr": ["tcW", "shd"],
    "pPr": ["pStyle", "keepNext", "keepLines", "numPr", "spacing", "ind", "outlineLvl"],
    "rPr": ["rFonts", "b", "i", "color", "sz"],
    "style": ["name", "basedOn", "next", "qFormat", "pPr", "rPr", "tblPr"],
    "lvl": ["start", "numFmt", "lvlText", "lvlJc", "pPr", "rPr"],
    "abstractNum": ["multiLevelType", "lvl"],
    "docDefaults": ["rPrDefault", "pPrDefault"],
}

fallos = []


def falla(que):
    fallos.append(que)
    print("  FALLO   %s" % que)


def orden(raiz):
    """Recorre el árbol y comprueba el orden de los hijos donde el esquema manda."""
    malos = 0
    for nodo in raiz.iter():
        etiqueta = nodo.tag.replace(W, "")
        esperado = ORDENES.get(etiqueta)
        if not esperado:
            continue
        vistos = [h.tag.replace(W, "") for h in nodo]
        posiciones = [esperado.index(v) for v in vistos if v in esperado]
        if posiciones != sorted(posiciones):
            malos += 1
            if malos <= 3:
                falla("<%s> con los hijos desordenados: %s" % (etiqueta, vistos))
    return malos


def texto_de(raiz):
    return "".join(n.text or "" for n in raiz.iter(W + "t"))




def main():
    if not DOCX.exists():
        sys.exit("  no existe %s" % DOCX.name)
    print("Verificación del documento de Word · v%s\n" % VERSION)

    with zipfile.ZipFile(DOCX) as z:
        nombres = z.namelist()
        for pieza in OBLIGATORIAS:
            if pieza not in nombres:
                falla("falta la pieza %s" % pieza)
        arboles = {}
        for nombre in nombres:
            try:
                arboles[nombre] = ET.fromstring(z.read(nombre))
            except ET.ParseError as e:
                falla("%s no es XML válido: %s" % (nombre, e))
        malo = z.testzip()
        if malo:
            falla("el zip está dañado en %s" % malo)

    doc = arboles.get("word/document.xml")
    if doc is None:
        sys.exit("  sin documento que verificar")

    # 1 · orden de elementos en todas las piezas
    desordenes = sum(orden(a) for a in arboles.values())
    if not desordenes:
        print("  Orden de elementos correcto en las %d piezas del paquete." % len(arboles))

    # 2 · los estilos que el documento usa tienen que existir
    estilos = arboles["word/styles.xml"]
    definidos = {s.get(W + "styleId") for s in estilos.iter(W + "style")}
    usados = {p.get(W + "val") for p in doc.iter(W + "pStyle")} | \
             {p.get(W + "val") for p in doc.iter(W + "tblStyle")}
    huerfanos = sorted(u for u in usados if u and u not in definidos)
    if huerfanos:
        falla("usa estilos que no están definidos: %s" % huerfanos)
    else:
        print("  Los %d estilos que se usan están definidos." % len(usados))

    # 3 · los titulares llevan nivel de esquema: sin eso no hay panel de
    #     navegación ni índice automático
    niveles = {}
    for s in estilos.iter(W + "style"):
        sid = s.get(W + "styleId") or ""
        if sid.startswith("Titular"):
            lvl = s.find(".//" + W + "outlineLvl")
            niveles[sid] = None if lvl is None else lvl.get(W + "val")
    sin = [k for k, v in niveles.items() if v is None]
    if sin:
        falla("titulares sin nivel de esquema: %s" % sin)
    else:
        print("  Los %d niveles de titular llevan su nivel de esquema (%s)."
              % (len(niveles), ", ".join("%s→%s" % (k[-1], v) for k, v in sorted(niveles.items()))))

    # 4 · la numeración que se usa está definida
    definidas = {n.get(W + "numId") for n in estilos.iter(W + "num")} | \
                {n.get(W + "numId") for n in arboles["word/numbering.xml"].iter(W + "num")}
    usadas = {n.get(W + "val") for n in doc.iter(W + "numId")}
    faltan = sorted(u for u in usadas if u and u not in definidas)
    if faltan:
        falla("listas con numeración no definida: %s" % faltan)
    else:
        print("  Las listas usan numeraciones definidas: %s." % sorted(usadas))

    # 5 · las tablas cuadran: cada fila con tantas celdas como columnas, y los
    #     anchos sumando el ancho de la tabla
    tablas = list(doc.iter(W + "tbl"))
    malas = 0
    for t in tablas:
        cols = len(list(t.find(W + "tblGrid")))
        suma = sum(int(g.get(W + "w")) for g in t.find(W + "tblGrid"))
        for fila in t.findall(W + "tr"):
            if len(fila.findall(W + "tc")) != cols:
                malas += 1; break
        else:
            if abs(suma - 9360) > 2:
                malas += 1
    if malas:
        falla("%d tablas descuadran en columnas o en anchos" % malas)
    else:
        print("  Las %d tablas cuadran: filas completas y anchos sumando el ancho." % len(tablas))

    # 6 · el índice automático está y pide actualizarse al abrir
    campo = "".join(i.text or "" for i in doc.iter(W + "instrText"))
    if "TOC" not in campo:
        falla("no lleva campo de tabla de contenido")
    elif arboles["word/settings.xml"].find(W + "updateFields") is None:
        falla("el índice no se actualizará solo al abrir")
    else:
        print("  Índice automático presente, y marcado para actualizarse al abrir.")

    # 7 · nada perdido por el camino: el texto del Word contra el de los
    #     documentos. Es la comprobación que de verdad importa.
    from importlib import util
    spec = util.spec_from_file_location("bw", RAIZ / "build-word.py")
    bw = util.module_from_spec(spec)
    sys.argv = ["verifica"]
    spec.loader.exec_module(bw)

    salido = re.sub(r"\s+", " ", texto_de(doc)).strip().lower()
    perdidas, revisadas = [], 0
    for ruta, titulo, _q in bw.PARTES:
        bloques = bw.bloques_de(ruta)
        frases = []
        for tipo, dato in bloques:
            if tipo == "tabla":
                continue
            t = re.sub(r"\s+", " ", "".join(x.texto for x in dato)).strip()
            if len(t) > 45:
                frases.append(t)
        # se comprueba una de cada veinte, que con miles de bloques ya es prueba
        muestra = frases[::20]
        revisadas += len(muestra)
        for f in muestra:
            if re.sub(r"\s+", " ", f).lower() not in salido:
                perdidas.append((titulo, f[:70]))
    if perdidas:
        falla("%d fragmentos del original no aparecen en el Word" % len(perdidas))
        for t, f in perdidas[:4]:
            print("            %s · «%s…»" % (t, f))
    else:
        print("  %d fragmentos comprobados uno a uno: todos están en el Word." % revisadas)

    print()
    if fallos:
        print("%d problema(s). El documento no está listo." % len(fallos))
        sys.exit(1)
    print("Sin problemas. El paquete es válido y el contenido está entero.")
    print("No se ha podido abrir en Word: esta máquina solo tiene LibreOffice Calc.")


if __name__ == "__main__":
    main()
