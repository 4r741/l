#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rasteriza las figuras para el documento de Word.

    python3 figuras-png.py

Las figuras del sistema son SVG escritos a mano, y toman su color y su
tipografía de la hoja de estilos de la página: sacadas del documento y
renderizadas sueltas perderían las dos. Así que se abren en su propia página y
se fotografía cada una donde está, al doble de resolución para que aguanten el
papel.
"""
import json
import pathlib
import re
import sys

from playwright.sync_api import sync_playwright

RAIZ = pathlib.Path(__file__).parent
DESTINO = RAIZ / "export" / "figuras"
NAVEGADOR = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

DOCUMENTOS = ["memoria.html", "marketing.html", "manual.html", "index.html"]


def main():
    DESTINO.mkdir(parents=True, exist_ok=True)
    for viejo in DESTINO.glob("*.png"):
        viejo.unlink()

    censo = {}
    with sync_playwright() as pw:
        nav = pw.chromium.launch(executable_path=NAVEGADOR)
        # al doble: una figura de 880 px sale a 1760 y se imprime sin escalones
        ctx = nav.new_context(viewport={"width": 1400, "height": 1000},
                              device_scale_factor=2)
        pg = ctx.new_page()
        pg.route("**/*", lambda r: r.abort()
                 if r.request.url.startswith(("http://", "https://")) else r.continue_())
        for doc in DOCUMENTOS:
            ruta = RAIZ / doc
            if not ruta.exists():
                continue
            pg.goto(ruta.as_uri())
            pg.wait_for_timeout(900)
            # todo lo diferido a la vista: si no, se fotografía una figura en blanco
            pg.evaluate("document.querySelectorAll('.reveal').forEach(e=>e.classList.add('in'))")
            pg.wait_for_timeout(300)
            svgs = pg.query_selector_all("main svg")
            fichas = []
            for i, svg in enumerate(svgs):
                caja = svg.bounding_box()
                if not caja or caja["width"] < 200 or caja["height"] < 80:
                    continue          # los iconos no son figuras
                svg.scroll_into_view_if_needed()
                pg.wait_for_timeout(120)
                nombre = "%s-%02d.png" % (doc.replace(".html", "").replace("/", "-"),
                                          len(fichas))
                svg.screenshot(path=str(DESTINO / nombre))
                pie = svg.evaluate("""el=>{
                  const f = el.closest('figure');
                  const c = f && f.querySelector('figcaption');
                  return c ? c.textContent.replace(/\\s+/g,' ').trim() : '';
                }""")
                rotulo = svg.get_attribute("aria-label") or ""
                fichas.append({"archivo": nombre,
                               "ancho": round(caja["width"]), "alto": round(caja["height"]),
                               "pie": pie, "rotulo": rotulo})
            censo[doc] = fichas
            print("  %-28s %d figuras" % (doc, len(fichas)))
        nav.close()

    (DESTINO / "censo.json").write_text(
        json.dumps(censo, ensure_ascii=False, indent=1), encoding="utf-8")
    total = sum(len(v) for v in censo.values())
    peso = sum(p.stat().st_size for p in DESTINO.glob("*.png")) // 1024
    print("  → export/figuras/ · %d figuras · %d KB" % (total, peso))
    if total == 0:
        sys.exit("  no se ha rasterizado ninguna figura")


if __name__ == "__main__":
    main()
