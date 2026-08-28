#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Arma el sistema documental entero en un solo .docx, editable en Word.

    python3 build-word.py

El HTML y el PDF son para leer; el .docx es para trabajar encima: mandarlo a
asesoría, comentar un apartado, llevarse una tabla a un acta. Se construye desde
los mismos documentos, de modo que lo que dice el Word es exactamente lo que
dice el sistema.

Viaja el contenido: texto, titulares —con su nivel de esquema, para que el panel
de navegación de Word recorra el documento y el índice se genere solo—, tablas y
listas. No viaja la maquinaria de la pantalla —barras, mapas, botones,
buscadores—, que en un procesador de textos no significa nada.
"""
import json
import pathlib
import re
import sys
from html.parser import HTMLParser

from docx import Documento, Trozo

RAIZ = pathlib.Path(__file__).parent

_v = {}
exec(compile((RAIZ / "version.py").read_text(encoding="utf-8"), "version.py", "exec"), _v)
VERSION, FECHA = _v["VERSION"], _v["FECHA"]

SALIDA = RAIZ / "export" / ("Sistema-Documental-Giraldo-v%s.docx" % VERSION)

PARTES = [
    ("memoria.html", "Tesis de Dirección",
     "Qué creemos, qué apostamos y las quince decisiones que se someten a la Junta."),
    ("marketing.html", "Plan Maestro de Marketing",
     "Setenta y seis acciones sobre los doce estados del paciente, con dueño, coste y semáforo legal."),
    ("manual.html", "Manual Maestro de Operaciones",
     "Las catorce fases del recorrido del paciente, los seis puestos y la puesta en marcha."),
    ("index.html", "Protocolo de Primera Visita",
     "Las doce fases de la primera visita, minuto a minuto."),
    ("otros.html", "Otros documentos del sistema",
     "Los catorce documentos de apoyo, del compendio maestro al programa de cuidado."),
    ("instrumentos/captura.html", "Captura de la línea base",
     "Los diez indicadores y los cinco números, mes a mes."),
]

# El <svg> ya no se descarta: se anota por dónde pasaba, para poner ahí su
# imagen. Lo que no puede transcribirse a texto tiene que viajar igualmente.
FUERA_ETIQUETA = {"script", "style", "button", "input", "select", "textarea",
                  "nav", "header", "footer", "form", "noscript"}
FUERA_CLASE = ("strip", "ticks", "mapa", "volver", "saltar", "avance", "topbar",
               "cabecera", "hud", "idx__mando", "paleta", "cap__barra",
               "edit", "puerta__flecha")


class Bloques(HTMLParser):
    """Reduce un documento a la lista de bloques que un Word sabe representar."""

    NEGRITA = {"strong", "b", "th"}
    CURSIVA = {"em", "i", "cite", "blockquote"}
    MONO = {"code", "kbd", "samp"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.bloques = []
        self.saltando = 0
        self.acumula = None        # trozos del bloque en curso
        self.tipo = None
        self.negrita = self.cursiva = self.mono = 0
        self.listas = []           # pila de (ordenada,)
        self.tabla = None          # filas en construcción
        self.fila = None
        self.celda = None

    # ------------------------------------------------------------ utilidades
    def _descartable(self, etiqueta, attrs):
        if etiqueta in FUERA_ETIQUETA:
            return True
        d = dict(attrs)
        if d.get("hidden") is not None or d.get("aria-hidden") == "true":
            return True
        clases = d.get("class", "")
        return any(c in clases for c in FUERA_CLASE)

    def _cierra(self):
        if self.acumula is None:
            return
        trozos = [t for t in self.acumula if t.texto.strip()]
        if trozos:
            self.bloques.append((self.tipo, trozos))
        self.acumula, self.tipo = None, None

    def _abre(self, tipo):
        self._cierra()
        self.acumula, self.tipo = [], tipo

    # -------------------------------------------------------------- etiquetas
    def handle_starttag(self, etiqueta, attrs):
        if self.saltando:
            if etiqueta not in ("br", "img", "hr", "input", "meta"):
                self.saltando += 1
            return
        if self._descartable(etiqueta, attrs):
            self.saltando = 1
            return

        if etiqueta == "svg":
            self._cierra()
            self.bloques.append(("figura", None))
            self.saltando = 1          # el interior del svg no es texto
            return
        if etiqueta == "figcaption":
            self._abre("pie")
        elif etiqueta in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self._abre("h%d" % min(int(etiqueta[1]) + 1, 5))
        elif etiqueta in ("p", "dd"):
            self._abre("p")
        elif etiqueta == "dt":
            self._abre("h5")
        elif etiqueta == "blockquote":
            self._abre("cita")
        elif etiqueta in ("ul", "ol"):
            self._cierra()
            self.listas.append(etiqueta == "ol")
        elif etiqueta == "li":
            self._abre("li")
        elif etiqueta == "table":
            self._cierra()
            self.tabla, self.fila = [], None
        elif etiqueta == "tr" and self.tabla is not None:
            self.fila = []
        elif etiqueta in ("td", "th") and self.fila is not None:
            self.celda = []
        elif etiqueta == "br" and self.acumula is not None:
            self.acumula.append(Trozo(" "))

        if etiqueta in self.NEGRITA:
            self.negrita += 1
        if etiqueta in self.CURSIVA:
            self.cursiva += 1
        if etiqueta in self.MONO:
            self.mono += 1

    def handle_endtag(self, etiqueta):
        if self.saltando:
            self.saltando -= 1
            return
        if etiqueta in self.NEGRITA and self.negrita:
            self.negrita -= 1
        if etiqueta in self.CURSIVA and self.cursiva:
            self.cursiva -= 1
        if etiqueta in self.MONO and self.mono:
            self.mono -= 1

        if etiqueta in ("td", "th") and self.celda is not None and self.fila is not None:
            self.fila.append([t for t in self.celda if t.texto.strip()] or [Trozo("")])
            self.celda = None
        elif etiqueta == "tr" and self.fila is not None and self.tabla is not None:
            if any(any(t.texto.strip() for t in c) for c in self.fila):
                self.tabla.append(self.fila)
            self.fila = None
        elif etiqueta == "table" and self.tabla is not None:
            if self.tabla:
                self.bloques.append(("tabla", self.tabla))
            self.tabla, self.fila, self.celda = None, None, None
        elif etiqueta in ("ul", "ol"):
            self._cierra()
            if self.listas:
                self.listas.pop()
        elif etiqueta in ("h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "dt", "dd",
                          "blockquote", "figcaption"):
            self._cierra()

    def handle_data(self, datos):
        if self.saltando or not datos.strip():
            # los espacios entre etiquetas sí importan dentro de una frase
            if not self.saltando and datos and self.acumula is not None and datos != "\n":
                self.acumula.append(Trozo(" "))
            return
        trozo = Trozo(re.sub(r"\s+", " ", datos),
                      negrita=bool(self.negrita), cursiva=bool(self.cursiva),
                      mono=bool(self.mono))
        if self.celda is not None:
            self.celda.append(trozo)
        elif self.acumula is not None:
            self.acumula.append(trozo)
        elif self.fila is None and self.tabla is None:
            # texto suelto fuera de bloque: se le da uno
            self._abre("p")
            self.acumula.append(trozo)

    def cierra(self):
        self._cierra()
        return self.bloques


def bloques_de(ruta):
    t = (RAIZ / ruta).read_text(encoding="utf-8")
    m = re.search(r"<main\b[^>]*>(.*?)</main>", t, re.S)
    if not m:
        sys.exit("  %s no tiene <main>" % ruta)
    b = Bloques()
    b.feed(m.group(1))
    return b.cierra()


def anchos(filas):
    """Reparte los 9360 dxa según lo que ocupa cada columna, con un suelo."""
    n = max(len(f) for f in filas)
    peso = [0] * n
    for f in filas:
        for j in range(min(len(f), n)):
            peso[j] = max(peso[j], min(60, sum(len(t.texto) for t in f[j])))
    total = sum(peso) or n
    crudos = [max(700, int(9360 * p / total)) for p in peso]
    ajuste = 9360 / sum(crudos)
    salida = [int(a * ajuste) for a in crudos]
    salida[-1] += 9360 - sum(salida)         # que sumen exactamente el ancho
    return salida


def main():
    doc = Documento(
        titulo="Sistema documental · Centro de Excelencia Implantológica Giraldo",
        autor="Centro de Excelencia Implantológica Giraldo",
        asunto="Los siete documentos del sistema, versión %s" % VERSION)

    # ------------------------------------------------------------- cubierta
    doc.titular(1, [Trozo("Sistema documental")])
    doc.parrafo([Trozo("Centro de Excelencia Implantológica Giraldo", negrita=True)])
    doc.parrafo([Trozo("Rúa Bolivia nº 2 · Vigo (Pontevedra)")])
    doc.parrafo([Trozo("Versión %s · %s" % (VERSION, FECHA))])
    doc.parrafo([Trozo("Uso interno y confidencial. Contiene información económica, "
                       "laboral y estratégica. No se difunde fuera de la organización "
                       "sin autorización expresa de la Dirección General.")],
                estilo="Sumario")
    doc.titular(2, [Trozo("Qué hay dentro")])
    for _r, titulo, que in PARTES:
        doc.punto([Trozo(titulo + ". ", negrita=True), Trozo(que)], ordenada=True)
    doc.parrafo([Trozo("Los titulares llevan su nivel de esquema, de modo que el panel "
                       "de navegación de Word recorra el documento. El índice se rellena "
                       "solo al abrir el archivo; si no lo hace, pulse sobre él y F9.")],
                estilo="Sumario")
    doc.titular(2, [Trozo("Índice")])
    doc.indice()

    # -------------------------------------------------------------- las partes
    censo = {}
    carpeta = RAIZ / "export" / "figuras"
    ficha = carpeta / "censo.json"
    if ficha.exists():
        censo = json.loads(ficha.read_text(encoding="utf-8"))
    else:
        print("  aviso: sin figuras rasterizadas; ejecute antes python3 figuras-png.py")

    cuenta = {"h": 0, "p": 0, "li": 0, "tabla": 0, "figura": 0}
    for ruta, titulo, que in PARTES:
        doc.salto()
        doc.titular(1, [Trozo(titulo)])
        doc.parrafo([Trozo(que)], estilo="Sumario")
        figuras, siguiente = censo.get(ruta, []), 0
        for tipo, dato in bloques_de(ruta):
            if tipo == "figura":
                if siguiente < len(figuras):
                    f = figuras[siguiente]; siguiente += 1
                    doc.imagen((carpeta / f["archivo"]).read_bytes(),
                               f["ancho"], f["alto"], f.get("rotulo", ""))
                    cuenta["figura"] += 1
                continue
            if tipo == "pie":
                doc.pie(dato)
                continue
            if tipo == "tabla":
                doc.tabla(dato, anchos=anchos(dato))
                cuenta["tabla"] += 1
            elif tipo.startswith("h"):
                doc.titular(int(tipo[1]), dato)
                cuenta["h"] += 1
            elif tipo == "li":
                doc.punto(dato)
                cuenta["li"] += 1
            elif tipo == "cita":
                doc.cita(dato)
                cuenta["p"] += 1
            else:
                doc.parrafo(dato)
                cuenta["p"] += 1

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    doc.guarda(SALIDA)
    print("  → export/%s · %d KB · %d titulares · %d párrafos · %d puntos · "
          "%d tablas · %d figuras"
          % (SALIDA.name, SALIDA.stat().st_size // 1024,
             cuenta["h"], cuenta["p"], cuenta["li"], cuenta["tabla"], cuenta["figura"]))


if __name__ == "__main__":
    main()
