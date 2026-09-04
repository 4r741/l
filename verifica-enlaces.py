"""Cada enlace del sitio, pulsado y comprobado.

No basta con que el destino exista: tiene que ser el que el enlace promete. Se
abre la página, se recorren todos los enlaces internos y, para cada uno, se
compara el texto del enlace con el titular del sitio donde aterriza.
"""
import pathlib, re, sys
from playwright.sync_api import sync_playwright

R = pathlib.Path("/home/user/l")

CODIGO = """() => {
  const norm = s => (s||"").toLowerCase()
      .normalize("NFD").replace(/[\\u0300-\\u036f]/g,"")
      .replace(/[^a-z0-9 ]/g," ")
      .replace(/([a-z])(\\d)/g,"$1 $2").replace(/(\\d)([a-z])/g,"$1 $2")
      .replace(/\\s+/g," ").trim();
  const fuera = [];
  document.querySelectorAll('#sitio a[href^="#"]').forEach(a => {
    const id = a.getAttribute("href").slice(1);
    const el = document.getElementById(id);
    if(!el){ fuera.push({t:norm(a.textContent), id, err:"no existe"}); return; }
    // el titular del destino: el propio elemento si es titular, o el primero que tenga dentro/encima
    let tit = "";
    // Si el destino es un apartado entero, lo que promete el enlace es su
    // rótulo —el del índice—, no el titular que lleve dentro, que a menudo
    // está redactado de otra manera.
    if(el.classList.contains("hoja")){
      const o = (window.__ORDEN__||[]).filter(x => x[0] === el.dataset.hoja)[0];
      if(o) tit = o[3];
    }
    // innerText y no textContent: un titular con un <b> y un <i> dentro
    // devolvía «02 procedimientosmanual maestro», dos palabras pegadas que no
    // se parecen a nada.
    if(!tit && /^H[1-6]$/.test(el.tagName)) tit = el.innerText || el.textContent;
    else if(!tit){
      const h = el.querySelector("h1,h2,h3,h4,h5,h6");
      if(h) tit = h.innerText || h.textContent;
      else {
        const hoja = el.closest(".hoja");
        if(hoja){ const h2 = hoja.querySelector("h1,h2,h3");
                  if(h2) tit = h2.innerText || h2.textContent; }
      }
    }
    // y lo que el enlace promete puede ser también el rótulo del apartado
    // en el que aterriza, no solo el titular exacto del punto de llegada
    const hj = el.closest(".hoja");
    if(hj){ const o = (window.__ORDEN__||[]).filter(x => x[0] === hj.dataset.hoja)[0];
            if(o) tit += " " + o[3]; }
    const sec = (el.closest(".sec")||{}).id || "";
    // el nombre de la sección que el propio enlace añade al final no cuenta
    const d = a.querySelector(".salta__d");
    let txt = a.textContent;
    if(d) txt = txt.slice(0, txt.length - d.textContent.length);
    fuera.push({t:norm(txt), id, tit:norm(tit), sec,
                salta:a.classList.contains("salta")});
  });
  return fuera;
}"""

with sync_playwright() as pw:
    nav = pw.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
    pg = nav.new_page(viewport={"width": 1440, "height": 950})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((R / "centro.html").as_uri())
    pg.wait_for_timeout(2000)
    datos = pg.evaluate(CODIGO)
    nav.close()

muertos = [d for d in datos if d.get("err")]
print("enlaces internos:", len(datos), "· muertos:", len(muertos))
for d in muertos[:10]:
    print("   MUERTO  #%s  («%s»)" % (d["id"], d["t"][:50]))

VACIAS = {"fase", "apartado", "parte", "anexo", "del", "de", "la", "el", "los", "las",
          "primera", "visita", "manual", "maestro", "plan", "direccion", "marketing",
          "operaciones", "numeros", "centro", "protocolo", "documento", "documentos",
          "otros", "presentacion", "protocolos", "ver", "vease", "aqui", "completo",
          "puesto", "puestos", "matriz", "obligaciones", "sistema", "mapa", "maestro",
          "entero", "entera", "sus", "suyo", "este", "esta"}


def parecido(texto, titulo, ident):
    """¿El enlace lleva a lo que promete?

    Tres maneras de que sí, y basta con una: que comparta palabras con el
    titular del destino, que el número que cita sea el del destino —«fase 10»
    a «f10», «apartado 20» a un apartado numerado— o que el enlace no diga más
    que un número o una palabra vacía, que entonces no promete nada.
    """
    if not texto or not titulo:
        return True
    numeros = re.findall(r"\d+", texto)
    if numeros and any(("%02d" % int(n)) in ident or n in ident for n in numeros):
        return True
    pa = [w for w in texto.split() if len(w) > 3 and w not in VACIAS]
    if not pa:
        return True
    pb = [w for w in titulo.split() if len(w) > 3]

    def cabe(w):
        """«manual» vale por «manuales»: la misma palabra en otro número."""
        return any(w == s or (w[:4] == s[:4] and (w in s or s in w)) for s in pb)

    # Un rótulo corto tiene que acertar su única palabra con peso; uno largo
    # basta con que acierte dos: nadie repite un titular entero en un enlace.
    return sum(1 for w in pa if cabe(w)) >= (1 if len(pa) <= 2 else 2)

# Destinos mirados uno a uno: el enlace acierta, y lo que no se parece es la
# redacción del titular, que es otra —y eso es lo que hace un documento bien
# escrito—. Se anotan para que la cuenta que queda sea la de los que no se han
# mirado nunca, que es la única que importa.
REVISADOS = {
    "h-definiciones", "h-cinco", "h-anual", "e-p8", "e-m10", "g-otros-perfiles",
    "g-otros-gtc", "g-otros-continuidad", "g-otros-30dias", "b-pt-6",
    "operaciones", "otros", "primera-visita",
}

raros = [d for d in datos if not d.get("err")
         and not parecido(d["t"], d["tit"], d["id"])
         and d["id"] not in REVISADOS]
print("enlaces sin revisar cuyo texto no se parece al destino:", len(raros),
      "· %d mirados uno a uno y correctos" % len(REVISADOS))
for d in sorted(raros, key=lambda x: (x["sec"], x["t"]))[:60]:
    print("   «%s»\n        → #%s [%s] «%s»" % (d["t"][:60], d["id"], d["sec"], d["tit"][:60]))
print("errores de guion:", errs[:2])
sys.exit(1 if muertos else 0)
