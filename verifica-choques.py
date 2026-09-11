"""Ningún texto encima de otro, y ninguno por debajo de la barra.

Este comprobador nace de una captura que mandó quien usa esto, hecha en su
portátil, donde se veía lo que yo no había visto nunca: el rótulo del centro y
las primeras cifras del censo corriendo POR DEBAJO de la barra de arriba, y el
lema metiéndose dentro del párrafo siguiente.

Los dos defectos llevaban versiones enteras ahí. No los cacé porque mis
barridos medían una sola cosa —que nada se saliera de la pantalla a lo ancho—
y un texto encima de otro no se sale de la pantalla: se queda dentro, encima
de otro. Medir lo que es fácil de medir no es lo mismo que comprobar.

Aquí se mide caja contra caja, a siete tamaños que incluyen los de un portátil
de verdad, que es donde aparecieron:

  · un texto cuya caja se cruza con la de otro texto;
  · un texto que queda por debajo de la barra, que es fija y lo tapa.

Se miran solo los nodos de hoja con texto: comparar contenedores daría por
solapado a todo padre con su hijo, que es lo normal y no es un defecto.
"""

import pathlib
import sys

from playwright.sync_api import sync_playwright

RAIZ = pathlib.Path(__file__).resolve().parent
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

# Portátiles de verdad, más un monitor grande y una pantalla corta.
TAMANOS = [(1024, 640), (1100, 700), (1280, 700), (1280, 800),
           (1366, 768), (1440, 900), (1680, 1050)]

# Lo que se superpone A PROPÓSITO no es un defecto y no se cuenta: el número
# de cada sección es una marca de agua puesta detrás del titular, y las
# diapositivas se componen en capas. Se miran solo elementos en el flujo
# normal —nada posicionado—, opacos, y se exige que el cruce sea grande: dos
# cajas que se rozan un píxel por el redondeo de una línea no se pisan.
CODIGO = """() => {
  const fuera = [];
  const enFlujo = (e) => {
    const c = getComputedStyle(e);
    if (c.position !== 'static') return false;
    /* Un elemento «inline» no tiene una caja: tiene una por cada línea que
       ocupa, y la que devuelve el navegador las envuelve todas. Esa envolvente
       se cruza con la de sus vecinos por definición, sin que nada se pise en
       la pantalla. Se miran solo cajas de verdad. */
    if (c.display === 'inline') return false;
    const r = e.getBoundingClientRect();
    if (r.width < 2 || r.height < 2) return false;
    if (parseFloat(c.opacity) < 0.9) return false;
    let a = e;
    while (a && a !== document.body) {
      const ca = getComputedStyle(a);
      if (ca.position === 'absolute' || ca.position === 'fixed') return false;
      if (parseFloat(ca.opacity) < 0.9) return false;
      if (a.classList.contains('dia') || a.classList.contains('slide')) return false;
      /* Un desplegable cerrado tiene alto cero y recorta lo que lleva dentro.
         Sus hijos siguen declarando la caja que tendrían si se abriera, y esas
         cajas se cruzan entre sí sin que en la pantalla se vea nada. No es un
         defecto: es contenido plegado. */
      if (/(hidden|clip)/.test(ca.overflow + ca.overflowY) &&
          a.getBoundingClientRect().height < r.height - 2) return false;
      a = a.parentElement;
    }
    return true;
  };
  const cruce = (a, b) => {
    const x = Math.min(a.right, b.right) - Math.max(a.left, b.left);
    const y = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
    if (x <= 1 || y <= 1) return 0;
    const menor = Math.min(a.width * a.height, b.width * b.height);
    return menor ? (x * y) / menor : 0;
  };
  const hoja = (e) => e.children.length === 0 && e.offsetHeight > 0 &&
                      (e.innerText || '').trim().length > 1 && enFlujo(e);
  const sec = document.querySelector('.sec.es-on');
  if (!sec) return fuera;
  const tope = document.querySelector('.tope');
  const els = [...sec.querySelectorAll('*')].filter(hoja);

  if (tope) {
    const t = tope.getBoundingClientRect();
    els.forEach(e => {
      const r = e.getBoundingClientRect();
      if (r.top < t.bottom - 2 && r.bottom > t.top + 2 &&
          r.left < t.right && r.right > t.left)
        fuera.push({q: 'bajo la barra',
                    a: (e.innerText || '').trim().slice(0, 40), b: ''});
    });
  }
  for (let i = 0; i < els.length; i++)
    for (let j = i + 1; j < els.length; j++) {
      const a = els[i].getBoundingClientRect(), b = els[j].getBoundingClientRect();
      if (cruce(a, b) > 0.3)
        fuera.push({q: 'texto sobre texto',
                    a: (els[i].innerText || '').trim().slice(0, 30),
                    b: (els[j].innerText || '').trim().slice(0, 30)});
    }
  return fuera;
}"""


def main():
    web = RAIZ / "centro.html"
    if not web.exists():
        print("  no hay centro.html que mirar")
        return 0
    malas = []
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        for an, al in TAMANOS:
            ctx = b.new_context(viewport={"width": an, "height": al})
            pg = ctx.new_page()
            pg.goto(web.as_uri())
            pg.wait_for_timeout(1100)
            secs = pg.evaluate("() => [...document.querySelectorAll('.sec')].map(s => s.id)")
            for sid in secs:
                pg.evaluate("(s) => document.querySelector('[data-ir-sec=\"' + s + '\"]')?.click()", sid)
                pg.wait_for_timeout(260)
                for c in pg.evaluate(CODIGO):
                    malas.append((an, al, sid, c))
            ctx.close()
        b.close()
    if not malas:
        print("nada se monta encima de nada: %d tamaños × %d secciones."
              % (len(TAMANOS), len(secs)))
        return 0
    print("textos que se pisan o que quedan bajo la barra:")
    for an, al, sid, c in malas[:18]:
        print("   %dx%d [%s] %-16s «%s»%s"
              % (an, al, sid, c["q"], c["a"], (" / «%s»" % c["b"]) if c["b"] else ""))
    print("   (%d en total)" % len(malas))
    return 1


if __name__ == "__main__":
    sys.exit(main())
