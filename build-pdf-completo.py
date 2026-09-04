#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Arma el sistema documental entero en un solo PDF, encuadernable.

    python3 build-pdf-completo.py

Los PDF por documento existían desde hace tiempo; lo que no existía era el
sistema completo en un solo cuaderno. Se construye a partir de aquellos —ya
paginados, con su cabecera de clasificación y su pie— y se les antepone una
portada y un índice general con los números de página reales, que solo pueden
calcularse después de saber cuánto ocupa cada parte. Cada documento queda además
como marcador del PDF, de modo que un lector lo abra por donde quiera.
"""
import json
import pathlib
import re
import subprocess
import sys

from pypdf import PdfWriter, PdfReader
from pypdf.generic import (ArrayObject, DictionaryObject, FloatObject,
                           NameObject, NullObject, NumberObject)
from playwright.sync_api import sync_playwright

RAIZ = pathlib.Path(__file__).parent

_v = {}
exec(compile((RAIZ / "version.py").read_text(encoding="utf-8"), "version.py", "exec"), _v)
VERSION, FECHA = _v["VERSION"], _v["FECHA"]

PDFS = RAIZ / "export" / "pdf"
SALIDA = RAIZ / "export" / ("Sistema-Documental-Giraldo-v%s.pdf" % VERSION)
NAVEGADOR = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

# El archivo HTML del que sale cada parte: es la clave que permite convertir un
# enlace «memoria.html#tes-foso» en un salto a la página del cuaderno donde vive
# ese apartado. Sin esta correspondencia, el PDF encuadernado conservaba enlaces
# al disco de la máquina que lo compiló —file:///…/manual.html—, que en la
# máquina de cualquier otro lector no llevan a ninguna parte.
ORIGEN = {
    "Plan-Direccion-Giraldo-v%s.pdf": "memoria.html",
    "Presentacion-Junta-Giraldo-v%s.pdf": "deck.html",
    "Plan-Marketing-Giraldo-v%s.pdf": "marketing.html",
    "Manual-Maestro-Giraldo-v%s.pdf": "manual.html",
    "Protocolos-Por-Puesto-Giraldo-v%s.pdf": "protocolos.html",
    "Protocolo-Primera-Visita-Giraldo-v%s.pdf": "index.html",
    "Otros-Documentos-Giraldo-v%s.pdf": "otros.html",
    "Captura-Linea-Base-Giraldo-v%s.pdf": "instrumentos/captura.html",
}

# El orden es el del sistema, no el del tamaño: primero lo que gobierna, luego
# lo que se presenta, después lo que se ejecuta y al final el instrumento.
PARTES = [
    ("Plan-Direccion-Giraldo-v%s.pdf", "Plan de Dirección",
     "Gobierno", "Qué creemos, qué apostamos y las quince decisiones que se someten a la Junta"),
    ("Presentacion-Junta-Giraldo-v%s.pdf", "Presentación de Junta",
     "Derivado", "Cuarenta y tres diapositivas extraídas del Plan de Dirección, para la sesión"),
    ("Plan-Marketing-Giraldo-v%s.pdf", "Plan Maestro de Marketing",
     "Plan", "Setenta y seis acciones sobre los doce estados del paciente"),
    ("Manual-Maestro-Giraldo-v%s.pdf", "Manual Maestro de Operaciones",
     "Troncal", "Las catorce fases del recorrido del paciente, los seis puestos y la puesta en marcha"),
    ("Protocolos-Por-Puesto-Giraldo-v%s.pdf", "Protocolos por puesto",
     "Vista operativa", "El protocolo del centro visto desde cada uno de los seis puestos"),
    ("Protocolo-Primera-Visita-Giraldo-v%s.pdf", "Protocolo de Primera Visita",
     "Troncal", "Las doce fases de la primera visita, minuto a minuto"),
    ("Otros-Documentos-Giraldo-v%s.pdf", "Otros documentos del sistema",
     "Troncal", "Los catorce documentos de apoyo, del compendio maestro al programa de cuidado"),
    ("Captura-Linea-Base-Giraldo-v%s.pdf", "Los números del centro",
     "Instrumento", "Los diez indicadores y los cinco números, mes a mes"),
]

# El número de documentos se cuenta, no se teclea: la portada decía «siete»
# desde antes de que existieran los Protocolos por puesto.
LETRA = {5: "Cinco", 6: "Seis", 7: "Siete", 8: "Ocho", 9: "Nueve", 10: "Diez"}
CUANTOS = LETRA[len(PARTES)]

PORTADA = """<!doctype html>
<html lang="es"><head><meta charset="utf-8"><style>
@page{size:A4;margin:0}
*{margin:0;padding:0;box-sizing:border-box}
body{
  font-family:Georgia,'Times New Roman',serif;color:#12232B;background:#EFEFEA;
  -webkit-print-color-adjust:exact;print-color-adjust:exact;
}
.hoja{width:210mm;height:297mm;padding:32mm 24mm;display:flex;flex-direction:column;page-break-after:always}
.hoja:last-child{page-break-after:auto}
.marca{font-family:'Courier New',monospace;font-size:8.5pt;letter-spacing:.22em;text-transform:uppercase;color:#3E5661}
h1{font-size:46pt;line-height:1.02;letter-spacing:-.02em;font-weight:400;margin-top:14mm}
h1 em{font-style:italic;color:#0B5C53;display:block}
.bajada{margin-top:9mm;font-size:12pt;line-height:1.55;max-width:118mm;color:#3A4744}
.regla{height:1px;background:#D7DEE1;margin:11mm 0}
.datos{display:flex;gap:14mm;font-family:'Courier New',monospace;font-size:8.5pt;
       letter-spacing:.13em;text-transform:uppercase;color:#3E5661;line-height:1.9}
.pie{margin-top:auto;font-size:9.5pt;color:#3E5661;line-height:1.6;max-width:130mm}
.pie b{color:#12232B}
h2{font-size:26pt;font-weight:400;letter-spacing:-.01em;margin-top:10mm}
.idx{margin-top:10mm;width:100%;border-collapse:collapse}
.idx td{padding:5.2mm 0;border-bottom:1px solid #DDE1DC;vertical-align:top}
/* la última fila no lleva raya: se la come la del pie y quedaban dos */
.idx tr:last-child td{border-bottom:0}
.idx .n{font-family:'Courier New',monospace;font-size:9pt;color:#0B5C53;width:11mm;padding-top:6.4mm}
.idx .t{font-size:14pt}
.idx .t small{display:block;font-family:'Courier New',monospace;font-size:7.6pt;
              letter-spacing:.14em;text-transform:uppercase;color:#3E5661;margin-bottom:1.4mm}
.idx .t p{font-size:9.5pt;color:#3E5661;margin-top:1.6mm;max-width:112mm;line-height:1.5}
.idx .p{font-family:'Courier New',monospace;font-size:10pt;text-align:right;
        white-space:nowrap;width:26mm;padding-top:6.2mm}
.nota{margin-top:auto;font-size:9pt;color:#3E5661;line-height:1.6;max-width:130mm;
      border-top:1px solid #D7DEE1;padding-top:6mm}
</style></head><body>

<section class="hoja">
  <p class="marca">Centro de Excelencia Implantológica Giraldo · Rúa Bolivia nº 2 · Vigo</p>
  <h1>Sistema<br>documental<em>completo</em></h1>
  <p class="bajada">Los @cuantos@ documentos que gobiernan y operan el centro, en un solo cuaderno: qué creemos, qué apostamos, qué se decide y cómo se ejecuta, fase a fase y puesto a puesto.</p>
  <div class="regla"></div>
  <div class="datos">
    <div>Versión @VERSION@<br>@FECHA@</div>
    <div>@CUANTOS@ documentos<br>@PAGINAS@ páginas</div>
    <div>Uso interno<br>Confidencial</div>
  </div>
  <p class="pie"><b>No medias sonrisas.</b><br>Documento de uso interno y confidencial. Contiene información económica, laboral y estratégica. No se difunde fuera de la organización sin autorización expresa de la Dirección General.</p>
</section>

<section class="hoja">
  <p class="marca">Índice general</p>
  <h2>Qué hay dentro</h2>
  <table class="idx">@FILAS@</table>
  <p class="nota">Todas las piezas comparten número de versión y fecha. Cada documento existe además por separado, en su propio archivo, y el sistema entero cabe en una sola página web que funciona sin conexión.</p>
</section>

</body></html>
"""


def paginas(ruta):
    return len(PdfReader(str(ruta)).pages)


def indice_de_destinos(ruta):
    """Ancla → (página dentro de este PDF, x, y).

    Chromium escribe un «destino con nombre» por cada ancla enlazada; build-pdf
    se encarga de que estén todas. Aquí se traduce cada destino a un número de
    página, que es lo que hace falta para apuntar dentro del cuaderno.
    """
    lector = PdfReader(str(ruta))
    donde = {}
    for i, pag in enumerate(lector.pages):
        ref = pag.indirect_reference
        if ref is not None:
            donde[(ref.idnum, ref.generation)] = i
    salida = {}
    try:
        destinos = lector.named_destinations
    except Exception:
        return salida
    for nombre, d in destinos.items():
        limpio = str(nombre).lstrip("/")
        if not limpio:
            continue
        try:
            ref = d.page
            clave = (ref.idnum, ref.generation) if hasattr(ref, "idnum") else None
            pag = donde.get(clave)
            if pag is None:
                continue
            salida[limpio] = (pag, d.left, d.top)
        except Exception:
            continue
    return salida


def salto_a(referencia, izquierda, arriba):
    """La acción PDF «ve a esta página, a esta altura»."""
    def num(v):
        try:
            return FloatObject(float(v))
        except Exception:
            return NullObject()
    return DictionaryObject({
        NameObject("/S"): NameObject("/GoTo"),
        NameObject("/D"): ArrayObject([referencia, NameObject("/XYZ"),
                                       num(izquierda), num(arriba), NumberObject(0)]),
    })


def recose_enlaces(escritor, mapa):
    """Convierte los enlaces «file:///…/manual.html#ancla» en saltos del cuaderno.

    Cada documento se escribió para vivir junto a sus hermanos en una carpeta, y
    sus referencias cruzadas son enlaces a esos archivos. Encuadernados en un
    solo PDF, esos enlaces apuntaban al disco de quien compiló: aquí se
    reescriben para que apunten a la página del propio cuaderno donde está lo
    que prometen. Devuelve (reescritos, sin destino, dejados).
    """
    hechos = perdidos = otros = 0
    huerfanos = []
    for pagina in escritor.pages:
        for anot in (pagina.get("/Annots") or []):
            obj = anot.get_object()
            if obj.get("/Subtype") != "/Link":
                continue
            accion = obj.get("/A")
            accion = accion.get_object() if accion is not None else None
            uri = str(accion.get("/URI")) if accion is not None and accion.get("/URI") else ""
            if not uri.startswith("file:"):
                if uri:
                    otros += 1
                continue
            camino, _, ancla = uri.partition("#")
            archivo = camino.rsplit("/", 1)[-1]
            destino = mapa.get((archivo, ancla)) or mapa.get((archivo, ""))
            if destino is None:
                perdidos += 1
                huerfanos.append(archivo + ("#" + ancla if ancla else ""))
                continue
            obj[NameObject("/A")] = salto_a(*destino)
            hechos += 1
    return hechos, perdidos, otros, huerfanos


def main():
    faltan = [n % VERSION for n, *_ in PARTES if not (PDFS / (n % VERSION)).exists()]
    if faltan:
        sys.exit("  faltan PDF por documento: %s\n  ejecute antes python3 build-pdf.py" % ", ".join(faltan))

    # 1 · cuánto ocupa cada parte, para poder numerar el índice de verdad
    cuentas = [paginas(PDFS / (n % VERSION)) for n, *_ in PARTES]

    tmp = RAIZ / "export" / "_portada.html"
    portada = RAIZ / "export" / "_portada.pdf"

    def dibuja(hojas):
        """La portada suponiendo que ella misma ocupa «hojas» páginas."""
        arranques, cursor = [], hojas + 1
        for c in cuentas:
            arranques.append(cursor)
            cursor += c
        filas = []
        for (nombre, titulo, clase, que), desde, cuantas in zip(PARTES, arranques, cuentas):
            filas.append(
                '<tr><td class="n">%02d</td>'
                '<td class="t"><small>%s</small>%s<p>%s</p></td>'
                '<td class="p">%d<br><span style="font-size:7.5pt;color:#8A968F">%d pág.</span></td></tr>'
                % (len(filas) + 1, clase, titulo, que, desde, cuantas))
        html = (PORTADA.replace("@VERSION@", VERSION).replace("@FECHA@", FECHA)
                       .replace("@CUANTOS@", CUANTOS).replace("@cuantos@", CUANTOS.lower())
                       .replace("@PAGINAS@", str(sum(cuentas) + hojas))
                       .replace("@FILAS@", "\n    ".join(filas)))
        tmp.write_text(html, encoding="utf-8")
        with sync_playwright() as pw:
            nav = pw.chromium.launch(executable_path=NAVEGADOR)
            pg = nav.new_page()
            pg.route("**/*", lambda r: r.abort()
                     if r.request.url.startswith(("http://", "https://")) else r.continue_())
            pg.goto(tmp.as_uri())
            pg.wait_for_timeout(500)
            pg.pdf(path=str(portada), format="A4", print_background=True,
                   margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
            nav.close()
        return arranques, paginas(portada)

    # 2 · portada e índice a PDF. La numeración depende de cuánto ocupe la propia
    # portada, y cuánto ocupa depende de cuántos documentos haya: se dibuja, se
    # mide y se vuelve a dibujar hasta que la cuenta cuadra consigo misma. Antes
    # había un 2 escrito a mano y al añadir un documento el sistema no compilaba.
    hojas = 2
    for _ in range(5):
        arranques, medidas = dibuja(hojas)
        if medidas == hojas:
            break
        hojas = medidas
    else:
        sys.exit("  la portada no se estabiliza en un número de hojas")

    # 3 · dónde cae cada ancla dentro del cuaderno ya encuadernado. Se calcula
    #     antes de unir nada: cada parte sabe en qué página interna vive cada una
    #     de sus anclas, y basta sumarle la página en la que empieza la parte.
    mapa = {}
    for (nombre, _t, _c, _q), desde in zip(PARTES, arranques):
        archivo = nombre % VERSION
        origen = ORIGEN.get(nombre, "")
        hoja = origen.rsplit("/", 1)[-1]
        destinos = indice_de_destinos(PDFS / archivo)
        # el documento entero, para los enlaces que no traen ancla
        mapa[(hoja, "")] = (desde - 1, 0, None)
        for ancla, (pag, izq, arr) in destinos.items():
            mapa[(hoja, ancla)] = (desde - 1 + pag, izq, arr)

    # 4 · el cuaderno, con cada documento y cada apartado como marcador
    escritor = PdfWriter()
    escritor.append(str(portada))
    escritor.add_outline_item("Portada e índice", 0)
    esquemas = {}
    ruta_esquema = PDFS / "_esquema.json"
    if ruta_esquema.exists():
        esquemas = json.loads(ruta_esquema.read_text(encoding="utf-8"))
    apartados = 0
    for (nombre, titulo, _c, _q), desde in zip(PARTES, arranques):
        archivo = nombre % VERSION
        escritor.append(str(PDFS / archivo))
        padre = escritor.add_outline_item(titulo, desde - 1)
        # y dentro del documento, un marcador por apartado: un cuaderno de
        # seiscientas páginas con ocho marcadores obliga a hojear
        hoja = ORIGEN.get(nombre, "").rsplit("/", 1)[-1]
        for ap in esquemas.get(archivo, []):
            sitio = mapa.get((hoja, ap["ancla"]))
            if sitio is None or not ap["rotulo"]:
                continue
            rotulo = ("%s · %s" % (ap["n"], ap["rotulo"])) if ap["n"] else ap["rotulo"]
            escritor.add_outline_item(rotulo, sitio[0], parent=padre)
            apartados += 1

    # 5 · y los saltos entre documentos, que hasta ahora apuntaban al disco
    recosidos, perdidos, otros, huerfanos = recose_enlaces(escritor, {
        clave: (escritor.pages[pag].indirect_reference, izq, arr)
        for clave, (pag, izq, arr) in mapa.items()
    })
    print("  · saltos entre documentos recosidos: %d" % recosidos)
    if huerfanos:
        print("  · enlaces sin destino en el cuaderno: %d (%s)"
              % (perdidos, ", ".join(sorted(set(huerfanos))[:6])))

    escritor.add_metadata({
        "/Title": "Sistema documental · Centro de Excelencia Implantológica Giraldo",
        "/Author": "Centro de Excelencia Implantológica Giraldo",
        "/Subject": "Los %s documentos del sistema, versión %s" % (CUANTOS.lower(), VERSION),
        "/Keywords": "uso interno, confidencial, v%s" % VERSION,
        "/Creator": "Sistema documental Giraldo",
    })
    with open(SALIDA, "wb") as f:
        escritor.write(f)

    tmp.unlink(); portada.unlink()
    print("  → export/%s · %d páginas · %d KB · %d marcadores de apartado"
          % (SALIDA.name, paginas(SALIDA), SALIDA.stat().st_size // 1024, apartados))


if __name__ == "__main__":
    main()
