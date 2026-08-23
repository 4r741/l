#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Recalcula un libro de cálculo con LibreOffice.

    python3 recalc.py instrumentos/Captura-Linea-Base-Giraldo-2026.xlsx

openpyxl escribe las fórmulas sin resultado: quien abra el libro con una
herramienta que no calcule —una vista previa, un lector de móvil, una
importación— verá casillas vacías donde debería haber cifras. Este guion abre
el libro con LibreOffice, fuerza el recálculo y lo vuelve a guardar con los
valores en caché.

El recálculo forzado no es el comportamiento por omisión: al abrir un xlsx
ajeno LibreOffice pregunta, y en modo desatendido «preguntar» equivale a «no
recalcular». Por eso se prepara un perfil propio con OOXMLRecalcMode=0.
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

AJUSTE = """<?xml version="1.0" encoding="UTF-8"?>
<oor:items xmlns:oor="http://openoffice.org/2001/registry"
           xmlns:xs="http://www.w3.org/2001/XMLSchema"
           xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
 <item oor:path="/org.openoffice.Office.Calc/Formula/Load">
  <prop oor:name="OOXMLRecalcMode" oor:op="fuse"><value>0</value></prop>
 </item>
 <item oor:path="/org.openoffice.Office.Calc/Formula/Load">
  <prop oor:name="ODFRecalcMode" oor:op="fuse"><value>0</value></prop>
 </item>
</oor:items>
"""


def recalcula(ruta, espera=180):
    ruta = Path(ruta).resolve()
    if not ruta.exists():
        raise SystemExit("no existe: %s" % ruta)
    if not shutil.which("soffice"):
        raise SystemExit("falta LibreOffice: apt-get install -y libreoffice-calc")

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        perfil, salida = tmp / "perfil", tmp / "salida"
        salida.mkdir()
        base = ["soffice", "-env:UserInstallation=file://%s" % perfil,
                "--headless", "--norestore", "--nolockcheck", "--nodefault"]

        # Primera pasada en seco: LibreOffice crea el perfil. Después se le
        # inyecta el ajuste; hacerlo antes no sirve, lo sobrescribe al crearlo.
        subprocess.run(base + ["--terminate_after_init"],
                       capture_output=True, timeout=espera)
        usuario = perfil / "user"
        usuario.mkdir(parents=True, exist_ok=True)
        (usuario / "registrymodifications.xcu").write_text(AJUSTE, encoding="utf-8")

        r = subprocess.run(base + ["--convert-to", "xlsx:Calc MS Excel 2007 XML",
                                   "--outdir", str(salida), str(ruta)],
                           capture_output=True, text=True, timeout=espera)
        producto = salida / ruta.name
        if not producto.exists():
            raise SystemExit("LibreOffice no produjo nada:\n%s\n%s" % (r.stdout, r.stderr))
        shutil.copy(producto, ruta)
    return ruta


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    print("  → recalculado %s" % recalcula(sys.argv[1]))
