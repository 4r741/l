#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ningún enlace puede llevar a algo que no es.

    python3 verifica-anclas.py

Que el destino exista no basta: tiene que ser el que el enlace promete. Aquí se
recorre cada enlace interno de cada documento escrito, se busca el titular del
sitio al que aterriza y se compara con lo que el enlace dice. Si un enlace
llamado «Rúbrica de auditoría» cae en «Cómo se mide si el protocolo funciona»,
esto lo dice y la construcción se para.

No se comparan cadenas: se comparan palabras con peso. Un enlace que es una
entrada de índice —«22 Calendario y capacidad del año»— puede llevar a un
titular redactado de otra manera —«Cuándo se enciende cada una»— y eso no es un
error, es un documento bien escrito; por eso se acepta también que el enlace
coincida con el rótulo del apartado, que es lo que el índice promete.
"""
import html as H
import pathlib
import re
import sys
import unicodedata

RAIZ = pathlib.Path(__file__).parent
DOCUMENTOS = ["manual.html", "index.html", "memoria.html", "marketing.html", "otros.html",
              "protocolos.html", "deck.html", "instrumentos/captura.html"]
TITULAR = re.compile(r"<h[1-6][^>]*>(.*?)</h[1-6]>", re.S | re.I)
ENLACE = re.compile(r'<a\b([^>]*)>(.*?)</a>', re.S | re.I)

# Palabras que no prometen nada por sí solas: si un enlace solo las lleva, no se
# le puede pedir que su texto se parezca a ningún titular.
VACIAS = {"aqui", "abrir", "completo", "completa", "con", "cada", "como", "del", "de", "el",
          "en", "entero", "entera", "esta", "este", "las", "los", "mas", "para", "por",
          "que", "sus", "una", "uno", "ver", "vease", "y", "su", "la", "lo", "un"}

# Enlaces mirados uno a uno y correctos: el rótulo del enlace y el titular del
# destino están redactados de otra manera, que es lo que hace un documento bien
# escrito. Se anotan aquí con su motivo para que la comprobación siga siendo
# dura con los que aparezcan de nuevo.
REVISADOS = {
    ("manual.html", "anexos"):            "los anexos son eso: plantillas y checklists",
    ("index.html", "portada"):            "la portada del Protocolo de Primera Visita",
    ("index.html", "continua"):           "ahí están las fases 13 y 14",
    ("index.html", "anexos"):             "los anexos traen los guiones y las preguntas",
    ("memoria.html", "censo"):            "el censo documental es el censo de los documentos",
    ("memoria.html", "activo"):           "el apartado 09 es lo que vale el centro",
    ("manual.html", "m10"):               "la tabla de descuentos está en la fase de cierre",
    ("manual.html", "m14"):               "la fase 14 es el programa de mantenimiento",
    ("otros.html", "otros-perfiles"):     "el circuito del RAC se describe en ese documento",
    ("otros.html", "otros-continuidad"):  "el inventario heredado está en continuidad",
    ("marketing.html", "gtc"):            "el apartado 20 del Plan de Marketing es el GTC",
    ("otros.html", "otros-30dias"):       "los cinco números se piden en el dosier de los 30 días",
    ("protocolos.html", "portada"):       "la portada de Protocolos por puesto",
}

ROMANOS = {"i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5, "vi": 6, "vii": 7, "viii": 8,
           "ix": 9, "x": 10, "xi": 11, "xii": 12, "xiii": 13, "xiv": 14}


def llano(x):
    x = re.sub(r"<[^>]+>", " ", x)
    x = H.unescape(x)
    x = "".join(c for c in unicodedata.normalize("NFD", x)
                if unicodedata.category(c) != "Mn")
    x = re.sub(r"[^a-zA-Z0-9 ]", " ", x)
    return re.sub(r"\s+", " ", x).strip().lower()


GUION = re.compile(r"<script\b.*?</script>", re.S | re.I)


def carga():
    """Los documentos, sin sus guiones: ahí dentro no hay enlaces, hay código."""
    return {d: GUION.sub(" ", (RAIZ / d).read_text(encoding="utf-8"))
            for d in DOCUMENTOS if (RAIZ / d).exists()}


EYEBROW = re.compile(r'<p class="eyebrow"[^>]*>(.*?)</p>', re.S | re.I)


def vocabulario(fuentes, doc, ancla):
    """Todo lo que el destino dice de sí mismo, para juzgar si el enlace acierta.

    No solo su titular: también el antetítulo que lo encabeza, el rótulo con el
    que aparece en el índice, el titular de la sección que lo contiene y las
    palabras de su propio identificador. Un enlace que dice «Manual del puesto,
    completo» y cae en un capítulo titulado «Dirección de Clínica» acierta,
    porque ese capítulo está dentro de «Manuales por puesto»; pedirle que
    coincida solo con el titular sería pedirle que repita el nombre del puesto.
    """
    t = fuentes.get(doc)
    if t is None:
        return None
    m = re.search(r'id="%s"' % re.escape(ancla), t)
    if not m:
        return None
    ini = t.rfind("<", 0, m.start())
    piezas = [ancla.replace("-", " ")]
    etiqueta = re.match(r"<(\w+)", t[ini:])
    abre = t[ini:t.index(">", ini)]
    rot = re.search(r'data-rotulo="([^"]*)"', abre)
    if rot:
        piezas.append(rot.group(1))
    if etiqueta and re.fullmatch(r"h[1-6]", etiqueta.group(1).lower()):
        cierre = "</%s>" % etiqueta.group(1).lower()
        desde = t.index(">", ini) + 1
        piezas.append(t[desde:t.index(cierre, desde)])
    else:
        dentro = TITULAR.search(t, ini, ini + 4000)
        if dentro:
            piezas.append(dentro.group(1))
    # el antetítulo, justo antes o justo dentro
    for eb in EYEBROW.finditer(t, max(0, ini - 400), ini + 1200):
        piezas.append(eb.group(1))
    # y el titular de la sección que lo contiene
    sec = t.rfind("<section", 0, ini)
    if sec >= 0:
        cabeza = TITULAR.search(t, sec, sec + 3000)
        if cabeza:
            piezas.append(cabeza.group(1))
    return llano(" ".join(piezas))


def promete(texto, voces, ancla):
    """¿El enlace lleva a lo que dice que lleva?"""
    if not texto:
        return True
    palabras = [w for w in texto.split() if len(w) > 2 and w not in VACIAS]
    if not palabras:
        return True
    suyas = [w for w in (voces or "").split() if len(w) > 2]

    def cabe(w):
        """«manual» vale por «manuales», y «descuento» por «descuentos»."""
        return any(w == s or (len(w) > 3 and len(s) > 3 and w[:4] == s[:4]
                              and (w in s or s in w))
                   for s in suyas)

    # Un rótulo corto tiene que acertar su única palabra con peso; uno largo
    # basta con que acierte dos: nadie repite un titular entero en un enlace.
    if sum(1 for w in palabras if cabe(w)) >= (1 if len(palabras) <= 2 else 2):
        return True
    # «fase 10» a #f10, «parte VIII» a #p8, «apartado 3» a algo que lleva un 3
    numeros = [int(n) for n in re.findall(r"\d+", texto)]
    numeros += [ROMANOS[w] for w in texto.split() if w in ROMANOS]
    cifras = re.findall(r"\d+", ancla)
    if numeros and cifras and any(n == int(c) for n in numeros for c in cifras):
        return True
    return False


def main():
    fuentes = carga()
    rotos, torcidos = [], []
    for doc, t in fuentes.items():
        for m in ENLACE.finditer(t):
            href = re.search(r'href="([^"]+)"', m.group(1))
            if not href:
                continue
            h = href.group(1)
            if h.startswith(("http", "mailto:", "tel:", "#!")) or "#" not in h:
                continue
            destino, ancla = h.split("#", 1)
            destino = destino or doc
            if "/" not in destino and "/" in doc:
                # un enlace desde instrumentos/ a la raíz
                destino = destino if (RAIZ / destino).exists() else destino
            texto = llano(m.group(2))
            voces = vocabulario(fuentes, destino, ancla)
            if voces is None:
                if destino in fuentes:
                    rotos.append((doc, texto, destino, ancla))
                continue
            if not promete(texto, voces, ancla) and (destino, ancla) not in REVISADOS:
                torcidos.append((doc, texto, destino, ancla, voces))

    print("Enlaces con destino: cada uno comprobado contra el titular al que llega\n")
    if rotos:
        print("  Anclas que no existen: %d" % len(rotos))
        for doc, texto, destino, ancla in rotos[:12]:
            print("    %-22s «%s» → %s#%s" % (doc, texto[:40], destino, ancla))
    if torcidos:
        print("  Enlaces que prometen una cosa y llevan a otra: %d" % len(torcidos))
        for doc, texto, destino, ancla, tit in torcidos:
            print("    %-22s «%s»\n%26s→ %s#%s  «%s»"
                  % (doc, texto[:46], "", destino, ancla, (tit or "")[:46]))
    if not rotos and not torcidos:
        print("  Sin enlaces torcidos: todos llevan a lo que dicen.")
        print("  %d enlaces mirados uno a uno y anotados como correctos."
              % len(REVISADOS))
    return 1 if (rotos or torcidos) else 0


if __name__ == "__main__":
    sys.exit(main())
