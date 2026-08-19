#!/usr/bin/env python3
"""Exporta los documentos a HTML autónomos, con las tipografías incrustadas.

Genera en export/ una copia de cada página que funciona sin conexión: descarga
las fuentes de Google Fonts, las incrusta como data URI y reescribe los enlaces
cruzados a los nombres de archivo exportados.

    python3 build-export.py

Requiere conexión solo durante la exportación. El resultado no depende de nada
externo: ni fuentes, ni scripts, ni imágenes.
"""
import base64
import pathlib
import re
import urllib.request

RAIZ = pathlib.Path(__file__).parent
DESTINO = RAIZ / "export"

# Los archivos a exportar y el nombre con el que se guardan
PAGINAS = {
    "manual.html": "Manual-Maestro-Giraldo-v4.html",
    "index.html": "Protocolo-Primera-Visita-Giraldo.html",
}

# Solo se incrustan estos subconjuntos: el resto (cirílico, vietnamita) no se usa
SUBCONJUNTOS = ("latin", "latin-ext")

# Navegador moderno, para que Google Fonts devuelva woff2
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

ENLACES_FUENTES = re.compile(
    r'<link rel="preconnect"[^>]*>\s*<link rel="preconnect"[^>]*>\s*'
    r'<link rel="stylesheet" href="(https://fonts\.googleapis\.com[^"]*)">',
    re.S,
)


def descargar(url):
    peticion = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(peticion) as respuesta:
        return respuesta.read()


def fuentes_incrustadas(url_css):
    """Devuelve un <style> con las @font-face de los subconjuntos latinos."""
    css = descargar(url_css).decode("utf-8")
    bloques = re.findall(r"/\*\s*([a-z\-]+)\s*\*/\s*(@font-face\s*\{.*?\})", css, re.S)
    incrustados, peso = [], 0
    for subconjunto, bloque in bloques:
        if subconjunto not in SUBCONJUNTOS:
            continue
        encontrada = re.search(r"url\((https://[^)]+\.woff2)\)", bloque)
        if not encontrada:
            continue
        datos = descargar(encontrada.group(1))
        peso += len(datos)
        b64 = base64.b64encode(datos).decode()
        incrustados.append(
            bloque.replace(encontrada.group(1), "data:font/woff2;base64," + b64)
        )
    print(f"  {len(incrustados)} tipografías incrustadas · {peso // 1024} KB")
    return (
        "<style>\n/* Tipografías incrustadas (subconjuntos latin y latin-ext) "
        "para uso sin conexión */\n" + "\n".join(incrustados) + "\n</style>"
    )


def main():
    DESTINO.mkdir(exist_ok=True)
    estilo = None
    for origen, salida in PAGINAS.items():
        print(origen)
        html = (RAIZ / origen).read_text(encoding="utf-8")
        coincidencia = ENLACES_FUENTES.search(html)
        if not coincidencia:
            raise SystemExit(f"No se encontró el enlace a Google Fonts en {origen}")
        if estilo is None:                      # las dos páginas usan las mismas fuentes
            estilo = fuentes_incrustadas(coincidencia.group(1))
        html = ENLACES_FUENTES.sub(lambda _: estilo, html, count=1)
        for otro_origen, otra_salida in PAGINAS.items():
            html = html.replace(f'href="{otro_origen}"', f'href="{otra_salida}"')
        (DESTINO / salida).write_text(html, encoding="utf-8")
        print(f"  → export/{salida} · {(DESTINO / salida).stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
