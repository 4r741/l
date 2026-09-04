#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pulsa uno a uno los enlaces del archivo único y comprueba dónde aterrizan.

    python3 verifica-unico.py

El archivo único mete los nueve documentos en la misma página y solo enseña uno.
Eso abre una clase de fallo que ningún examen del texto detecta: el enlace
existe, el destino existe, y aun así el lector pulsa y no llega —porque lo que
pide está en un documento que no está abierto, en la ficha de un puesto que no
es la que se ve, o dentro de un desplegable cerrado—. La única manera de saberlo
es pulsar los mil trescientos enlaces en un navegador de verdad y mirar dónde
queda la pantalla.

Se comprueba, por cada enlace:

  · que el destino exista;
  · que después de pulsar esté visible, y no dentro de algo plegado;
  · que la pantalla se haya movido hasta él.
"""
import pathlib
import sys

from playwright.sync_api import sync_playwright

RAIZ = pathlib.Path(__file__).parent

_v = {}
exec(compile((RAIZ / "version.py").read_text(encoding="utf-8"), "version.py", "exec"), _v)
CORTA = _v["CORTA"]

ARCHIVO = RAIZ / "export" / ("Giraldo-TODO-EN-UNO-v%s.html" % CORTA)
NAVEGADOR = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

# El desplazamiento es suave: un salto de tres mil píxeles tarda casi un segundo
# en llegar. No se mide con un plazo fijo —con uno corto se daban por rotos
# enlaces que solo estaban a mitad de camino, y con uno largo la comprobación
# entera pasaba de la media hora—: se espera a que la página deje de moverse.
ESPERA = 1800

# Cada enlace se marca antes de empezar. Se probaban por su posición en la
# lista, y la posición se mueve: abrir un desplegable o revelar un bloque añade
# enlaces al documento, de modo que el enlace número 40 dejaba de ser el mismo
# entre mirarlo y pulsarlo, y el informe acusaba a enlaces que nadie había
# tocado. Marcado, cada uno es él mismo de principio a fin.
LISTA = """(d) => [...document.getElementById(d).querySelectorAll('a[href^="#"]')]
   .map((a, i) => { a.dataset.probado = String(i); return {
     i, rot:(a.innerText || a.textContent || '').replace(/\\s+/g, ' ').trim().slice(0, 46),
     ancla:a.dataset.ancla || (a.getAttribute('href') || '').slice(1)}; })"""

PRUEBA = """async ([d, i, espera]) => {
  const sp = ms => new Promise(r => setTimeout(r, ms));
  const doc = document.getElementById(d);
  if (!doc || doc.hidden) return {ok:false, por:'el documento no está abierto', reabrir:true};
  /* volver arriba tiene que ser instantáneo: la página se desplaza con
     suavidad, y si la vuelta sigue en marcha cuando se pulsa, las dos
     animaciones se estorban y el enlace parece que no mueve nada. */
  const hoja = document.documentElement, comoEra = hoja.style.scrollBehavior;
  hoja.style.scrollBehavior = 'auto';
  window.scrollTo(0, 0);
  hoja.style.scrollBehavior = comoEra;
  await sp(60);
  const a = doc.querySelector('a[data-probado="' + i + '"]');
  if (!a) return {ok:false, por:'el enlace ya no está'};
  const quiere = a.dataset.ancla || (a.getAttribute('href') || '').slice(1);
  if (!quiere) return {ok:true};

  /* «portada-doc» y otros rótulos de apartado se repiten en los nueve
     documentos: se busca dentro del que está abierto, no en el primero que
     aparezca en la página. */
  const donde = () => {
    const fuera = document.querySelector('.doc:not([hidden])');
    const dest = document.getElementById(quiere)
              || (fuera && fuera.querySelector('[data-ap="' + CSS.escape(quiere) + '"]'))
              || doc.querySelector('[data-ap="' + CSS.escape(quiere) + '"]');
    return {fuera, dest};
  };
  const llega = el => {
    const r = el.getBoundingClientRect();
    return r.top > -170 && r.top < innerHeight - 40;
  };
  const tapado = el => {
    let v = el;
    while (v) { if (v.hidden) return v.id || v.className; v = v.parentElement; }
    return null;
  };

  a.click();
  /* Se espera a que la página llegue, no un plazo fijo: el desplazamiento es
     suave y un salto de tres mil píxeles tarda casi un segundo, mientras que
     la mayoría llega en una décima. Con un plazo corto se daban por rotos
     enlaces que solo estaban a mitad de camino; con uno largo, la
     comprobación entera pasaba de la media hora. */
  let pasado = 0, sitio = donde();
  while (pasado < espera) {
    if (sitio.dest && !tapado(sitio.dest) && llega(sitio.dest)) break;
    await sp(90); pasado += 90; sitio = donde();
  }
  const fuera = sitio.fuera, dest = sitio.dest;
  const salio = !fuera || fuera.id !== d;
  if (!dest) return {ok:false, por:'el destino no existe', reabrir:salio};
  const oculto = tapado(dest);
  if (oculto) return {ok:false, por:'aterriza en algo plegado (' + oculto + ')', reabrir:salio};
  if (llega(dest)) return {ok:true, reabrir:salio};
  return {ok:false, por:'la pantalla no llega: ' +
      Math.round(dest.getBoundingClientRect().top) + ' px', reabrir:salio};
}"""

ABRE = """async (d) => {
  const sp = ms => new Promise(r => setTimeout(r, ms));
  const b = document.querySelector('[data-ir-a="' + d + '"]');
  if (b) { b.click(); await sp(320); }
  window.scrollTo(0, 0);
  const x = document.getElementById(d);
  return !!x && !x.hidden;
}"""


def main():
    if not ARCHIVO.exists():
        sys.exit("  falta %s: ejecute antes python3 build-export.py" % ARCHIVO.name)
    with sync_playwright() as pw:
        nav = pw.chromium.launch(executable_path=NAVEGADOR)
        pg = nav.new_context(viewport={"width": 1440, "height": 950}).new_page()
        pg.goto(ARCHIVO.as_uri())
        pg.wait_for_timeout(1600)
        docs = pg.evaluate("[...document.querySelectorAll('.doc')].map(d=>d.id)")
        total = 0
        fallos = []
        for d in docs:
            if not pg.evaluate(ABRE, d):
                fallos.append(("(el conmutador)", d, "el documento no abre"))
                continue
            enlaces = pg.evaluate(LISTA, d)
            for e in enlaces:
                r = pg.evaluate(PRUEBA, [d, e["i"], ESPERA])
                total += 1
                if not r["ok"]:
                    fallos.append(("%s · %s" % (d, e["rot"]), e["ancla"], r["por"]))
                if r.get("reabrir"):
                    pg.evaluate(ABRE, d)
        nav.close()

    if fallos:
        print("  %d enlaces del archivo único no llevan a donde dicen:" % len(fallos))
        vistos = set()
        for rot, ancla, por in fallos:
            clave = (rot.split(" · ")[0], ancla, por)
            if clave in vistos:
                continue
            vistos.add(clave)
            print("    ✗ «%s» → #%s · %s" % (rot, ancla, por))
        sys.exit(1)
    print("  %d enlaces del archivo único pulsados: todos llegan a donde dicen." % total)


if __name__ == "__main__":
    main()
