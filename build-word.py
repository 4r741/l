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
    ("memoria.html", "Plan de Dirección",
     "Qué creemos, qué apostamos y las quince decisiones que se someten a la Junta."),
    ("marketing.html", "Plan Maestro de Marketing",
     "Setenta y seis acciones sobre los doce estados del paciente, con dueño, coste y semáforo legal."),
    ("manual.html", "Manual Maestro de Operaciones",
     "Las catorce fases del recorrido del paciente, los seis puestos y la puesta en marcha."),
    ("protocolos.html", "Protocolos por puesto",
     "El protocolo del centro visto desde cada uno de los seis puestos, con su papel "
     "en las catorce fases y sus procedimientos."),
    ("index.html", "Protocolo de Primera Visita",
     "Las doce fases de la primera visita, minuto a minuto."),
    ("otros.html", "Otros documentos del sistema",
     "Los catorce documentos de apoyo, del compendio maestro al programa de cuidado."),
    ("instrumentos/captura.html", "Los números del centro",
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

    def __init__(self, archivo=""):
        super().__init__(convert_charrefs=True)
        self.archivo = archivo     # de qué documento salen las anclas de aquí
        self.pendientes = []       # identificadores vistos aún sin bloque al que pegarse
        self.enlaces = []          # pila de destinos: un <a> puede envolver a otro
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
            self.bloques.append((self.tipo, trozos, tuple(self.pendientes)))
            self.pendientes = []
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

        d = dict(attrs)
        # Todo identificador que se cruza queda esperando al siguiente bloque:
        # es donde el lector espera aterrizar cuando alguien lo enlaza.
        for clave in ("id", "data-ap"):
            valor = (d.get(clave) or "").strip()
            if valor and valor not in self.pendientes:
                self.pendientes.append(valor)
        if etiqueta == "a":
            self.enlaces.append(destino_de(d.get("href", ""), self.archivo))

        if etiqueta == "svg":
            self._cierra()
            self.bloques.append(("figura", None, ()))
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
        if etiqueta == "a" and self.enlaces:
            self.enlaces.pop()
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
                self.bloques.append(("tabla", self.tabla, tuple(self.pendientes)))
                self.pendientes = []
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
        salta = next((x for x in reversed(self.enlaces) if x), None)
        trozo = Trozo(re.sub(r"\s+", " ", datos),
                      negrita=bool(self.negrita), cursiva=bool(self.cursiva),
                      mono=bool(self.mono), destino=salta)
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


def destino_de(href, archivo):
    """De un href del sistema a la pareja (documento, ancla), o None.

    En la web, «véase la Fase 14» es un enlace; al pasar a Word era texto plano
    y el lector tenía que buscar a mano en seiscientas páginas. Aquí se traduce:
    un «#m14» apunta al mismo documento, un «manual.html#m14» al Manual, y un
    «manual.html» a secas al principio del Manual.
    """
    href = (href or "").strip()
    if not href or href.startswith(("http:", "https:", "mailto:", "tel:", "javascript:")):
        return None
    if href.startswith("#"):
        return (archivo, href[1:]) if len(href) > 1 else None
    camino, _, ancla = href.partition("#")
    if not camino.endswith(".html"):
        return None
    return (camino.rsplit("/", 1)[-1], ancla)


def nombre_marca(clave, registro):
    """Un nombre de marcador que Word admita, estable y sin colisiones.

    Word solo acepta letras, dígitos y subrayado, hasta cuarenta caracteres y
    empezando por letra; las anclas del sistema llevan guiones y algunas pasan
    de cuarenta. Se normaliza y se numera si dos distintas caen en el mismo
    nombre, para que ningún enlace acabe en el apartado de otro.
    """
    if clave in registro:
        return registro[clave]
    archivo, ancla = clave
    crudo = "%s_%s" % (archivo.replace(".html", ""), ancla or "inicio")
    limpio = re.sub(r"[^A-Za-z0-9]", "_", crudo).strip("_") or "ancla"
    if not limpio[0].isalpha():
        limpio = "a" + limpio
    limpio = limpio[:36]
    usados = set(registro.values())
    nombre, n = limpio, 1
    while nombre in usados:
        n += 1
        nombre = "%s_%d" % (limpio[:32], n)
    registro[clave] = nombre
    return nombre


def bloques_de(ruta):
    t = (RAIZ / ruta).read_text(encoding="utf-8")
    m = re.search(r"<main\b[^>]*>(.*?)</main>", t, re.S)
    if not m:
        sys.exit("  %s no tiene <main>" % ruta)
    b = Bloques(archivo=ruta.rsplit("/", 1)[-1])
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

    # Se lee todo antes de escribir nada: un enlace del Plan de Dirección apunta
    # al Manual, que se escribe después, y hasta no haber recorrido las siete
    # partes no se sabe qué anclas existen de verdad. Prometer un salto a algo
    # que no está en el archivo es peor que no prometerlo.
    partido = [(ruta, titulo, que, bloques_de(ruta)) for ruta, titulo, que in PARTES]
    registro, disponibles = {}, set()
    for ruta, titulo, _q, bloques in partido:
        hoja = ruta.rsplit("/", 1)[-1]
        disponibles.add((hoja, ""))            # el documento entero, por su titular
        for _tipo, _dato, anclas in bloques:
            for ancla in anclas:
                disponibles.add((hoja, ancla))
    for clave in sorted(disponibles):
        nombre_marca(clave, registro)

    def marcas(hoja, anclas):
        return [registro[(hoja, a)] for a in anclas if (hoja, a) in registro]

    prometidos = perdidos = 0

    def resuelve(trozos):
        """Cambia la pareja (documento, ancla) por el marcador que le toca."""
        nonlocal prometidos, perdidos
        for t in trozos:
            if not t.destino:
                continue
            nombre = registro.get(t.destino)
            if nombre:
                t.destino = nombre
                prometidos += 1
            else:
                t.destino = None       # antes que llevar a ninguna parte, texto
                perdidos += 1
        return trozos

    cuenta = {"h": 0, "p": 0, "li": 0, "tabla": 0, "figura": 0}
    for ruta, titulo, que, bloques in partido:
        hoja = ruta.rsplit("/", 1)[-1]
        doc.salto()
        doc.titular(1, [Trozo(titulo)], anclas=marcas(hoja, [""]))
        doc.parrafo([Trozo(que)], estilo="Sumario")
        figuras, siguiente = censo.get(ruta, []), 0
        for tipo, dato, anclas in bloques:
            puestas = marcas(hoja, anclas)
            if tipo == "figura":
                if siguiente < len(figuras):
                    f = figuras[siguiente]; siguiente += 1
                    doc.imagen((carpeta / f["archivo"]).read_bytes(),
                               f["ancho"], f["alto"], f.get("rotulo", ""))
                    cuenta["figura"] += 1
                continue
            if tipo == "pie":
                doc.pie(resuelve(dato))
                continue
            if tipo == "tabla":
                for fila in dato:
                    for celda in fila:
                        resuelve(celda)
                if puestas:
                    doc.parrafo([], espacio=False, anclas=puestas)
                doc.tabla(dato, anchos=anchos(dato))
                cuenta["tabla"] += 1
            elif tipo.startswith("h"):
                doc.titular(int(tipo[1]), resuelve(dato), anclas=puestas)
                cuenta["h"] += 1
            elif tipo == "li":
                doc.punto(resuelve(dato), anclas=puestas)
                cuenta["li"] += 1
            elif tipo == "cita":
                doc.cita(resuelve(dato))
                cuenta["p"] += 1
            else:
                doc.parrafo(resuelve(dato), anclas=puestas)
                cuenta["p"] += 1

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    doc.guarda(SALIDA)
    print("  → export/%s · %d KB · %d titulares · %d párrafos · %d puntos · "
          "%d tablas · %d figuras"
          % (SALIDA.name, SALIDA.stat().st_size // 1024,
             cuenta["h"], cuenta["p"], cuenta["li"], cuenta["tabla"], cuenta["figura"]))
    print("     %d marcadores · %d saltos internos · %d referencias que el Word no "
          "puede resolver y quedan en texto" % (len(registro), prometidos, perdidos))


if __name__ == "__main__":
    main()
