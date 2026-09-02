#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""El tablero de mando de cada documento. No toca ni una palabra del texto.

    python3 tablero.py

Un documento de gobierno no se abre por el principio: se abre por la pregunta
que uno trae. Antes, la entrada de cada documento era un titular y una columna
de texto, y para saber qué había dentro tocaba abrir un menú y leer una lista.

Ahora la entrada es un tablero: las cifras del documento delante, y debajo una
tarjeta por parte con sus apartados dentro. Se ve de un vistazo qué hay, cuánto
hay y por dónde entrar, y el texto se abre al pulsar.

Se construye aquí, en el HTML, y no en el navegador: así existe también cuando
no se ejecutan guiones y al imprimir. Las cifras salen de la propia portada del
documento —de su ficha de datos— y los apartados, de las marcas que dejó
paginar.py. Nada se inventa.
"""
import html as H
import pathlib
import re
import sys
import types

RAIZ = pathlib.Path(__file__).parent

menu = types.ModuleType("menu")
menu.__file__ = str(RAIZ / "menu.py")
exec(compile((RAIZ / "menu.py").read_text(encoding="utf-8"), menu.__file__, "exec"),
     menu.__dict__)


# Qué es cada documento, en la voz con la que ya se presenta en el sistema.
FICHAS = {
    "memoria.html": ("Plan de Dirección", "Documento de gobierno · Junta Directiva",
                     "Qué creemos, qué apostamos y las quince decisiones que se someten a la Junta."),
    "marketing.html": ("Plan Maestro de Marketing", "Documento de dirección",
                       "Las 76 acciones sobre los 12 estados del paciente, y el programa "
                       "Giraldo Te Cuida."),
    "manual.html": ("Manual Maestro de Operaciones", "Documento troncal · Todo el equipo",
                    "Las 14 fases del recorrido, los 6 puestos, la matriz RACI, los "
                    "indicadores y los incentivos."),
    "index.html": ("Protocolo de Primera Visita", "Documento troncal · Recepción, Doctor, RAC",
                   "Las 12 fases de la primera visita, minuto a minuto."),
    "otros.html": ("Otros documentos del sistema", "Documento troncal",
                   "Los 14 documentos de apoyo, del compendio maestro a la continuidad legal."),
}


def limpio(s):
    s = re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", s))).strip()
    s = re.sub(r"\s+([:;,.!?%»)\]])", r"\1", s)
    return re.sub(r"([«(\[¿¡])\s+", r"\1", s)


def cifras(portada):
    """Las cifras de la ficha de la portada, tal y como las declara el documento."""
    fuera = []
    for m in re.finditer(r'<div class="spec">\s*<dt>(.*?)</dt>\s*<dd>(.*?)</dd>',
                         portada, re.S):
        rotulo = limpio(m.group(1))
        cuerpo = m.group(2)
        chico = re.search(r"<small>(.*?)</small>", cuerpo, re.S)
        valor = limpio(re.sub(r"<small>.*?</small>", "", cuerpo, flags=re.S))
        fuera.append((valor, rotulo, limpio(chico.group(1)) if chico else ""))
    return fuera


def apartados(html):
    """(ancla, número, rótulo, grupo) de cada apartado, en orden de documento."""
    return [(m.group(1), m.group(2), H.unescape(m.group(3)), H.unescape(m.group(4)))
            for m in re.finditer(
                r'<article class="ap" data-ap="([^"]*)" data-n="([^"]*)" '
                r'data-rotulo="([^"]*)" data-grupo="([^"]*)"', html)]


def cuenta_dentro(html, ancla):
    """Cuántos titulares vive dentro de un apartado. Es su peso, y se dice."""
    m = re.search(r'<article class="ap" data-ap="%s"[^>]*>' % re.escape(ancla), html)
    if not m:
        return 0
    fin = html.find('</article><!--/ap-->', m.end())
    return len(re.findall(r"<h[23][^>]*>", html[m.end():fin if fin > 0 else None]))


def tarjeta(grupo, filas, html, ancla_grupo):
    puntos = []
    for ancla, numero, rotulo, _ in filas:
        if ancla == ancla_grupo:
            continue          # el título de la tarjeta ya es esa parte
        n = cuenta_dentro(html, ancla)
        puntos.append(
            '<a class="tb__e" href="#%s">'
            '<b class="tb__n">%s</b>'
            '<span class="tb__r">%s</span>'
            '<span class="tb__c">%s</span>'
            '</a>'
            % (ancla, numero or "·", H.escape(rotulo),
               ("%d" % n) if n else ""))
    cabeza = H.escape(grupo) or "Contenido"
    if ancla_grupo:
        cabeza = '<a href="#%s">%s</a>' % (ancla_grupo, cabeza)
    return ('<section class="tb__g">'
            '<header class="tb__gh"><h3>%s</h3><span>%d</span></header>'
            '<div class="tb__l">%s</div>'
            '</section>'
            % (cabeza, len(puntos), "".join(puntos)))


def dibuja(html, archivo):
    aps = [a for a in apartados(html) if a[0] != "portada-doc"]
    if not aps:
        return None

    m = re.search(r'<article class="ap" data-ap="portada-doc"[^>]*>(.*?)</article><!--/ap-->',
                  html, re.S)
    portada = m.group(1) if m else ""

    del_grupo = {g: a for g, a, _ in menu.MENUS[archivo]["grupos"] if a}

    tarjetas = []
    orden = []
    for _, _, _, grupo in aps:
        if grupo not in orden:
            orden.append(grupo)
    for grupo in orden:
        tarjetas.append(tarjeta(grupo, [a for a in aps if a[3] == grupo], html,
                                del_grupo.get(grupo)))

    datos = cifras(portada)
    fila = ""
    if datos:
        fila = ('<div class="tb__cifras">%s</div>'
                % "".join('<div class="tb__d"><b>%s</b><span>%s</span>%s</div>'
                          % (H.escape(v), H.escape(r),
                             '<small>%s</small>' % H.escape(c) if c else "")
                          for v, r, c in datos))

    ficha = FICHAS.get(archivo, ("", ""))
    return ('\n<div class="wrap">\n'
            '  <nav class="tb" aria-label="Tablero del documento">\n'
            '    <header class="tb__cab">\n'
            '      <p class="tb__k">%s</p>\n'
            '      <h1 class="tb__t">%s</h1>\n'
            '      <p class="tb__q">%s</p>\n'
            '    </header>\n'
            '    %s\n'
            '    <div class="tb__rejilla">%s</div>\n'
            '    <p class="tb__pie">Pulse cualquier apartado para abrirlo. '
            'El documento entero, seguido, está debajo de este tablero.</p>\n'
            '  </nav>\n'
            '</div>\n' % (H.escape(ficha[1]), H.escape(ficha[0]),
                          H.escape(ficha[2] if len(ficha) > 2 else ""),
                          fila, "".join(tarjetas)))


def quita(html):
    return re.sub(r'\n<div class="wrap">\n  <nav class="tb".*?</nav>\n</div>\n',
                  "\n", html, flags=re.S)


def main():
    total = 0
    for archivo in menu.MENUS:
        ruta = RAIZ / archivo
        html = quita(ruta.read_text(encoding="utf-8"))
        pieza = dibuja(html, archivo)
        if pieza:
            m = re.search(r'(<article class="ap" data-ap="portada-doc"[^>]*>)', html)
            if m:
                html = html[:m.end()] + pieza + html[m.end():]
                total += 1
                print("  %-28s tablero con %d grupos"
                      % (archivo, pieza.count('class="tb__g"')))
            else:
                print("  %-28s sin portada donde ponerlo" % archivo)
        else:
            print("  %-28s entero, sin tablero" % archivo)
        ruta.write_text(html, encoding="utf-8")
    print("tableros: %d" % total)
    return 0


if __name__ == "__main__":
    sys.exit(main())
