#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cambia el sistema de numeración de apartados: fuera el §.

    python3 renumera.py --ver     # dice qué cambiaría, sin tocar nada
    python3 renumera.py           # lo cambia

El signo § es correcto y es de otra época. Se sustituye por el número a secas,
a dos cifras cuando es de una —«03»—, que es como se numeran hoy los apartados
de un documento y como se leen de un vistazo en una barra.

La dificultad no es el reemplazo: es que el mismo signo hace dos trabajos.

  · Como rótulo —el titular de un apartado, su entrada en la barra de secciones,
    su línea en el índice— se convierte en el número: «§3» pasa a «03».
  · Como cita dentro de una frase —«declarado en su §18»— no puede quedarse en
    un número suelto, que no se lee: pasa a «declarado en su apartado 18».

Distinguir uno de otro es todo el trabajo de este guion.
"""
import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).parent

ARCHIVOS = (sorted(RAIZ.glob("fuentes/*.html"))
            + sorted(RAIZ.glob("generadores/*.py"))
            + [RAIZ / n for n in ("manual.html", "index.html", "otros.html",
                                  "build-inicio.py", "build-captura.py",
                                  "build-libro.py", "build-export.py",
                                  "catalogo-acciones.py", "modelo-campanas.py")])


def rotulo(n):
    """El número como rótulo: dos cifras si es entero de una."""
    return "%02d" % int(n) if re.fullmatch(r"\d", n) else n


def como_rotulo(texto):
    """Dentro de un rótulo, § desaparece y queda el número."""
    return re.sub(r"§(\d+(?:\.\d+)?)", lambda m: rotulo(m.group(1)), texto)


# En la frase, el número necesita su palabra delante. El orden importa: primero
# los casos con dos números, luego los que traen artículo, y al final el resto.
PROSA = [
    (r"§(\d+(?:\.\d+)?)\s+a\s+§(\d+(?:\.\d+)?)", r"apartados \1 a \2"),
    (r"§(\d+(?:\.\d+)?)\s+y\s+§(\d+(?:\.\d+)?)", r"apartados \1 y \2"),
    (r"\b([Dd]el)\s+§(\d+(?:\.\d+)?)", r"\1 apartado \2"),
    (r"\b([Aa]l)\s+§(\d+(?:\.\d+)?)", r"\1 apartado \2"),
    (r"\b([Ee]n)\s+el\s+§(\d+(?:\.\d+)?)", r"\1 el apartado \2"),
    (r"\b([Ee]n)\s+§(\d+(?:\.\d+)?)", r"\1 el apartado \2"),
    (r"\b([Ee]l|[Ss]u|[Ee]se|[Ee]ste)\s+§(\d+(?:\.\d+)?)", r"\1 apartado \2"),
    (r"\b([Ll]os|[Ss]us)\s+§(\d+(?:\.\d+)?)", r"\1 apartados \2"),
    (r"§(\d+(?:\.\d+)?)", r"apartado \1"),
]


def como_prosa(texto):
    for patron, cambio in PROSA:
        texto = re.sub(patron, cambio, texto)
    return texto


# Los sitios donde el § es rótulo y no cita.
# El contenido va con `.*?` y no con `[^<]*`: un rótulo puede llevar una
# etiqueta dentro —un semáforo, una marca— y con la versión estrecha el patrón
# no lo abarcaba y el § acababa tratado como si fuera prosa.
ROTULOS = [
    (r'(<p class="eyebrow"[^>]*>)(.*?)(</p>)', 2),          # rótulo de apartado
    (r'(<a href="#[^"]*">)(.*?)(</a>)', 2),                 # barra de secciones
    (r'(<h[1-4][^>]*>)(.*?)(</h[1-4]>)', 2),                # titulares
    (r'(<span class="mono">)(.*?)(</span>)', 2),            # fichas de decisión
    (r'(<td class="num">)(.*?)(</td>)', 2),                 # celdas de referencia
    (r'("(?:seccion|rotulo|eyebrow|marca)":\s*")([^"]*)(")', 2),
]


def convierte(texto):
    """Primero los rótulos, luego lo que quede es prosa."""
    for patron, grupo in ROTULOS:
        def cambia(m, g=grupo):
            partes = list(m.groups())
            if "§" not in partes[g - 1]:
                return m.group(0)
            partes[g - 1] = como_rotulo(partes[g - 1])
            return "".join(partes)
        texto = re.sub(patron, cambia, texto, flags=re.S)
    return como_prosa(texto)


def main():
    solo_ver = "--ver" in sys.argv
    tocados = cambios = 0
    for ruta in ARCHIVOS:
        if not ruta.exists():
            continue
        antes = ruta.read_text(encoding="utf-8")
        if "§" not in antes:
            continue
        despues = convierte(antes)
        n = antes.count("§") - despues.count("§")
        if antes == despues:
            continue
        tocados += 1
        cambios += n
        if solo_ver:
            print("  %-42s %3d" % (ruta.relative_to(RAIZ), n))
            for a, b in zip(antes.split("\n"), despues.split("\n")):
                if a != b and "§" in a:
                    print("      − %s" % a.strip()[:100])
                    print("      + %s" % b.strip()[:100])
                    break
        else:
            ruta.write_text(despues, encoding="utf-8")
            print("  %-42s %3d" % (ruta.relative_to(RAIZ), n))
    print("\n  %d archivos · %d apariciones de § convertidas" % (tocados, cambios))
    quedan = sum(r.read_text(encoding="utf-8").count("§") for r in ARCHIVOS if r.exists())
    if not solo_ver and quedan:
        sys.exit("  quedan %d sin convertir" % quedan)


if __name__ == "__main__":
    main()
