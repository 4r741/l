#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Comprueba los enlaces del cuaderno en PDF y del documento de Word.

    python3 verifica-libro.py

Las dos piezas impresas del sistema también tienen enlaces, y hasta ahora nadie
los miraba. El PDF encuadernado arrastraba doscientos sesenta y cuatro que
apuntaban al disco de la máquina donde se compiló —«file:///home/…/manual.html»,
que en el ordenador de cualquier otro lector no abre nada— y el Word no tenía
ninguno: «véase la Fase 14» era texto muerto en un documento de seiscientas
páginas.

Lo que se comprueba:

  PDF   · que no quede ni un enlace al disco de nadie;
        · que todo salto interno caiga en una página que existe;
        · que haya marcadores hasta el apartado, y no solo hasta el documento.
  Word  · que el XML esté bien formado;
        · que todo hipervínculo tenga su marcador;
        · que los nombres de marcador sean de los que Word admite.
"""
import pathlib
import re
import sys
import xml.dom.minidom as xml_dom
import zipfile

from pypdf import PdfReader

RAIZ = pathlib.Path(__file__).parent

_v = {}
exec(compile((RAIZ / "version.py").read_text(encoding="utf-8"), "version.py", "exec"), _v)
VERSION = _v["VERSION"]

PDF = RAIZ / "export" / ("Sistema-Documental-Giraldo-v%s.pdf" % VERSION)
WORD = RAIZ / "export" / ("Sistema-Documental-Giraldo-v%s.docx" % VERSION)

# Un marcador por documento y nada más obliga a hojear seiscientas páginas.
MINIMO_MARCADORES = 60

fallos = []


def falla(mensaje):
    fallos.append(mensaje)
    print("  ✗ %s" % mensaje)


def revisa_pdf():
    if not PDF.exists():
        return falla("no está %s" % PDF.name)
    lector = PdfReader(str(PDF))
    paginas = {}
    for i, p in enumerate(lector.pages):
        ref = p.indirect_reference
        if ref is not None:
            paginas[(ref.idnum, ref.generation)] = i
    nombrados = {str(k).lstrip("/") for k in lector.named_destinations}
    al_disco, saltos, rotos, por_nombre, sueltos = [], 0, 0, 0, 0
    for p in lector.pages:
        for a in (p.get("/Annots") or []):
            o = a.get_object()
            if o.get("/Subtype") != "/Link":
                continue
            accion = o.get("/A")
            accion = accion.get_object() if accion is not None else None
            uri = str(accion.get("/URI")) if accion is not None and accion.get("/URI") else ""
            if uri:
                if uri.startswith("file:"):
                    al_disco.append(uri)
                continue
            if accion is not None and accion.get("/S") == "/GoTo":
                saltos += 1
                destino = accion.get("/D")
                ref = destino[0] if destino is not None and len(destino) else None
                if not hasattr(ref, "idnum") or (ref.idnum, ref.generation) not in paginas:
                    rotos += 1
                continue
            d = o.get("/Dest")
            if d is None:
                sueltos += 1
            elif isinstance(d, (str, bytes)) or isinstance(getattr(d, "get_object", lambda: d)(), str):
                por_nombre += 1
                if str(d).lstrip("/") not in nombrados:
                    rotos += 1

    def cuenta(bs):
        n = 0
        for b in bs:
            n += cuenta(b) if isinstance(b, list) else 1
        return n

    marcadores = cuenta(lector.outline)
    if al_disco:
        falla("el PDF lleva %d enlaces al disco de quien lo compiló (%s…)"
              % (len(al_disco), al_disco[0][:52]))
    if rotos:
        falla("el PDF tiene %d saltos que no caen en ninguna página" % rotos)
    if marcadores < MINIMO_MARCADORES:
        falla("el PDF solo tiene %d marcadores: no se puede navegar" % marcadores)
    if not fallos:
        print("  PDF  · %d páginas · %d saltos internos · %d enlaces por nombre · "
              "%d marcadores · ni uno al disco."
              % (len(lector.pages), saltos, por_nombre, marcadores))


def revisa_word():
    if not WORD.exists():
        return falla("no está %s" % WORD.name)
    with zipfile.ZipFile(WORD) as z:
        xml = z.read("word/document.xml").decode("utf-8")
    try:
        xml_dom.parseString(xml)
    except Exception as e:
        return falla("el XML del Word no está bien formado: %s" % e)
    marcas = set(re.findall(r'<w:bookmarkStart w:id="\d+" w:name="([^"]+)"', xml))
    anclas = re.findall(r'<w:hyperlink w:anchor="([^"]+)"', xml)
    huerfanos = sorted({a for a in anclas if a not in marcas})
    malos = [m for m in marcas if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,39}", m)]
    abre = len(re.findall(r"<w:bookmarkStart", xml))
    cierra = len(re.findall(r"<w:bookmarkEnd", xml))
    if huerfanos:
        falla("el Word tiene %d hipervínculos sin marcador (%s)"
              % (len(huerfanos), ", ".join(huerfanos[:4])))
    if malos:
        falla("el Word tiene %d nombres de marcador que Word no admite (%s)"
              % (len(malos), ", ".join(malos[:3])))
    if abre != cierra:
        falla("el Word abre %d marcadores y cierra %d" % (abre, cierra))
    if not huerfanos and not malos and abre == cierra:
        print("  Word · %d marcadores · %d saltos internos · todos con destino."
              % (len(marcas), len(anclas)))


def main():
    print("Los enlaces de las dos piezas impresas\n")
    revisa_pdf()
    revisa_word()
    print()
    if fallos:
        sys.exit("%d problema(s). No se entrega." % len(fallos))
    print("Las dos piezas se navegan solas.")


if __name__ == "__main__":
    main()
