"""Ninguna sección enseña la misma cosa dos veces.

Este comprobador nace de un error concreto y repetido. En la versión 22 se
añadió el tablero de las catorce fases DELANTE de la rejilla que ya las
dibujaba, con el razonamiento de que así «no se borraba nada». El resultado
eran las catorce fases escritas dos veces en la misma pantalla —los mismos
nombres, los mismos minutos, una lista debajo de la otra—, y nadie se dio
cuenta hasta que lo vio quien lo tenía que usar.

Es un error fácil de cometer cuando se añade sin mirar lo que ya había, y
conservar no es lo mismo que duplicar: el texto de las fases vive en Primera
Visita y en Operaciones, y ahí sigue intacto; lo que sobraba era una segunda
lista de nombres.

La regla: dentro de una misma sección, ningún NOMBRE distintivo puede
aparecer dos veces. Nombre es lo que titula algo —un titular, el rótulo de
una ficha, el nombre de una fase, el de una sección del índice—, no el texto
corrido ni los rótulos de estructura, que sí se repiten con toda la razón
(«Portada», «3 apartados», o las etiquetas de una tabla fila tras fila).
"""

import pathlib
import re
import sys
import unicodedata

from playwright.sync_api import sync_playwright

RAIZ = pathlib.Path(__file__).resolve().parent
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

# Rótulos de estructura: repetirlos es lo correcto, no un defecto.
ESTRUCTURA = {
    "portada", "marcar", "superada", "ejecuta", "se informa",
    "ejecuta y responde", "consultado", "informado", "responsable",
    "leerlo entero seguido", "volver al indice", "volver", "abrir",
    "ver la ficha", "empezar el recorrido", "cerrar",
}

# De dónde se sacan los nombres: lo que titula algo.
NOMBRES = ("h1, h2, h3, h4, .tab__r, .nodo__r, .arb__r, .puerta b, "
           ".rutacard b, .atajo span, .censo__i span, .hecho b")

# Dos veces el mismo nombre no siempre es un defecto: un índice de los seis
# puestos y, tres mil píxeles más abajo, el manual de ese puesto, dicen su
# nombre dos veces con toda la razón. Lo que no vale es enseñarlo dos veces
# JUNTO, que es lo que se ve como duplicado. Se toma la posición de cada uno
# y solo se señalan los que caben en la misma pantalla larga.
CERCA = 1200

CODIGO = """(sel) => {
  const sec = document.querySelector('.sec.es-on');
  if (!sec) return [];
  return [...sec.querySelectorAll(sel)]
    .filter(e => e.offsetHeight > 0)
    .map(e => ({t: (e.innerText || e.textContent || '').trim(),
                y: Math.round(e.getBoundingClientRect().top + window.scrollY)}))
    .filter(o => o.t.length > 8 && o.t.length < 90);
}"""


def pela(t):
    t = unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()


def main():
    web = RAIZ / "centro.html"
    if not web.exists():
        print("  no hay centro.html que mirar")
        return 0
    malas = []
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        pg = b.new_context(viewport={"width": 1440, "height": 900}).new_page()
        pg.goto(web.as_uri())
        pg.wait_for_timeout(1500)
        secs = pg.evaluate("() => [...document.querySelectorAll('.sec')].map(s => s.id)")
        for sid in secs:
            pg.evaluate("(s) => document.querySelector('[data-ir-sec=\"' + s + '\"]')?.click()", sid)
            pg.wait_for_timeout(420)
            nombres = pg.evaluate(CODIGO, NOMBRES)
            porNombre = {}
            for o in nombres:
                k = pela(o["t"])
                if k and k not in ESTRUCTURA:
                    porNombre.setdefault(k, []).append(o["y"])
            for k, ys in porNombre.items():
                ys.sort()
                juntos = sum(1 for a, b in zip(ys, ys[1:]) if b - a <= CERCA)
                if juntos:
                    malas.append((sid, k, juntos + 1))
        b.close()
    if not malas:
        print("ninguna sección enseña dos veces el mismo nombre: %d miradas."
              % len(secs))
        return 0
    print("nombres repetidos dentro de una misma sección:")
    for sid, t, n in sorted(malas, key=lambda x: -x[2])[:20]:
        print("   [%s] x%d  «%s»" % (sid, n, t[:64]))
    return 1


if __name__ == "__main__":
    sys.exit(main())
