#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reconstruye el sistema documental entero, en orden, y lo verifica.

    python3 build.py              # documentos + verificación
    python3 build.py --todo       # además exportaciones, PDF y libro de cálculo

El orden importa: las figuras salen del modelo, la Parte VI sale de las
figuras y del modelo, la Tesis ensambla todo eso, y la presentación toma sus
figuras de las mismas fuentes. Al final se ejecuta el guion de coherencia, que
comprueba que ningún documento contradiga a otro ni al modelo. Si algo falla,
este guion se detiene ahí: un sistema a medio construir no se publica.
"""
import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
GEN = RAIZ / "generadores"

# (guion, rótulo). Se ejecutan en este orden y no en otro.
DOCUMENTOS = [
    (GEN / "figuras-1-3.py", "Figuras F1–F3 · descuento, conversión y valor del paciente"),
    (GEN / "figuras-4-6.py", "Figuras F4–F6 · escenarios, sensibilidad y valor acumulado"),
    (GEN / "figuras-7.py", "Figura F7 · valor de empresa por peldaño"),
    (GEN / "figuras-8-12.py", "Figuras F8–F12 · el objetivo, derivadas del modelo"),
    (GEN / "parte6.py", "Parte VI y sus supuestos, con las cifras del modelo"),
    (GEN / "actas.py", "Anexo A · hojas de acta"),
    (GEN / "campanas.py", "Anexo B · fichas de campaña"),
    (GEN / "tesis.py", "memoria.html · Tesis de Dirección"),
    (GEN / "deck.py", "deck.html · presentación de Junta"),
    (GEN / "marketing-figuras.py", "Figuras del Plan Maestro de Marketing"),
    (GEN / "marketing.py", "marketing.html · Plan Maestro de Marketing"),
    (RAIZ / "build-captura.py", "instrumentos/captura.html · hoja de captura"),
    (RAIZ / "anclas.py", "anclas de todos los titulares"),
    (RAIZ / "build-inicio.py", "inicio.html · portada del sistema"),
]

EXTRAS = [
    (RAIZ / "build-libro.py", "instrumentos/…xlsx · libro de cálculo"),
    (RAIZ / "build-export.py", "export/ · HTML autónomo y archivo único"),
    (RAIZ / "build-pdf.py", "export/pdf/ · seis PDF paginados"),
]


def corre(guion, rotulo):
    inicio = time.time()
    r = subprocess.run([sys.executable, str(guion)], capture_output=True, text=True, cwd=str(RAIZ))
    if r.returncode != 0:
        print("  ✗ %s" % rotulo)
        print((r.stdout + r.stderr).rstrip())
        raise SystemExit("\nSe detiene en %s. Un sistema a medio construir no se publica." % guion.name)
    detalle = r.stdout.strip().splitlines()
    print("  · %-58s %s" % (rotulo, detalle[-1].strip() if detalle else ""))
    return time.time() - inicio


def main():
    todo = "--todo" in sys.argv
    print("Sistema documental Giraldo · reconstrucción completa\n")
    tareas = DOCUMENTOS + (EXTRAS if todo else [])
    reloj = sum(corre(g, r) for g, r in tareas)
    if not todo:
        print("\n  (con --todo se regeneran además el libro de cálculo, las exportaciones y los PDF)")
    print("\nVerificación de coherencia\n")
    r = subprocess.run([sys.executable, str(RAIZ / "check-coherencia.py")],
                       capture_output=True, text=True, cwd=str(RAIZ))
    print(r.stdout.rstrip())
    if r.returncode != 0:
        raise SystemExit("\nEl sistema no está listo para publicarse.")
    print("\nListo en %.1f s." % reloj)


if __name__ == "__main__":
    main()
