#!/usr/bin/env python3
"""Genera los PDF paginados de los documentos, listos para imprimir y repartir.

    python3 build-pdf.py

Cada PDF sale en A4 con márgenes de encuadernación, cabecera de clasificación y
pie con numeración «Página X de Y». La presentación sale en apaisado, una
diapositiva por página, y además en una segunda versión con el guion del ponente
impreso bajo cada diapositiva. Requiere Playwright con Chromium instalado.
"""
import json
import pathlib

from playwright.sync_api import sync_playwright

RAIZ = pathlib.Path(__file__).parent

# La versión no se teclea: sale de version.py, que es el único sitio donde vive.
_v = {}
exec(compile((RAIZ / "version.py").read_text(encoding="utf-8"), "version.py", "exec"), _v)
VERSION, FECHA, CORTA = _v["VERSION"], _v["FECHA"], _v["CORTA"]

DESTINO = RAIZ / "export" / "pdf"
NAVEGADOR = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

# Todo lo diferible se revela antes de imprimir; el guion del ponente solo se
# activa en la salida que lo pide.
REVELAR = "document.querySelectorAll('.reveal').forEach(e=>e.classList.add('in'))"

# Chromium solo escribe en el PDF un «destino con nombre» por cada ancla que
# alguien enlace dentro del propio documento. Sin destinos, un enlace que llega
# de otro documento no tiene adónde apuntar y el cuaderno encuadernado se queda
# con enlaces al disco de quien lo compiló. Así que antes de imprimir se añade,
# fuera de la caja de escritura, un enlace a cada ancla del documento: no ocupa
# ni una página y deja el PDF con un destino por ancla, que es lo que luego
# permite convertir los saltos entre documentos en saltos de verdad.
DESTINOS = """() => {
  const ids = [...document.querySelectorAll('[id]')]
      .map(e => e.id).filter(i => i && /^[A-Za-z0-9_.:-]+$/.test(i));
  const caja = document.createElement('div');
  caja.id = '__destinos'; caja.setAttribute('aria-hidden', 'true');
  caja.style.cssText = 'position:absolute;left:-9999px;top:0;width:1px;height:0;overflow:hidden';
  caja.innerHTML = ids.map(i => '<a href="#' + i + '">.</a>').join('');
  document.body.appendChild(caja);
  return ids.length;
}"""

# El esquema del cuaderno: qué apartados tiene cada documento, en su orden y con
# su rótulo, para que el PDF completo lleve marcadores hasta el apartado y no
# solo hasta el documento.
ESQUEMA = """() => [...document.querySelectorAll('article.ap')].map(a => ({
  ancla: a.dataset.ap || '',
  rotulo: (a.dataset.rotulo || '').trim(),
  n: (a.dataset.n || '').trim(),
  grupo: (a.dataset.grupo || '').trim()
})).filter(x => x.ancla)"""
PONENTE = ("document.body.classList.add('modo-ponente');"
           "document.querySelectorAll('.nota').forEach(n=>n.hidden=false)")

# origen → (nombre del PDF, rótulo de cabecera, apaisado, preparación extra)
# El rótulo de cabecera llevaba la versión tecleada, de modo que cada página de
# cada PDF anunciaba una versión que ya no era la del archivo. Sale de VERSION,
# como todo lo demás.
DOCUMENTOS = [
    ("memoria.html", "Plan-Direccion-Giraldo-v%s.pdf" % VERSION,
     "Plan de Dirección · v%s" % VERSION, False, ""),
    ("manual.html", "Manual-Maestro-Giraldo-v%s.pdf" % VERSION,
     "Manual Maestro de Operaciones · v%s" % VERSION, False, ""),
    ("protocolos.html", "Protocolos-Por-Puesto-Giraldo-v%s.pdf" % VERSION,
     "Protocolos por puesto · v%s" % VERSION, False, ""),
    ("index.html", "Protocolo-Primera-Visita-Giraldo-v%s.pdf" % VERSION,
     "Protocolo de Primera Visita · v%s" % VERSION, False, ""),
    ("otros.html", "Otros-Documentos-Giraldo-v%s.pdf" % VERSION,
     "Otros documentos del sistema · v%s" % VERSION, False, ""),
    ("marketing.html", "Plan-Marketing-Giraldo-v%s.pdf" % VERSION,
     "Plan Maestro de Marketing · v%s" % VERSION, False, ""),
    ("instrumentos/captura.html", "Captura-Linea-Base-Giraldo-v%s.pdf" % VERSION,
     "Los números del centro · v%s" % VERSION, False, ""),
    ("deck.html", "Presentacion-Junta-Giraldo-v%s.pdf" % VERSION, "", True, ""),
    ("deck.html", "Guion-del-Ponente-Giraldo-v%s.pdf" % VERSION, "", "guion", PONENTE),
]

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
    esquemas = {}
    with sync_playwright() as pw:
        navegador = pw.chromium.launch(executable_path=NAVEGADOR)
        pagina = navegador.new_page()
        # sin red: las tipografías se resuelven con las de sistema si no están en caché
        pagina.route("**/*", lambda r: r.abort()
                     if r.request.url.startswith(("http://", "https://")) else r.continue_())
        for origen, salida, rotulo, apaisado, preparar in DOCUMENTOS:
            if not (RAIZ / origen).exists():
                continue
            pagina.goto((RAIZ / origen).as_uri())
            pagina.wait_for_timeout(900)
            pagina.evaluate(REVELAR)
            if preparar:
                pagina.evaluate(preparar)
                pagina.wait_for_timeout(200)
            pagina.evaluate(DESTINOS)
            esquemas[salida] = pagina.evaluate(ESQUEMA)
            opciones = dict(path=str(DESTINO / salida), print_background=True)
            if apaisado == "guion":
                # el guion usa la hoja con nombre propio que declara su propio CSS
                opciones.update(prefer_css_page_size=True)
            elif apaisado:
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
    (DESTINO / "_esquema.json").write_text(
        json.dumps(esquemas, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
