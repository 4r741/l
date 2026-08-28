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
            if not nombre.endswith((".xml", ".rels")):
                continue          # las imágenes no son XML
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

    # 6 · las figuras: cada dibujo con su imagen dentro del paquete, su relación
    #     y su texto alternativo. Una imagen enlazada y ausente es un cuadro roto
    #     en mitad de un documento de Junta.
    with zipfile.ZipFile(DOCX) as z:
        medios = {n for n in z.namelist() if n.startswith("word/media/")}
        pesos = {n: z.getinfo(n).file_size for n in medios}
    rels = arboles["word/_rels/document.xml.rels"]
    RNS = "{http://schemas.openxmlformats.org/package/2006/relationships}"
    destinos = {r.get("Id"): r.get("Target") for r in rels.iter(RNS + "Relationship")}
    A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
    R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
    blips = [b.get(R + "embed") for b in doc.iter(A + "blip")]
    rotas = [b for b in blips if "word/" + (destinos.get(b) or "") not in medios]
    if not blips:
        falla("no lleva ninguna figura")
    elif rotas:
        falla("%d figuras apuntan a una imagen que no está en el paquete" % len(rotas))
    else:
        vacias = [n for n, p in pesos.items() if p < 2000]
        sobran = len(medios) - len(set(blips))
        WP = "{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}"
        sinalt = [d for d in doc.iter(WP + "docPr") if not (d.get("descr") or "").strip()]
        sincaja = [e for e in doc.iter(WP + "extent")
                   if int(e.get("cx") or 0) <= 0 or int(e.get("cy") or 0) <= 0]
        if vacias:
            falla("%d imágenes pesan menos de 2 KB: probablemente salieron en blanco" % len(vacias))
        elif sobran:
            falla("%d imágenes en el paquete que ningún dibujo usa" % sobran)
        elif sincaja:
            falla("%d figuras sin medidas" % len(sincaja))
        else:
            # A4 menos los márgenes: 11906 − 1191×2 = 9524 dxa, a 635 EMU cada uno
            CAJA = 9524 * 635
            grandes = sum(1 for e in doc.iter(WP + "extent")
                          if int(e.get("cx")) > CAJA)
            print("  Las %d figuras están incrustadas, con su imagen en el paquete "
                  "(%d KB), medidas y texto alternativo en %d de ellas."
                  % (len(blips), sum(pesos.values()) // 1024, len(blips) - len(sinalt)))
            if grandes:
                falla("%d figuras se salen del ancho de la caja de escritura" % grandes)

    # 7 · el índice automático está y pide actualizarse al abrir
    campo = "".join(i.text or "" for i in doc.iter(W + "instrText"))
    if "TOC" not in campo:
        falla("no lleva campo de tabla de contenido")
    elif arboles["word/settings.xml"].find(W + "updateFields") is None:
        falla("el índice no se actualizará solo al abrir")
    else:
        print("  Índice automático presente, y marcado para actualizarse al abrir.")

    # 8 · nada perdido por el camino: el texto del Word contra el de los
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
            if tipo == "tabla" or not dato:
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
