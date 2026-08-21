#!/usr/bin/env python3
"""Genera los PDF paginados de los documentos, listos para imprimir y repartir.

    python3 build-pdf.py

Cada PDF sale en A4 con márgenes de encuadernación, cabecera de clasificación y
pie con numeración «Página X de Y». Requiere Playwright con Chromium instalado.
"""
import pathlib

from playwright.sync_api import sync_playwright

RAIZ = pathlib.Path(__file__).parent
DESTINO = RAIZ / "export" / "pdf"
NAVEGADOR = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

# archivo de origen → (nombre del PDF, rótulo de cabecera, orientación)
DOCUMENTOS = {
    "memoria.html": ("Tesis-Direccion-Giraldo-v2.0.pdf", "Tesis de Dirección · v2.0", False),
    "manual.html": ("Manual-Maestro-Giraldo-v5.5.pdf", "Manual Maestro de Operaciones · v5.5", False),
    "index.html": ("Protocolo-Primera-Visita-Giraldo-v5.5.pdf", "Protocolo de Primera Visita · v5.5", False),
    "otros.html": ("Otros-Documentos-Giraldo-v1.3.pdf", "Otros documentos del sistema · v1.3", False),
    "deck.html": ("Presentacion-Junta-Giraldo-v2.0.pdf", "", True),
}

ESTILO_PIE = "font-family:Helvetica,Arial,sans-serif;font-size:7pt;color:#555;width:100%;padding:0 15mm;letter-spacing:.06em"


def cabecera(rotulo):
    return ('<div style="%s"><span>%s</span>'
            '<span style="float:right">USO INTERNO · CONFIDENCIAL</span></div>'
            % (ESTILO_PIE, rotulo.upper()))


def pie():
    return ('<div style="%s"><span>Centro de Excelencia Implantológica Giraldo</span>'
            '<span style="float:right">Página <span class="pageNumber"></span> '
            'de <span class="totalPages"></span></span></div>' % ESTILO_PIE)


def main():
    DESTINO.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        navegador = pw.chromium.launch(executable_path=NAVEGADOR)
        pagina = navegador.new_page()
        # sin red: las tipografías se resuelven con las de sistema si no están en caché
        pagina.route("**/*", lambda r: r.abort()
                     if r.request.url.startswith(("http://", "https://")) else r.continue_())
        for origen, (salida, rotulo, apaisado) in DOCUMENTOS.items():
            if not (RAIZ / origen).exists():
                continue
            pagina.goto((RAIZ / origen).as_uri())
            pagina.wait_for_timeout(900)
            # nada puede quedar sin revelar en el PDF
            pagina.evaluate("document.querySelectorAll('.reveal').forEach(e=>e.classList.add('in'))")
            opciones = dict(path=str(DESTINO / salida), print_background=True)
            if apaisado:
                opciones.update(width="297mm", height="167mm",
                                margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
            else:
                opciones.update(format="A4",
                                margin={"top": "18mm", "bottom": "20mm", "left": "15mm", "right": "15mm"},
                                display_header_footer=True,
                                header_template=cabecera(rotulo),
                                footer_template=pie())
            pagina.pdf(**opciones)
            print("  → export/pdf/%s · %d KB" % (salida, (DESTINO / salida).stat().st_size // 1024))
        navegador.close()


if __name__ == "__main__":
    main()
