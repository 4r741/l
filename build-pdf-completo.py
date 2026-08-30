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
import pathlib
import subprocess
import sys

from pypdf import PdfWriter, PdfReader
from playwright.sync_api import sync_playwright

RAIZ = pathlib.Path(__file__).parent

_v = {}
exec(compile((RAIZ / "version.py").read_text(encoding="utf-8"), "version.py", "exec"), _v)
VERSION, FECHA = _v["VERSION"], _v["FECHA"]

PDFS = RAIZ / "export" / "pdf"
SALIDA = RAIZ / "export" / ("Sistema-Documental-Giraldo-v%s.pdf" % VERSION)
NAVEGADOR = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

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
    ("Protocolo-Primera-Visita-Giraldo-v%s.pdf", "Protocolo de Primera Visita",
     "Troncal", "Las doce fases de la primera visita, minuto a minuto"),
    ("Otros-Documentos-Giraldo-v%s.pdf", "Otros documentos del sistema",
     "Troncal", "Los catorce documentos de apoyo, del compendio maestro al programa de cuidado"),
    ("Captura-Linea-Base-Giraldo-v%s.pdf", "Captura de la línea base",
     "Instrumento", "Los diez indicadores y los cinco números, mes a mes"),
]

PORTADA = """<!doctype html>
<html lang="es"><head><meta charset="utf-8"><style>
@page{size:A4;margin:0}
*{margin:0;padding:0;box-sizing:border-box}
body{
  font-family:Georgia,'Times New Roman',serif;color:#172420;background:#EFEFEA;
  -webkit-print-color-adjust:exact;print-color-adjust:exact;
}
.hoja{width:210mm;height:297mm;padding:32mm 24mm;display:flex;flex-direction:column;page-break-after:always}
.hoja:last-child{page-break-after:auto}
.marca{font-family:'Courier New',monospace;font-size:8.5pt;letter-spacing:.22em;text-transform:uppercase;color:#5C6B66}
h1{font-size:46pt;line-height:1.02;letter-spacing:-.02em;font-weight:400;margin-top:14mm}
h1 em{font-style:italic;color:#0E5F58;display:block}
.bajada{margin-top:9mm;font-size:12pt;line-height:1.55;max-width:118mm;color:#3A4744}
.regla{height:1px;background:#C9CFC9;margin:11mm 0}
.datos{display:flex;gap:14mm;font-family:'Courier New',monospace;font-size:8.5pt;
       letter-spacing:.13em;text-transform:uppercase;color:#5C6B66;line-height:1.9}
.pie{margin-top:auto;font-size:9.5pt;color:#5C6B66;line-height:1.6;max-width:130mm}
.pie b{color:#172420}
h2{font-size:26pt;font-weight:400;letter-spacing:-.01em;margin-top:10mm}
.idx{margin-top:10mm;width:100%;border-collapse:collapse}
.idx td{padding:5.2mm 0;border-bottom:1px solid #DDE1DC;vertical-align:top}
/* la última fila no lleva raya: se la come la del pie y quedaban dos */
.idx tr:last-child td{border-bottom:0}
.idx .n{font-family:'Courier New',monospace;font-size:9pt;color:#0E5F58;width:11mm;padding-top:6.4mm}
.idx .t{font-size:14pt}
.idx .t small{display:block;font-family:'Courier New',monospace;font-size:7.6pt;
              letter-spacing:.14em;text-transform:uppercase;color:#5C6B66;margin-bottom:1.4mm}
.idx .t p{font-size:9.5pt;color:#5C6B66;margin-top:1.6mm;max-width:112mm;line-height:1.5}
.idx .p{font-family:'Courier New',monospace;font-size:10pt;text-align:right;
        white-space:nowrap;width:26mm;padding-top:6.2mm}
.nota{margin-top:auto;font-size:9pt;color:#5C6B66;line-height:1.6;max-width:130mm;
      border-top:1px solid #C9CFC9;padding-top:6mm}
</style></head><body>

<section class="hoja">
  <p class="marca">Centro de Excelencia Implantológica Giraldo · Rúa Bolivia nº 2 · Vigo</p>
  <h1>Sistema<br>documental<em>completo</em></h1>
  <p class="bajada">Los siete documentos que gobiernan y operan el centro, en un solo cuaderno: qué creemos, qué apostamos, qué se decide y cómo se ejecuta, fase a fase y puesto a puesto.</p>
  <div class="regla"></div>
  <div class="datos">
    <div>Versión @VERSION@<br>@FECHA@</div>
    <div>Siete documentos<br>@PAGINAS@ páginas</div>
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


def main():
    faltan = [n % VERSION for n, *_ in PARTES if not (PDFS / (n % VERSION)).exists()]
    if faltan:
        sys.exit("  faltan PDF por documento: %s\n  ejecute antes python3 build-pdf.py" % ", ".join(faltan))

    # 1 · cuánto ocupa cada parte, para poder numerar el índice de verdad
    cuentas = [paginas(PDFS / (n % VERSION)) for n, *_ in PARTES]
    total = sum(cuentas) + 2                      # las dos hojas de portada e índice
    arranques, cursor = [], 3                     # la primera parte empieza en la 3
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
                   .replace("@PAGINAS@", str(total)).replace("@FILAS@", "\n    ".join(filas)))
    tmp = RAIZ / "export" / "_portada.html"
    tmp.write_text(html, encoding="utf-8")

    # 2 · portada e índice a PDF
    portada = RAIZ / "export" / "_portada.pdf"
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
    assert paginas(portada) == 2, "la portada tiene que ocupar exactamente dos hojas"

    # 3 · el cuaderno, con cada documento como marcador
    escritor = PdfWriter()
    escritor.append(str(portada))
    escritor.add_outline_item("Portada e índice", 0)
    for (nombre, titulo, _c, _q), desde in zip(PARTES, arranques):
        escritor.append(str(PDFS / (nombre % VERSION)))
        escritor.add_outline_item(titulo, desde - 1)

    escritor.add_metadata({
        "/Title": "Sistema documental · Centro de Excelencia Implantológica Giraldo",
        "/Author": "Centro de Excelencia Implantológica Giraldo",
        "/Subject": "Los siete documentos del sistema, versión %s" % VERSION,
        "/Keywords": "uso interno, confidencial, v%s" % VERSION,
        "/Creator": "Sistema documental Giraldo",
    })
    with open(SALIDA, "wb") as f:
        escritor.write(f)

    tmp.unlink(); portada.unlink()
    print("  → export/%s · %d páginas · %d KB"
          % (SALIDA.name, paginas(SALIDA), SALIDA.stat().st_size // 1024))


if __name__ == "__main__":
    main()
