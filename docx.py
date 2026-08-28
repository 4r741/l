#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Escribe documentos de Word sin depender de nada.

Un .docx es un zip con unos cuantos XML dentro, y en esta máquina no hay ni
pandoc ni las bibliotecas de Python que suelen usarse para escribirlos —y el
importador de HTML de LibreOffice no arranca—. Así que se escribe el formato
directamente, que además deja controlar lo único que de verdad importa aquí:
que los titulares lleven su nivel de esquema, para que el panel de navegación de
Word recorra el documento y la tabla de contenido se genere sola.

Se usa así:

    doc = Documento()
    doc.titular(1, [Trozo("Tesis de Dirección")])
    doc.parrafo([Trozo("Texto normal y "), Trozo("negrita", negrita=True)])
    doc.tabla([[celdas...], ...], cabecera=True)
    doc.guarda("salida.docx")
"""
import zipfile
from xml.sax.saxutils import escape

NS = ('xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
      'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"')


class Trozo:
    """Un fragmento de texto con su forma."""

    def __init__(self, texto, negrita=False, cursiva=False, mono=False, apagado=False):
        self.texto = texto
        self.negrita = negrita
        self.cursiva = cursiva
        self.mono = mono
        self.apagado = apagado

    def xml(self):
        f = []
        if self.negrita:
            f.append("<w:b/>")
        if self.cursiva:
            f.append("<w:i/>")
        if self.mono:
            f.append('<w:rFonts w:ascii="Consolas" w:hAnsi="Consolas"/>')
        if self.apagado:
            f.append('<w:color w:val="6B7873"/>')
        props = "<w:rPr>%s</w:rPr>" % "".join(f) if f else ""
        # xml:space para que no se coman los espacios de los extremos
        return ('<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r>'
                % (props, escape(self.texto)))


def _runs(trozos):
    return "".join(t.xml() for t in trozos if t.texto)


class Documento:
    def __init__(self, titulo="", autor="", asunto=""):
        self.cuerpo = []
        self.imagenes = []
        self.titulo, self.autor, self.asunto = titulo, autor, asunto

    # ---------------------------------------------------------------- bloques
    def parrafo(self, trozos, estilo=None, espacio=True):
        p = []
        if estilo:
            p.append('<w:pStyle w:val="%s"/>' % estilo)
        if not espacio:
            p.append('<w:spacing w:after="0"/>')
        props = "<w:pPr>%s</w:pPr>" % "".join(p) if p else ""
        self.cuerpo.append("<w:p>%s%s</w:p>" % (props, _runs(trozos)))

    def titular(self, nivel, trozos):
        self.cuerpo.append('<w:p><w:pPr><w:pStyle w:val="Titular%d"/></w:pPr>%s</w:p>'
                           % (min(nivel, 5), _runs(trozos)))

    def punto(self, trozos, ordenada=False, nivel=0):
        num = 2 if ordenada else 1
        self.cuerpo.append(
            '<w:p><w:pPr><w:pStyle w:val="Lista"/><w:numPr>'
            '<w:ilvl w:val="%d"/><w:numId w:val="%d"/></w:numPr></w:pPr>%s</w:p>'
            % (min(nivel, 2), num, _runs(trozos)))

    def cita(self, trozos):
        self.parrafo(trozos, estilo="Cita")

    def salto(self):
        self.cuerpo.append('<w:p><w:r><w:br w:type="page"/></w:r></w:p>')

    def indice(self):
        """El campo de tabla de contenido. Word lo rellena al abrir el archivo."""
        self.cuerpo.append(
            '<w:p><w:r><w:fldChar w:fldCharType="begin" w:dirty="true"/></w:r>'
            '<w:r><w:instrText xml:space="preserve"> TOC \\o "1-3" \\h \\z \\u </w:instrText></w:r>'
            '<w:r><w:fldChar w:fldCharType="separate"/></w:r>'
            '<w:r><w:t>Actualice el índice: pulse aquí y luego F9.</w:t></w:r>'
            '<w:r><w:fldChar w:fldCharType="end"/></w:r></w:p>')

    def imagen(self, datos, ancho_px, alto_px, rotulo="", ancho_max=9360):
        """Incrusta un PNG. Las medidas van en EMU: 914.400 por pulgada.

        Lo que no puede transcribirse a texto —una figura— se incrusta como
        imagen, que es la única manera de que viaje. Se escala para que quepa en
        la caja de escritura sin deformarse.
        """
        idx = len(self.imagenes) + 1
        self.imagenes.append(datos)
        # 9360 dxa de caja: 1 dxa = 635 EMU
        ancho = min(int(ancho_px * 9525), int(ancho_max * 635))
        alto = int(ancho * alto_px / max(1, ancho_px))
        self.cuerpo.append(
            '<w:p><w:pPr><w:spacing w:before="120" w:after="60"/>'
            '<w:jc w:val="center"/></w:pPr><w:r><w:drawing>'
            '<wp:inline distT="0" distB="0" distL="0" distR="0" '
            'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing">'
            '<wp:extent cx="%d" cy="%d"/><wp:docPr id="%d" name="Figura %d" descr="%s"/>'
            '<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
            '<a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
            '<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">'
            '<pic:nvPicPr><pic:cNvPr id="%d" name="figura%d.png"/><pic:cNvPicPr/></pic:nvPicPr>'
            '<pic:blipFill><a:blip r:embed="rIdImg%d"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
            '<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="%d" cy="%d"/></a:xfrm>'
            '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>'
            '</pic:pic></a:graphicData></a:graphic></wp:inline>'
            '</w:drawing></w:r></w:p>'
            % (ancho, alto, idx, idx, escape(rotulo)[:400], idx, idx, idx, ancho, alto))

    def pie(self, trozos):
        self.parrafo(trozos, estilo="Pie")

    def tabla(self, filas, anchos=None, cabecera=True):
        """filas = lista de listas de listas de Trozo."""
        if not filas:
            return
        n = max(len(f) for f in filas)
        anchos = anchos or [int(9360 / n)] * n
        rejilla = "".join('<w:gridCol w:w="%d"/>' % a for a in anchos)
        out = ['<w:tbl><w:tblPr><w:tblStyle w:val="Rejilla"/>'
               '<w:tblW w:w="9360" w:type="dxa"/><w:tblLayout w:type="fixed"/>'
               '</w:tblPr><w:tblGrid>%s</w:tblGrid>' % rejilla]
        for i, fila in enumerate(filas):
            encabeza = cabecera and i == 0
            celdas = []
            for j in range(n):
                trozos = fila[j] if j < len(fila) else []
                sombra = ('<w:shd w:val="clear" w:color="auto" w:fill="E9E8E1"/>'
                          if encabeza else "")
                estilo = "CeldaCab" if encabeza else "Celda"
                celdas.append(
                    '<w:tc><w:tcPr><w:tcW w:w="%d" w:type="dxa"/>%s</w:tcPr>'
                    '<w:p><w:pPr><w:pStyle w:val="%s"/></w:pPr>%s</w:p></w:tc>'
                    % (anchos[j], sombra, estilo, _runs(trozos)))
            # El orden de los hijos de trPr lo fija el esquema: cantSplit antes
            # que tblHeader. Al revés, Word se queja del archivo al abrirlo.
            props = ('<w:trPr><w:cantSplit/><w:tblHeader/></w:trPr>' if encabeza
                     else '<w:trPr><w:cantSplit/></w:trPr>')
            out.append("<w:tr>%s%s</w:tr>" % (props, "".join(celdas)))
        out.append("</w:tbl>")
        # un párrafo vacío detrás: dos tablas seguidas se funden en una
        out.append('<w:p><w:pPr><w:spacing w:after="120"/></w:pPr></w:p>')
        self.cuerpo.append("".join(out))

    # ---------------------------------------------------------------- guardar
    def guarda(self, ruta):
        piezas = {
            "[Content_Types].xml": TIPOS,
            "_rels/.rels": RELS,
            "word/_rels/document.xml.rels": RELS_DOC,
            "word/styles.xml": ESTILOS,
            "word/numbering.xml": NUMERACION,
            "word/settings.xml": AJUSTES,
            "docProps/core.xml": NUCLEO % (escape(self.titulo), escape(self.asunto),
                                           escape(self.autor), escape(self.autor)),
            "docProps/app.xml": APP,
            "word/document.xml": (
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                '<w:document %s><w:body>%s'
                '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/>'
                '<w:pgMar w:top="1134" w:bottom="1134" w:left="1191" w:right="1191" '
                'w:header="709" w:footer="709" w:gutter="0"/></w:sectPr>'
                '</w:body></w:document>' % (NS, "".join(self.cuerpo))),
        }
        if self.imagenes:
            extra = "".join(
                '<Relationship Id="rIdImg%d" Type="http://schemas.openxmlformats.org/'
                'officeDocument/2006/relationships/image" Target="media/figura%d.png"/>'
                % (i + 1, i + 1) for i in range(len(self.imagenes)))
            piezas["word/_rels/document.xml.rels"] = piezas[
                "word/_rels/document.xml.rels"].replace("</Relationships>", extra + "</Relationships>")
            piezas["[Content_Types].xml"] = piezas["[Content_Types].xml"].replace(
                "</Types>", '<Default Extension="png" ContentType="image/png"/></Types>')

        with zipfile.ZipFile(ruta, "w", zipfile.ZIP_DEFLATED) as z:
            for i, datos in enumerate(self.imagenes):
                info = zipfile.ZipInfo("word/media/figura%d.png" % (i + 1),
                                       date_time=(2026, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(info, datos)
            for nombre, texto in piezas.items():
                # fecha fija: construir dos veces tiene que dar el mismo archivo
                info = zipfile.ZipInfo(nombre, date_time=(2026, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                z.writestr(info, texto)


# --------------------------------------------------------------------- piezas
TIPOS = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
<Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>
<Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>
<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>'''

RELS = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>'''

RELS_DOC = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/>
<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>
</Relationships>'''

# updateFields hace que Word ofrezca rellenar el índice al abrir el archivo
AJUSTES = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:settings %s><w:updateFields w:val="true"/></w:settings>''' % NS

NUCLEO = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
 xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/"
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<dc:title>%s</dc:title><dc:subject>%s</dc:subject><dc:creator>%s</dc:creator>
<cp:lastModifiedBy>%s</cp:lastModifiedBy>
<dcterms:created xsi:type="dcterms:W3CDTF">2026-01-01T00:00:00Z</dcterms:created>
<dcterms:modified xsi:type="dcterms:W3CDTF">2026-01-01T00:00:00Z</dcterms:modified>
</cp:coreProperties>'''

APP = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties">
<Application>Sistema documental Giraldo</Application></Properties>'''

def _titular(n, tam, color, antes, despues, negrita):
    return ('<w:style w:type="paragraph" w:styleId="Titular%d">'
            '<w:name w:val="heading %d"/><w:basedOn w:val="Normal"/>'
            '<w:next w:val="Normal"/><w:qFormat/>'
            '<w:pPr><w:keepNext/><w:keepLines/>'
            '<w:spacing w:before="%d" w:after="%d"/><w:outlineLvl w:val="%d"/></w:pPr>'
            '<w:rPr><w:rFonts w:ascii="Georgia" w:hAnsi="Georgia"/>%s'
            '<w:color w:val="%s"/><w:sz w:val="%d"/></w:rPr></w:style>'
            % (n, n, antes, despues, n - 1, "<w:b/>" if negrita else "", color, tam))

ESTILOS = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
 '<w:styles %s>'
 '<w:docDefaults><w:rPrDefault><w:rPr>'
 '<w:rFonts w:ascii="Georgia" w:hAnsi="Georgia"/><w:sz w:val="21"/><w:lang w:val="es-ES"/>'
 '</w:rPr></w:rPrDefault><w:pPrDefault><w:pPr>'
 '<w:spacing w:after="140" w:line="276" w:lineRule="auto"/></w:pPr></w:pPrDefault></w:docDefaults>'
 '<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/>'
 '<w:qFormat/></w:style>'
 + _titular(1, 48, "141F1D", 0, 200, False)
 + _titular(2, 32, "0A554F", 360, 120, False)
 + _titular(3, 25, "141F1D", 280, 100, True)
 + _titular(4, 22, "3A4A46", 220, 80, True)
 + _titular(5, 21, "3A4A46", 200, 60, True)
 + '<w:style w:type="paragraph" w:styleId="Lista"><w:name w:val="List Paragraph"/>'
   '<w:basedOn w:val="Normal"/><w:qFormat/>'
   '<w:pPr><w:spacing w:after="60"/><w:ind w:left="425"/></w:pPr></w:style>'
 + '<w:style w:type="paragraph" w:styleId="Cita"><w:name w:val="Quote"/>'
   '<w:basedOn w:val="Normal"/><w:qFormat/>'
   '<w:pPr><w:spacing w:before="160" w:after="160"/><w:ind w:left="425"/></w:pPr>'
   '<w:rPr><w:i/><w:color w:val="3A4A46"/></w:rPr></w:style>'
 + '<w:style w:type="paragraph" w:styleId="Sumario"><w:basedOn w:val="Normal"/>'
   '<w:pPr><w:spacing w:after="200"/></w:pPr>'
   '<w:rPr><w:color w:val="6B7873"/><w:sz w:val="20"/></w:rPr></w:style>'
 + '<w:style w:type="paragraph" w:styleId="Pie"><w:basedOn w:val="Normal"/>'
   '<w:pPr><w:jc w:val="center"/><w:spacing w:after="220"/></w:pPr>'
   '<w:rPr><w:color w:val="6B7873"/><w:sz w:val="18"/></w:rPr></w:style>'
 + '<w:style w:type="paragraph" w:styleId="Celda"><w:basedOn w:val="Normal"/>'
   '<w:pPr><w:spacing w:after="0" w:line="240" w:lineRule="auto"/></w:pPr>'
   '<w:rPr><w:sz w:val="18"/></w:rPr></w:style>'
 + '<w:style w:type="paragraph" w:styleId="CeldaCab"><w:basedOn w:val="Celda"/>'
   '<w:rPr><w:b/><w:sz w:val="18"/></w:rPr></w:style>'
 + '<w:style w:type="table" w:styleId="Rejilla"><w:name w:val="Table Grid"/>'
   '<w:tblPr><w:tblBorders>'
   '<w:top w:val="single" w:sz="4" w:color="D5D9D3"/>'
   '<w:left w:val="single" w:sz="4" w:color="D5D9D3"/>'
   '<w:bottom w:val="single" w:sz="4" w:color="D5D9D3"/>'
   '<w:right w:val="single" w:sz="4" w:color="D5D9D3"/>'
   '<w:insideH w:val="single" w:sz="4" w:color="D5D9D3"/>'
   '<w:insideV w:val="single" w:sz="4" w:color="D5D9D3"/>'
   '</w:tblBorders><w:tblCellMar>'
   '<w:top w:w="60" w:type="dxa"/><w:left w:w="90" w:type="dxa"/>'
   '<w:bottom w:w="60" w:type="dxa"/><w:right w:w="90" w:type="dxa"/>'
   '</w:tblCellMar></w:tblPr></w:style>'
 '</w:styles>') % NS

def _nivel(i, fmt, texto, sangria):
    return ('<w:lvl w:ilvl="%d"><w:start w:val="1"/><w:numFmt w:val="%s"/>'
            '<w:lvlText w:val="%s"/><w:lvlJc w:val="left"/>'
            '<w:pPr><w:ind w:left="%d" w:hanging="283"/></w:pPr>'
            '<w:rPr><w:rFonts w:ascii="Symbol" w:hAnsi="Symbol" w:hint="default"/></w:rPr>'
            '</w:lvl>' % (i, fmt, texto, sangria))

# Los «%1.» de la numeración son literales del formato de Word y chocan con el
# formateo de Python: aquí se sustituye por marca y no por porcentaje.
NUMERACION = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
 '<w:numbering @NS@>'
 '<w:abstractNum w:abstractNumId="1"><w:multiLevelType w:val="hybridMultilevel"/>'
 + _nivel(0, "bullet", "", 425)
 + _nivel(1, "bullet", "", 850)
 + _nivel(2, "bullet", "", 1275)
 + '</w:abstractNum>'
 '<w:abstractNum w:abstractNumId="2"><w:multiLevelType w:val="hybridMultilevel"/>'
 '<w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="decimal"/>'
 '<w:lvlText w:val="%1."/><w:lvlJc w:val="left"/>'
 '<w:pPr><w:ind w:left="425" w:hanging="283"/></w:pPr></w:lvl>'
 '<w:lvl w:ilvl="1"><w:start w:val="1"/><w:numFmt w:val="lowerLetter"/>'
 '<w:lvlText w:val="%2."/><w:lvlJc w:val="left"/>'
 '<w:pPr><w:ind w:left="850" w:hanging="283"/></w:pPr></w:lvl>'
 '<w:lvl w:ilvl="2"><w:start w:val="1"/><w:numFmt w:val="lowerRoman"/>'
 '<w:lvlText w:val="%3."/><w:lvlJc w:val="left"/>'
 '<w:pPr><w:ind w:left="1275" w:hanging="283"/></w:pPr></w:lvl>'
 '</w:abstractNum>'
 '<w:num w:numId="1"><w:abstractNumId w:val="1"/></w:num>'
 '<w:num w:numId="2"><w:abstractNumId w:val="2"/></w:num>'
 '</w:numbering>').replace("@NS@", NS)
